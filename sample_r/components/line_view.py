
from sample_r.bus import bus, MessageType
import dearpygui.dearpygui as dpg
import numpy as np

def create_line_view(values, width, height):

    with dpg.window(label="sample_window", no_close=True, no_resize=True, no_move= True):
        with dpg.drawlist(width=width, height= height):
            dpg.draw_polyline(values)





if __name__ == "__main__":

    #python -m sample_r.components.line_view
    dpg.create_context()

    # Initial window setup
    WIDTH = 1280
    HEIGHT = 720

    wwidth = 200
    wheight = wwidth

    rng = np.random.default_rng()
    v = 100

    ys = (rng.random(v) * wheight).tolist()
    xs = (np.linspace(0,1, v, endpoint=False) * wwidth).tolist()
    values = list(zip(xs,ys))

    print(values, wwidth, wheight)
    
    dpg.create_viewport(title='Sample-R', width=WIDTH, height=HEIGHT)
    
    create_line_view(values, wwidth, wheight)
    
    # Register the resize callback to keep things proportional
    # dpg.set_viewport_resize_callback(resize_handler)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()