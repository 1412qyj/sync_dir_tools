'''
Descripttion: 
Author: QYJ
version: 
Date: 2022-06-01 16:13:45
LastEditors: QYJ
LastEditTime: 2022-06-02 16:35:44
'''
import os
import PySimpleGUI as sg
import shutil
import pickle






                
def try_daemon(func):
    def daemon(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as E:
            print(str(E))

    return daemon


@try_daemon
def copy_files(src_path, dist_path):
    if not os.path.exists(dist_path):
        os.makedirs(dist_path)

    if os.path.exists(src_path):
        for root, _, files in os.walk(src_path):
            for file in files:
                src_file = os.path.join(root, file)
                dist_file = root.replace(src_path, dist_path)
                if not os.path.exists(dist_file):
                    os.makedirs(dist_file)
                shutil.copy(src_file, dist_file)
        
        print(src_file, "\nhas been copied to\n", dist_path)
    else:
        print("path:", src_path, "Not Exist")


@try_daemon
def save_default_config(src_path: str, dist_paths: list[str]):
    with open(r'./sync_tool_config.qyj', 'wb') as fp:
        data = {
            'src_path': src_path,
            'dist_paths': dist_paths
        }
        pickle.dump(data, fp)

default_config = {}
@try_daemon
def load_default_config() -> dict:
    global default_config
    if os.path.exists('./sync_tool_config.qyj'):
        with open(r'./sync_tool_config.qyj', 'rb') as fp:
            default_config = pickle.load(fp)
    else:
        print('Cannot Find sync_tool_config.qyj')


if __name__ == '__main__':
    load_default_config()
    
    dist_paths = default_config['dist_paths'] if 'dist_paths' in default_config.keys() else []
    src_path = default_config['src_path'] if 'src_path' in default_config.keys() else ''

    src_layout = [
        [sg.InputText(default_text=src_path, size=(30, 1), key='SRC_PATH'), sg.FolderBrowse('目标文件夹', size=(10, 1))],
        [sg.Output(size=(40, 20))]
    ]
    dist_layout = [
        [sg.Listbox(values=dist_paths ,size=(40, 10), key='target_folders', select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
        [sg.B("添加", size=(10, 1)), sg.B("删除", size=(10, 1))],
        [sg.B("同步", size=(10, 1)), sg.B("全部同步", size=(10, 1))],
        [sg.T('----------------------------------------------------')],
        [sg.B("保存配置", size=(10, 1))],
    ]
    layout = [
        [sg.Frame(title='Src', layout=src_layout, size=(500, 600)), 
        sg.Frame(title='Dist', layout=dist_layout, size=(500, 600))],
    ]

    window = sg.Window(layout=layout, title='SYNC TOOLS', font=("JetBrains Mono", 15), size=(1000,600))

    while True:
        event, val = window.Read() 
        if event in (sg.WINDOW_CLOSED, None):
            break

        if event == "添加":
            text = sg.popup_get_folder('选择同步的目标文件夹')
            if text != '':
                cur_folders = window['target_folders'].Values
                if text in cur_folders:
                    pass
                else:
                    cur_folders.append(text)
                    window['target_folders'].update(values=cur_folders)

        if event == "删除":
            try:
                cur_folders = window['target_folders'].get_list_values()
                for index in window['target_folders'].get_indexes()[::-1]:
                    del cur_folders[index]
                window['target_folders'].update(values=cur_folders)
            except Exception as E:
                print(str(E))

        if event == "同步":
            cur_folders = window['target_folders'].get_list_values()
            for index in window['target_folders'].get_indexes():
                copy_files(val['SRC_PATH'], cur_folders[index])

        if event == "全部同步":
            for dist_path in window['target_folders'].get_list_values():
                copy_files(val['SRC_PATH'], dist_path)

        if event == "保存配置":
            save_default_config(src_path=val['SRC_PATH'], dist_paths=window['target_folders'].get_list_values())

    window.close()