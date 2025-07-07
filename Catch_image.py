# Catch_image.py
# 截图模块
# 功能：截取游戏窗口指定区域的图像

import pyautogui
from PIL import Image
from Window_Coordinates_Initial import get_window_rect

# ===== 窗口坐标初始化 =====
# 获取游戏窗口左上角坐标
[x_o, y_o, _, _] = get_window_rect()
print(f"游戏窗口左上角坐标: ({x_o}, {y_o})")

# ===== 默认截图区域 =====
# 默认截取游戏主要区域的坐标和大小
x, y, width, height = 250, 210, 1050, 420

def get_screenshot_region(x, y, width, height):
    """
    截取指定区域的图像
    
    Args:
        x: 起始x坐标
        y: 起始y坐标
        width: 截图宽度
        height: 截图高度
    
    Returns:
        PIL.Image: 截取的图像对象
    """
    # 使用 pyautogui 截取指定区域
    image = pyautogui.screenshot(region=(x, y, width, height))
    return image

