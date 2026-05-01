import dearpygui.dearpygui as dpg
from sample_r.app import App


if __name__ == "__main__":
    app = App()

    dpg.create_context()

    dpg.create_viewport(title='Sample-R', width=App.WIDTH, height=App.HEIGHT)
    
    app.show()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    # dpg.start_dearpygui()

    while dpg.is_dearpygui_running():
        # Insert your custom logic here (must be fast!)
        app.update()
        
        # Manually tell DPG to render the frame
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
