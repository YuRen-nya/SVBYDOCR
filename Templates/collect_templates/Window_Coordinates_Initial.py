# Window_Coordinates_Initial.py

# get_window_rect()
# 返回左上角的x坐标和y坐标

import win32gui

def get_window_rect(title="ShadowverseWB"):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        print("未找到窗口")
        return None
    rect = win32gui.GetWindowRect(hwnd)
    x_left, y_top, x_right, y_bottom = rect
    return [x_left,y_top,x_right,y_bottom]
get_window_rect()