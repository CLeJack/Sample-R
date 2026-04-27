
from sample_r.bus import bus, MessageType
import dearpygui.dearpygui as dpg

def data_list_callback(sender, app_data):
    pass

def create_data_list(values):

    with dpg.table(header_row=False, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, label = "data_list",n):
        dpg.add_table_column()

        for v in values:
            with dpg.table_row():
                dpg.add_text(v)




if __name__ == "__main__":

    #python -m sample_r.components.file_list
    dpg.create_context()

    # Initial window setup
    WIDTH = 1280
    HEIGHT = 720
    
    dpg.create_viewport(title='Sample-R', width=WIDTH, height=HEIGHT)

    with dpg.window(label="Tutorial"):
        # Procedural call to build the UI component
        values = [1,2,3,4,5]
        create_data_list(values)
    
    # Register the resize callback to keep things proportional
    # dpg.set_viewport_resize_callback(resize_handler)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()