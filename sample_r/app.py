import dearpygui.dearpygui as dpg
from collections import deque
from enum import IntEnum, auto
import numpy as np
import traceback

from sample_r.core.audio import AudioData
from sample_r.core import files as IO

class Tag(IntEnum):
    SMPL_START_SLIDER = auto()
    SMPL_END_SLIDER = auto()
    SPECTRUM_SLIDER = auto()
    HARMONIC_SLIDER = auto()
    QUANTIZE_SLIDER = auto()
    CURRENT_FILE_SLIDER = auto()
    SAMPLE_VIEW = auto()
    SPECTRUM_VIEW = auto()
    HARMONICS_VIEW = auto()
    CYCLE_VIEW = auto()
    ROLL_SLIDER = auto()
    FILE_NAME = auto()
    FILE_COUNT = auto()
    LOG = auto()
    FILE_DIALOG = auto()
    IMPORT_FILES = auto()
    IMPORT_FOLDER = auto()
    EXPORT_CYCLES_DIALOG = auto()
    EXPORT_WAVETABLE_DIALOG = auto()

class App:

    WIDTH = 1280
    HEIGHT = 720

    audio = []
    file_queue = deque()
    logs = deque(maxlen= 10)
    first_draw_needed = False
    current_file = 0
    spectrum_limit = 1024
    spectrum_index = spectrum_limit
    harmonic_index = 1
    last_path = '../'
    io_type = Tag.IMPORT_FILES
    export_dir = './'

    def current_data():
        return App.audio[App.current_file]
    
    def log(text=''): #for external calls
        if(text != ''):
            App.logs.append(text)
        dpg.set_value(Tag.LOG, '\n'.join(App.logs))
        
        

    def load_gen(file):
        d = AudioData(file,len(App.audio))
        d.full_process()
        dpg.configure_item(Tag.CURRENT_FILE_SLIDER, max_value=max(0,len(App.audio)))
        # s = dpg.get_value(Tag.LOG)
        App.log(f'Loaded {len(App.audio)}. {d.name}')
        yield d
    
    def load(paths):        
        files = IO.get_files(paths)
        files.sort()
        if(len(files) > 0):
            App.file_queue = deque(files)
            App.audio = []
            App.first_draw_needed = True
            App.current_file = 0
        App.log(f'Loaded {len(files)} files')


    def update():
        if len(App.file_queue) > 0:
            d = next(App.load_gen(App.file_queue.popleft()))
            App.audio.append(d)
            
        
        if(App.first_draw_needed):
            App.first_draw_needed = False
            App.redraw()
            

    def redraw():
        try:
            a = App.current_data()
            ind = App.current_file
            d = a.data
            start = a.start_index
            end = a.end_index


            s = a.spectrum
            s = s/np.max(s)
            h = a.hview
            c = a.frame
            q = a.quantization_level
            

            dpg.set_value(Tag.SAMPLE_VIEW,d[start:end])
            dpg.set_value(Tag.SPECTRUM_VIEW, s)
            dpg.set_value(Tag.HARMONICS_VIEW, h)
            
            dpg.set_value(Tag.CYCLE_VIEW, c)
            dpg.set_value(Tag.QUANTIZE_SLIDER, q)

            dpg.configure_item(Tag.SMPL_START_SLIDER, min_value = 0, max_value =a.sample_limit())
            dpg.set_value(Tag.SMPL_START_SLIDER, start)
            

            dpg.configure_item(Tag.ROLL_SLIDER, min_value = -(max(len(h) - 1,0)), max_value = max(0,len(h) - 1))
            dpg.set_value(Tag.ROLL_SLIDER, a.roll)
            
            dpg.set_value(Tag.FILE_NAME, a.name)

            App.log()

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            # Get the last line of the trace (where the error actually happened)
            
            for t in tb:
                filename, line, func, text = t
                print(filename, line, func, text)
            # print(filename, line, func, text)
            print(f"Could not draw file: {App.audio[ind].name}")


# callbacks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def current_file_callback():
        ref = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        if(App.current_file != ref):
            App.current_file = ref
            App.redraw()
    
    def prev_file_callback():
        v = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        dpg.set_value(Tag.CURRENT_FILE_SLIDER, max(0,v - 1))
        App.current_file_callback()
    
    def next_file_callback():
        v = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        dpg.set_value(Tag.CURRENT_FILE_SLIDER, min(v + 1, len(App.audio) - 1))
        App.current_file_callback()

    def sample_boundary_callback():
        s = dpg.get_value(Tag.SMPL_START_SLIDER)
        a = App.current_data()
        a.set_start_index(s)
        a.full_process(internal_quantize = False)

        App.redraw()
        dpg.set_value(Tag.SMPL_START_SLIDER, s)
            
            

    def quantize_callback():
        a = App.current_data()
        val = dpg.get_value(Tag.QUANTIZE_SLIDER)
        a.quantization_level = val
        a.roll = 0
        a.full_process(internal_quantize=False)
        App.redraw()

    def roll_harmonics_callback():
        a = App.current_data()
        val = dpg.get_value(Tag.ROLL_SLIDER)
        a.roll = val
        a.full_process(internal_quantize=False)
        App.redraw()

    def export_callback():
        for a in App.audio:
            frame = a.resynthesize_quant()
            IO.export_frame(frame, App.export_dir, filename=a.name)
            App.log(f'Exported {a.name}')
            App.redraw()
    
    def export_stack_callback():
        frames = []
        for a in App.audio:
            frames.append(a.frame)
        
        IO.export_wavetable(frames, App.export_dir, App.audio[0].name)
        App.log(f'Exported {App.audio[0].name}')
        App.redraw()


