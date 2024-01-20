import cv2
import dearpygui.dearpygui as dpg
import os
import threading
import time

project_name = 'ThirdEye'
window_width = 900
window_height = 450

dpg.create_context()
dpg.create_viewport(title=project_name, width=window_width, height=window_height, min_width=window_width, max_width=window_width, min_height=window_height, max_height=int(window_height * 1.2))

# Return Current Time
def current_time():
    current_time = time.localtime()
    hours = str(current_time.tm_hour).rjust(2, '0')
    minutes = str(current_time.tm_min).rjust(2, '0')
    seconds = str(current_time.tm_sec).rjust(2, '0')
    return f"[{hours}:{minutes}:{seconds}]"

# Toggle Windows For Each Tab
def toggle_windows(sender, app_data):
    if dpg.get_item_label(app_data) == 'Camera':
        dpg.configure_item(item='select_camera_window', show=True)
        dpg.configure_item(item='upload_targets_window', show=False)
        dpg.configure_item(item='delete_targets_window', show=False)

    if dpg.get_item_label(app_data) == 'Manage Targets':
        dpg.configure_item(item='select_camera_window', show=False)
        # dpg.configure_item(item='upload_targets_window', show=True)
        # dpg.configure_item(item='delete_targets_window', show=True)

    if dpg.get_item_label(app_data) == 'Targets Last Seen':
        dpg.configure_item(item='select_camera_window', show=False)
        dpg.configure_item(item='upload_targets_window', show=False)
        dpg.configure_item(item='delete_targets_window', show=False)
    
    if dpg.get_item_label(app_data) == 'Developer Tools':
        dpg.configure_item(item='select_camera_window', show=False)
        dpg.configure_item(item='upload_targets_window', show=False)
        dpg.configure_item(item='delete_targets_window', show=False)

# Camera Tab Functions
camera_list = []

def get_connected_cameras_amount():
    camera_list.clear()
    index = 0

    while True:
        if not cv2.VideoCapture(index).isOpened():
            break
        
        camera_list.append(f'video capture ({index})')
        index += 1

    print(f'{current_time()}     {camera_list}')
    dpg.configure_item(item='listbox_camera_list', items=camera_list)

def periodic_cameras_check():
    while True:
        get_connected_cameras_amount()
        time.sleep(5)

cameras_thread = threading.Thread(target=periodic_cameras_check)
cameras_thread.daemon = True
cameras_thread.start()

# Manage Targets Tab Functions
faces_directory_path = r'C:\Users\orfon\Documents\[Programming]\[ ThirdEye ]\[ Code ]\ThirdEye\src\faces'
file_list = os.listdir(faces_directory_path)
picture_formats = ['.jpg', '.jpeg', '.png', '.gif']
picture_names = [filename for filename in file_list if os.path.splitext(filename)[1].lower() in picture_formats]

def search_targets():
    for picture_name in picture_names:
        if dpg.get_value(item='input_search_targets') in picture_name:
            dpg.configure_item(item=f'checkbox_{picture_name}', show=True)
        else:
            dpg.configure_item(item=f'checkbox_{picture_name}', show=False)

def show_upload_targets_window():
    dpg.set_value(item='input_upload_targets_path', value='')
    dpg.configure_item(item='upload_targets_window', show=True)

def upload_targets():
    try:
        os.rename(dpg.get_value(item='input_upload_targets_path'), os.path.join(faces_directory_path, os.path.basename(dpg.get_value(item='input_upload_targets_path'))))
        picture_names.append(os.path.basename(dpg.get_value(item='input_upload_targets_path')))
        dpg.add_checkbox(label=f'{picture_names[-1]}', tag=f'checkbox_{picture_names[-1]}', parent='manage_targets_tab', show=False)
        dpg.configure_item(item='upload_targets_window', show=False)
    except:
        print(f'{current_time()}     Error - os.rename({dpg.get_value(item="input_upload_targets_path"), os.path.join(faces_directory_path, os.path.basename(dpg.get_value(item="input_upload_targets_path")))})')

def show_delete_targets_window():
    dpg.set_value(item='input_delete_targets_confirm', value='')
    dpg.configure_item(item='delete_targets_window', show=True)

