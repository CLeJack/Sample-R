
from sample_r.bus import bus, MessageType
import dearpygui.dearpygui as dpg
import numpy as np


def create_bar_view(values, width, height):

    with dpg.window(label="sample_window", no_close=True, no_resize=True, no_move= True):
        with dpg.drawlist(width=width, height= height):
            step = width/len(values)
            for i,v in enumerate(values):
                x0 = step * i
                x1 = x0 + step
                y0 = height
                y1 = y0 - v*height
                print(v, x0, x1, y0, y1)
                dpg.draw_rectangle(pmin=(x0, y0), pmax=(x1, y1))
        #add buttons for choosing harmonics





if __name__ == "__main__":

    #python -m sample_r.components.bar_view
    dpg.create_context()

    # Initial window setup
    WIDTH = 1280
    HEIGHT = 720

    wwidth = 200
    wheight = wwidth

    rng = np.random.default_rng()
    v = 64

    values = (rng.random(v) * wheight).tolist()
    values=[x/v for x in range(v, 0, -1)]

    print(values, wwidth, wheight)
    
    dpg.create_viewport(title='Sample-R', width=WIDTH, height=HEIGHT)
    
    create_bar_view(values, wwidth, wheight)
    

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()