# Gui component setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_plot(label, values, x, y, width, height, tag, histogram = False):
            dpg.add_simple_plot(default_value=values, width=width,height=height, tag =tag, histogram=histogram)
    

    def show(input, output, included_text="Sample-R"):
        W = App.WIDTH
        W1 = W//8
        H =  App.HEIGHT
        H1 = 200

        App.export_dir = output
        
        with dpg.window(pos=(0,0), width = W, height = H, no_collapse=True, no_title_bar= True, no_move = True):
            with dpg.group():
                with dpg.child_window( width = -1, height = H1 *2 + 100 ):
                    with dpg.group():
                        ys = [0 for x in range(AudioData.NYQUIST)]

                        dpg.add_text("Sample <> Spectrum")
                        with dpg.group(horizontal=True):
                            App.create_plot('Sample View', ys,0,0, W//2,H1,Tag.SAMPLE_VIEW)
                            App.create_plot('Spectrum', ys, 0, H1*1, W//2, H1, Tag.SPECTRUM_VIEW)
                        
                        dpg.add_text("Harmonics <> Cycles")
                        with dpg.group(horizontal=True):
                            App.create_plot('Cycle', ys, 0, H1 * 3, W//2, H1,Tag.CYCLE_VIEW)
                            App.create_plot('Harmonic Quantization', ys, 0, H1 * 2, W//2, H1, Tag.HARMONICS_VIEW, True)
                            
                
                with dpg.child_window( width=-1, ): #issue
                    with dpg.group():
                        with dpg.table(
                            header_row=True, 
                            resizable=True, 
                            borders_innerV=True, 
                            width=-1
                            ):
                            # 1. Define Columns with headers
                            dpg.add_table_column(label="File")  # File Name
                            dpg.add_table_column(label="Smpl. Start")    # Smpl. Start
                            dpg.add_table_column(label="Quant level")  # Quantize
                            dpg.add_table_column(label="Shift Harmonics")     # Roll Harmonics
                            dpg.add_table_column(label="Current File")   # Current File
                            dpg.add_table_column(label="Nav -")     # Prev Button
                            dpg.add_table_column(label="Nav +")     # Next Button

                            with dpg.table_row():
                                dpg.add_input_text(default_value = 'File Name', tag = Tag.FILE_NAME, width = W1)

                                dpg.add_slider_int( min_value = 0,max_value = 0, tag= Tag.SMPL_START_SLIDER, clamped = True, 
                                                width = W1, callback=App.sample_boundary_callback)
                            

                                dpg.add_slider_int( min_value = 0, max_value = 9, tag = Tag.QUANTIZE_SLIDER,
                                                    width = W1, callback=App.quantize_callback)
                            

                                dpg.add_slider_int( min_value = 0, max_value = 0, tag = Tag.ROLL_SLIDER,
                                                    width = W1, callback = App.roll_harmonics_callback)

                                dpg.add_slider_int( min_value = 0,max_value = 0, clamped=True, tag = Tag.CURRENT_FILE_SLIDER, 
                                                    width = W1, callback=App.current_file_callback)
                            

                                dpg.add_button(label = "-", callback = App.prev_file_callback, width = W1)
                            

                                dpg.add_button(label = "+", callback = App.next_file_callback, width = W1)
                        with dpg.group(horizontal=True):
                            dpg.add_button(label = "Export", callback = App.export_callback, width = W1)
                            dpg.add_button(label = "Export Stack", callback = App.export_stack_callback, width = W1)
                            dpg.add_input_text(default_value=App.export_dir)

                        dpg.add_text(default_value= f'Sample-R: {input}')
                        with dpg.child_window(width = -1, height = -1):
                            dpg.add_text(default_value=included_text, tag = Tag.LOG)

        App.log(included_text)
        App.load(input)

    
            
    
    

if __name__ == "__main__":
    app = App()

    dpg.create_context()

    # Initial window setup
    WIDTH = 1280
    HEIGHT = 720
    
    dpg.create_viewport(title='Sample-R', width=WIDTH, height=HEIGHT)
    

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()
    app()