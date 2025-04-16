import subprocess

def run_exe_with_window(exe_path, window_title):
    try:
        cmd = f'cmd /c title {window_title} && "{exe_path}"'
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        # print(f"Error occurred: {e}")
        pass

# 使用方法
exe_path = "../Resource/other/publisher.exe"
title = '98堂地址发布器'
run_exe_with_window(exe_path, title)
