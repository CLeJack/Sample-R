import dearpygui.dearpygui as dpg
from collections import deque
from enum import IntEnum, auto
import numpy as np

from sample_r.core.audio import AudioData
from sample_r.core import files as IO
from sample_r.components import top_menu

class Tag(IntEnum):
    SMPL_START_SLIDER = auto()
    SMPL_END_SLIDER = auto()
    SPECTRUM_SLIDER = auto()
    QUANTIZE_SLIDER = auto()
    CURRENT_FILE_SLIDER = auto()
    SAMPLE_VIEW = auto()
    SPECTRUM_VIEW = auto()
    HARMONICS_VIEW = auto()
    CYCLE_VIEW = auto()
    DC = auto()
    PAD = auto()

class App:

    WIDTH = 1280
    HEIGHT = 720

    def __init__(self):
        self.audio = []
        self.file_queue = deque()
        self.first_draw_needed = False
        self.current_file = 0
        

    def load_gen(self, file):
        d = AudioData(file,len(self.audio))
        d.set_spectrum()
        d.analyze()
        d.create_harmonics()
        d.resynthesize_cycle()
        dpg.configure_item(Tag.CURRENT_FILE_SLIDER, max_value=max(0,len(self.audio)))
        yield d
    
    def load(self, paths):
        files = IO.get_files(paths)
        self.file_queue = deque(files)
        self.audio = []
        self.first_draw_needed = True
        print(f'Loaded {len(self.file_queue)} files')


    def update(self):
        if len(self.file_queue) > 0:
            d = next(self.load_gen(self.file_queue.popleft()))
            print(f"loading {d.name}")
            self.audio.append(d)
            
        
        if(self.first_draw_needed):
            self.first_draw_needed = False
            self.redraw(0)
            

    def redraw(self, ind):
        try:
            d = self.audio[ind].data
            s = self.audio[ind].spectrum
            s = s/np.max(s)
            h = self.audio[ind].harmonics
            c = self.audio[ind].frame
            q = self.audio[ind].quantization_level
            sample_lim = min(1000,len(d))
            spec_lim = len(s)//2

            dpg.set_value(Tag.SAMPLE_VIEW,d[:sample_lim])
            dpg.set_value(Tag.SPECTRUM_VIEW, s[:spec_lim])
            dpg.set_value(Tag.HARMONICS_VIEW, h)
            dpg.set_value(Tag.CYCLE_VIEW, c)
            dpg.set_value(Tag.QUANTIZE_SLIDER, q)

            dpg.set_value(Tag.SMPL_END_SLIDER, sample_lim)
            dpg.configure_item(Tag.SMPL_END_SLIDER, min_value = 1, max_value = len(d))

            dpg.set_value(Tag.SPECTRUM_SLIDER, spec_lim)
            dpg.configure_item(Tag.SPECTRUM_SLIDER, max_value = spec_lim,max_scale = 1, min_scale = 0 )
        except Exception as e:
            print(e)
            print(f"Could no draw file: {self.audio[ind].name}")
    
    def current_file_update(sender, app_data, user_data):
        ref = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        if(user_data.current_file != ref):
            user_data.current_file = ref
            user_data.redraw(ref)
    
    def prev_file_update(sender, app_data, user_data):
        v = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        dpg.set_value(Tag.CURRENT_FILE_SLIDER, v - 1)
        App.current_file_update(sender, app_data, user_data)
    
    def next_file_update(sender, app_data, user_data):
        v = dpg.get_value(Tag.CURRENT_FILE_SLIDER)
        dpg.set_value(Tag.CURRENT_FILE_SLIDER, v + 1)
        App.current_file_update(sender, app_data, user_data)


    def create_plot(self, label, values, x, y, width, height, tag, histogram = False):

        with dpg.window(pos=(x,y), label = label,
                        no_close=True, no_resize=True, no_move= True, 
                        no_collapse=True):
            dpg.add_simple_plot(default_value=values, width=width,height=height, tag =tag, histogram=histogram)

    
    
    


    def show(self):

        top_menu.create(self)
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
        
        self.create_plot('Sample View', ys,X,YS[0],w,h,Tag.SAMPLE_VIEW)
        # line_view.create(list(zip(xs,ys)), X, YS[0], w, h, "audio")

        x = X
        w = W0
        h = w
        ys = [i for i in range(w)]
        self.create_plot('Spectrum', ys, X, YS[1], w, h, Tag.SPECTRUM_VIEW)

        x = x + w + pad
        ys = [i for i in range(64)]
        self.create_plot('Harmonic Quantization', ys, x, YS[1], w, h, Tag.HARMONICS_VIEW, True)

        x = x + w + pad
        w = W0
        h = w
        ys = [i for i in range(w)]
        self.create_plot('Cycle', ys, x, YS[1], w, h,Tag.CYCLE_VIEW)

        with dpg.window(pos = (0,YS[0]), width=300, height=500, no_collapse=True, no_move = True, no_close=True):
            with dpg.group():
                dpg.add_slider_int(label = "Smpl. Start", min_value = 0,max_value = 0, tag= Tag.SMPL_START_SLIDER)
                dpg.add_slider_int(label = "Smpl. End", min_value = 0,max_value = 0, tag = Tag.SMPL_END_SLIDER )

                dpg.add_slider_int(label = "Spec. End", min_value = 0,max_value = 0, tag = Tag.SPECTRUM_SLIDER)
                dpg.add_slider_int(label = "Quantize", min_value = 0, max_value = 10, tag = Tag.QUANTIZE_SLIDER)

                dpg.add_checkbox(label = "left pad", default_value=False, tag=Tag.PAD)

                dpg.add_checkbox(label = "remove DC", default_value=True, tag= Tag.DC)

                dpg.add_slider_int(label = 'Current File', min_value = 0,max_value = 0, clamped=True, tag = Tag.CURRENT_FILE_SLIDER, 
                                   callback=App.current_file_update, user_data = self)
                
                dpg.add_button(label = "Prev File", callback = App.prev_file_update, user_data = self)
                dpg.add_button(label = "Next File", callback = App.next_file_update, user_data = self)
                dpg.add_button(label="Reanalyze")
        
        with dpg.window(pos = (0,YS[2]), width = App.WIDTH, height = App.HEIGHT - YS[2], no_collapse= True, no_move=True, no_close=True):
            dpg.add_text(default_value="Sample-R")

    
            
    
    

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