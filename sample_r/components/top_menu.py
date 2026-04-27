import dearpygui.dearpygui as dpg

def menu_callback(sender, app_data = 1):
    """Generic placeholder for menu actions."""
    print(f"Command Received: {dpg.get_item_label(sender)}")

def create_top_menu():
    """
    Creates the Top Menu panel.
    Calculates height as 10% of parent_height.
    """
    # menu_height = int(parent_height * 0.10)
    
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Import", callback=menu_callback)
            dpg.add_menu_item(label="Export", callback=menu_callback)
        
        with dpg.menu(label="Action"):
            dpg.add_menu_item(label="Sort", callback=menu_callback)
            dpg.add_menu_item(label="Analyze", callback=menu_callback)


if __name__ == "__main__":
    dpg.create_context()

    # Initial window setup
    WIDTH = 1280
    HEIGHT = 720
    
    dpg.create_viewport(title='Sample-R', width=WIDTH, height=HEIGHT)
    
    # Procedural call to build the UI component
    create_top_menu()
    
    # Register the resize callback to keep things proportional
    # dpg.set_viewport_resize_callback(resize_handler)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()