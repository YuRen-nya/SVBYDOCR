# Window_Coordinates_Initial.py
# 窗口坐标获取模块
# 功能：获取游戏窗口的位置和大小信息

import win32gui

def get_window_rect(title="ShadowverseWB"):
    """
    获取指定窗口的位置和大小信息
    
    Args:
        title: 窗口标题，默认为"ShadowverseWB"
    
    Returns:
        list: [左上角x坐标, 左上角y坐标, 右下角x坐标, 右下角y坐标] 或 None
    """
    # 查找指定标题的窗口句柄
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        print("未找到窗口")
        return None
    
    # 获取窗口矩形区域
    rect = win32gui.GetWindowRect(hwnd)
    x_left, y_top, x_right, y_bottom = rect
    
    # 返回窗口坐标信息
    return [x_left, y_top, x_right, y_bottom]

# 测试函数调用
get_window_rect()