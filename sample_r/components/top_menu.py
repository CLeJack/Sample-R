import dearpygui.dearpygui as dpg
from sample_r.bus import bus, MessageType


file_tag = "file_dialog_id"
folder_tag = "folder_dialog_id"

def menu_callback(sender, app_data):
    print(f"Command Received: {dpg.get_item_label(sender)}")


def file_callback(sender, app_data):
    msgtype = MessageType.IMPORT_FAILURE
    val = ""
    if sender == file_tag:
            msgtype = MessageType.IMPORT_FOLDER
            val = list(app_data['selections'].values())
            bus.push(msgtype, 0, val)

    elif sender == folder_tag:
            msgtype = MessageType.IMPORT_FILES
            val = app_data['file_path_name']
            bus.push(msgtype, 0, val)
    else:
         bus.push(msgtype,0,"")

    print(msgtype, val)

    

def cancel_callback(sender, app_data):
    print('Cancel was clicked.')
    print("Sender: ", sender)

def sort_callback(sender, app_data):
     print(sender)
     bus.push(MessageType.SORT)

def analyze_callback(sender, app_data):
     print(sender)
     bus.push(MessageType.ANALYZE)


def create_top_menu():
    """
    Creates the Top Menu panel.
    Calculates height as 10% of parent_height.
    """
    # menu_height = int(parent_height * 0.10)

    with dpg.file_dialog(
        directory_selector=False, show=False, callback=file_callback, tag=file_tag,
        cancel_callback=cancel_callback, width=700 ,height=400
        ):
         dpg.add_file_extension(".wav")

    with dpg.file_dialog(
        directory_selector=True, show=False, callback=file_callback, tag=folder_tag,
        cancel_callback=cancel_callback, width=700 ,height=400
        ):
         dpg.add_file_extension(".wav")
    
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Import File", callback=lambda: dpg.show_item(file_tag))
            dpg.add_menu_item(label="Import Folder", callback=lambda: dpg.show_item(folder_tag))
            dpg.add_menu_item(label="Export Cycles", callback=menu_callback)
            dpg.add_menu_item(label="Export Wavetable", callback=menu_callback)
        
        with dpg.menu(label="Action"):
            dpg.add_menu_item(label="Sort", callback=sort_callback)
            dpg.add_menu_item(label="Analyze", callback=analyze_callback)


if __name__ == "__main__":

    #run with: python -m sample_r.components.top_menu
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