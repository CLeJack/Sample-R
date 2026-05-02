import dearpygui.dearpygui as dpg
from collections import deque
from enum import IntEnum, auto
import numpy as np
import traceback

from sample_r.core.audio import AudioData
from sample_r.core import files as IO
from sample_r.core import top_menu

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
    first_draw_needed = False
    current_file = 0
    spectrum_limit = 1024
    spectrum_index = spectrum_limit
    harmonic_index = 1
    last_path = '../'
    io_type = Tag.IMPORT_FILES
        

    def load_gen(file):
        d = AudioData(file,len(App.audio))
        # d.set_spectrum()
        # d.analyze()
        # d.create_harmonics()
        # d.resynthesize_cycle()
        d.full_process()
        dpg.configure_item(Tag.CURRENT_FILE_SLIDER, max_value=max(0,len(App.audio)))
        s = dpg.get_value(Tag.LOG)
        dpg.set_value(Tag.LOG, s + f'\nloaded {len(App.audio)}. {d.name}')
        dpg.set_value(Tag.SPECTRUM_SLIDER, len(d.spectrum)//2)
        dpg.set_value(Tag.HARMONIC_SLIDER, len(d.hview)//2)
        yield d
    
    def load(paths):        
        files = IO.get_files(paths)
        if(len(files) > 0):
            App.file_queue = deque(files)
            App.audio = []
            App.first_draw_needed = True
            App.current_file = 0
        print(f'Loaded {len(files)} files')


    def update():
        if len(App.file_queue) > 0:
            d = next(App.load_gen(App.file_queue.popleft()))
            App.audio.append(d)
            
        
        if(App.first_draw_needed):
            App.first_draw_needed = False
            App.redraw()
            

    def redraw():
        try:
            a = App.audio[App.current_file]
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
            dpg.set_value(Tag.SPECTRUM_VIEW, s[:App.spectrum_index])
            dpg.set_value(Tag.HARMONICS_VIEW, h[:App.harmonic_index])
            
            dpg.set_value(Tag.CYCLE_VIEW, c)
            dpg.set_value(Tag.QUANTIZE_SLIDER, q)

            dpg.configure_item(Tag.SMPL_START_SLIDER, min_value = 0, max_value = len(d) - 2)
            dpg.set_value(Tag.SMPL_START_SLIDER, start)
            
            dpg.configure_item(Tag.SMPL_END_SLIDER, min_value = 1, max_value = len(d) - 1)
            dpg.set_value(Tag.SMPL_END_SLIDER, end)

            dpg.configure_item(Tag.ROLL_SLIDER, min_value = -(max(len(h) - 1,0)), max_value = max(0,len(h) - 1))
            dpg.set_value(Tag.ROLL_SLIDER, a.roll)
            
            dpg.configure_item(Tag.SPECTRUM_SLIDER, min_value = 2, max_value = App.spectrum_limit)

            dpg.configure_item(Tag.HARMONIC_SLIDER, max_value = len(h) - 1)

            
            dpg.set_value(Tag.FILE_NAME, a.name)
            dpg.set_value(Tag.FILE_COUNT, len(App.audio))

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
        dpg.set_value(Tag.CURRENT_FILE_SLIDER, v - 1)
        App.current_file_callback()
    
    def next_file_callback():
        v = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        dpg.set_value(Tag.CURRENT_FILE_SLIDER, v + 1)
        App.current_file_callback()

    def sample_boundary_callback():
        s = dpg.get_value(Tag.SMPL_START_SLIDER)
        e = dpg.get_value(Tag.SMPL_END_SLIDER)
        a = App.audio[App.current_file]
        if s > e -2 and e < len(a.data):
            e = s+2
            a.start_index = s
            a.end_index = e
            a.full_process(internal_quantize = False)
            App.redraw()
        elif e - s >2048 or e - s > len(a.data):
             e = min(len(a.data), s + 2048)
             a.start_index = s
             a.end_index = e
        a.full_process(internal_quantize = False)
        App.redraw()
               
        
        dpg.set_value(Tag.SMPL_START_SLIDER, s)
        dpg.set_value(Tag.SMPL_END_SLIDER, e)
            
            

    def spectrum_boundary_callback():
        App.spectrum_index = dpg.get_value(Tag.SPECTRUM_SLIDER)
        App.redraw()
    
    def harmonic_boundary_callback():
        App.harmonic_index = dpg.get_value(Tag.HARMONIC_SLIDER)
        App.redraw()

    def quantize_callback():
        a = App.audio[App.current_file]
        val = dpg.get_value(Tag.QUANTIZE_SLIDER)
        a.quantization_level = val
        a.roll = 0
        a.full_process(internal_quantize=False)
        App.redraw()

    def roll_harmonics_callback():
        a = App.audio[App.current_file]
        val = dpg.get_value(Tag.ROLL_SLIDER)
        a.roll = val
        a.full_process(internal_quantize=False)
        App.redraw()


    def menu_callback(sender):
        print(f"Command Received: {dpg.get_item_label(sender)}")


    def file_callback(sender, app_data):
        val = ""
        
        if isinstance(app_data, dict):
            match(App.io_type):
                case Tag.IMPORT_FILES:
                        val = list(app_data['selections'].values())
                        App.last_path = app_data['file_path_name']
                        App.load(val)

                case Tag.IMPORT_FOLDER:
                        val = app_data['file_path_name']
                        App.last_path = app_data['file_path_name']
                        App.load(val)

                case Tag.EXPORT_CYCLES_DIALOG:
                        val = app_data['file_path_name']
                        s = 'Wrote'
                        for a in App.audio:
                            IO.export_wavetable(a.frame,val, a.name)
                            s+= f'\n{a.name}'
                        dpg.set_value(Tag.LOG, s)

                case Tag.EXPORT_WAVETABLE_DIALOG:
                        val = app_data['file_path_name']
                        IO.consolidated_export(App.audio, val,'sample-r')
                        dpg.set_value(Tag.LOG, 'Wrote sample-r.wav')
                case _:
                    print("No callback defined")
    
    def file_dispatch(sender, app_data, user_data):
        App.io_type=user_data
        match(App.io_type):
            case Tag.IMPORT_FILES:
                    dpg.configure_item(Tag.FILE_DIALOG, directory_selector = False)

            case Tag.IMPORT_FOLDER:
                    dpg.configure_item(Tag.FILE_DIALOG, directory_selector = True)
            case Tag.EXPORT_CYCLES_DIALOG:
                    dpg.configure_item(Tag.FILE_DIALOG, directory_selector = True)
            case Tag.EXPORT_WAVETABLE_DIALOG:
                    dpg.configure_item(Tag.FILE_DIALOG, directory_selector = True)
            case _:
                print("No callback defined")

        App.file_callback(sender, app_data)
        dpg.show_item(Tag.FILE_DIALOG)

        

    def cancel_callback():
        print('Cancel was clicked.')

    def sort_callback():
        print('')

    def analyze_callback():
        print('')


# Gui component setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_plot(label, values, x, y, width, height, tag, histogram = False):

        with dpg.window(pos=(x,y), label = label,
                        no_close=True, no_resize=True, no_move= True, 
                        no_collapse=True):
            dpg.add_simple_plot(default_value=values, width=width,height=height, tag =tag, histogram=histogram)

    
    def top_menu():
        with dpg.file_dialog(
        directory_selector=False, show=False, callback=App.file_callback, tag=Tag.FILE_DIALOG,
        cancel_callback=App.cancel_callback, width=700 ,height=400,
        ):
         dpg.add_file_extension(".wav")

        
        with dpg.viewport_menu_bar(tag="top_menu"):
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Import File", callback=App.file_dispatch, user_data = Tag.IMPORT_FILES)
                dpg.add_menu_item(label="Import Folder", callback=App.file_dispatch, user_data = Tag.IMPORT_FOLDER)
                dpg.add_menu_item(label="Export Cycles", callback=App.file_dispatch, user_data= Tag.EXPORT_CYCLES_DIALOG)
                dpg.add_menu_item(label="Export Wavetable", callback=App.file_dispatch, user_data = Tag.EXPORT_WAVETABLE_DIALOG)
            
            with dpg.menu(label="Action"):
                dpg.add_menu_item(label="Sort", callback=App.sort_callback)
                # dpg.add_menu_item(label="Analyze", callback=App.analyze_callback)
    


    def show():

        App.top_menu()
        # with dpg.window(width = App.WIDTH, height = App.HEIGHT, no_collapse=True, no_title_bar= True, no_move = True):
            # pass

        pad = 25

        W0 = 200
        W = W0 + W0 + W0  + pad*2
        X = (App.WIDTH - W)//2
        YS = [25, 300, 575 ]

        w = W
        h = W0
        ys = [i for i in range(1000)]
        
        App.create_plot('Sample View', ys,X,YS[0],w,h,Tag.SAMPLE_VIEW)
        # line_view.create(list(zip(xs,ys)), X, YS[0], w, h, "audio")

        x = X
        w = W0
        h = w
        ys = [i for i in range(w)]
        App.create_plot('Spectrum', ys, X, YS[1], w, h, Tag.SPECTRUM_VIEW)

        x = x + w + pad
        ys = [i for i in range(64)]
        App.create_plot('Harmonic Quantization', ys, x, YS[1], w, h, Tag.HARMONICS_VIEW, True)

        x = x + w + pad
        w = W0
        h = w
        ys = [i for i in range(w)]
        App.create_plot('Cycle', ys, x, YS[1], w, h,Tag.CYCLE_VIEW)

        with dpg.window(pos = (0,YS[0]), width=300, height=500, no_collapse=True, no_move = True, no_close=True):
            with dpg.group():
                dpg.add_slider_int(label = "Smpl. Start", min_value = 0,max_value = 0, tag= Tag.SMPL_START_SLIDER, clamped = True, 
                                   callback=App.sample_boundary_callback)
                
                dpg.add_slider_int(label = "Smpl. End", min_value = 0,max_value = 0, tag = Tag.SMPL_END_SLIDER , clamped = True, 
                                   callback = App.sample_boundary_callback)

                dpg.add_slider_int(label = "Spec. End", min_value = 0,max_value = 0, tag = Tag.SPECTRUM_SLIDER, 
                                   callback=App.spectrum_boundary_callback)
                
                dpg.add_slider_int(label = "Harmonic. End", min_value = 1,max_value = 1, tag = Tag.HARMONIC_SLIDER, 
                                   callback=App.harmonic_boundary_callback)
                
                dpg.add_slider_int(label = "Quantize", min_value = 0, max_value = 10, tag = Tag.QUANTIZE_SLIDER, callback=App.quantize_callback)

                dpg.add_slider_int(label = 'Roll Harmonics', min_value = 0, max_value = 0, tag = Tag.ROLL_SLIDER, callback = App.roll_harmonics_callback)

                dpg.add_text(default_value = ' ', tag = Tag.FILE_NAME)

                dpg.add_slider_int(label = 'Current File', min_value = 0,max_value = 0, clamped=True, tag = Tag.CURRENT_FILE_SLIDER, 
                                   callback=App.current_file_callback, user_data = App)
                
                dpg.add_text(default_value = '0 total files', tag = Tag.FILE_COUNT)
                
                dpg.add_button(label = "Prev File", callback = App.prev_file_callback, user_data = App)
                dpg.add_button(label = "Next File", callback = App.next_file_callback, user_data = App)
        
        with dpg.window(pos = (0,YS[2]), width = App.WIDTH, height = App.HEIGHT - YS[2], no_collapse= True, no_move=True, no_close=True):
            dpg.add_text(default_value="Sample-R", tag = Tag.LOG)

    
            
    
    

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