def delete_targets():
    if 'confirm' == dpg.get_value(item='input_delete_targets_confirm').lower():
        picture_names_copy = picture_names.copy()
        for picture_name in picture_names_copy:
            print(picture_name)
            if dpg.get_value(item=f'checkbox_{picture_name}'):
                try:
                    os.remove(f'{faces_directory_path}\{picture_name}')
                    dpg.delete_item(f'checkbox_{picture_name}')
                    picture_names.remove(picture_name)
                except:
                    print(f'{current_time()}     Error - os.remove({faces_directory_path}\{picture_name})')
        dpg.configure_item(item='delete_targets_window', show=False)

def print_active_targets():
    for picture_name in picture_names:
        if dpg.get_value(item=f'checkbox_{picture_name}'):
            print(picture_name)

# Graphical User Interface
with dpg.window(tag='main_window'):
    with dpg.tab_bar(callback=toggle_windows):
        with dpg.tab(label='Camera', tag='camera_tab'):
            with dpg.window(label='Select Video Capture', tag='select_camera_window', pos=[5, 30], collapsed=True, autosize=True, no_resize=True, no_move=True, no_close=True, no_background=True):
                dpg.add_listbox(items=camera_list, tag='listbox_camera_list', width=int(window_width * 0.5), tracked=True, num_items=3)
        with dpg.tab(label='Manage Targets', tag='manage_targets_tab'):
            with dpg.group(horizontal=True):
                dpg.add_input_text(tag='input_search_targets', callback=search_targets, hint='Enter File Name', no_spaces=True, on_enter=True)
                dpg.add_button(label='Upload', tag='button_upload_targets',callback=show_upload_targets_window)
                dpg.add_button(label='Delete', tag='button_delete_targets', callback=show_delete_targets_window)
                dpg.add_button(label='Print Active Targets', callback=print_active_targets)
            with dpg.window(label='Upload Targets', tag='upload_targets_window', width=375, height=100, show=False, pos=[int(window_width * 0.5 - 195), int(window_height * 0.5 - 100)], no_resize=True, no_move=True, no_collapse=True):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag='input_upload_targets_path', width=int(375 * 0.75), callback=upload_targets, hint='c:\example.png', no_spaces=True, on_enter=True)
                    dpg.add_button(label='Upload', tag='button_upload_targets_path', callback=upload_targets)
            with dpg.window(label='Delete Targets', tag='delete_targets_window', width=375, height=100, show=False, pos=[int(window_width * 0.5 - 195), int(window_height * 0.5 - 100)], no_resize=True, no_move=True, no_collapse=True):
                dpg.add_text(default_value='Are You Sure You Want To Delete All Active Targets?')
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag='input_delete_targets_confirm', callback=delete_targets, hint='Type "Confirm" To Delete', no_spaces=True, on_enter=True)
                    dpg.add_button(label='Delete', tag='button_delete_targets_path', callback=delete_targets)
        with dpg.tab(label='Targets Last Seen', tag='targets_last_seen_tab'):
            dpg.add_button(label='Button') # Doesn't Have Callback
        with dpg.tab(label='Developer Tools', tag='developer_tools'):
            dpg.add_button(label='dpg.show_about()', callback=dpg.show_about)
            dpg.add_button(label='dpg.show_debug()', callback=dpg.show_debug)
            dpg.add_button(label='dpg.show_documentation()', callback=dpg.show_documentation)
            dpg.add_button(label='dpg.show_font_manager()', callback=dpg.show_font_manager)
            dpg.add_button(label='dpg.show_item_registry()', callback=dpg.show_item_registry)
            dpg.add_button(label='dpg.show_metrics()', callback=dpg.show_metrics)
            dpg.add_button(label='dpg.show_style_editor()', callback=dpg.show_style_editor)

# Create Targets
for picture_name in picture_names:
    try:
        dpg.add_checkbox(label=f'{picture_name}', tag=f'checkbox_{picture_name}', parent='manage_targets_tab', show=False)
    except:
        print(f'{current_time()}     Error - add_checkbox [{picture_name}]')

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('main_window', True)

dpg.start_dearpygui()
dpg.destroy_context()