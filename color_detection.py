# color_detection.py

import cv2
import numpy as np
import pyautogui

def is_color_in_region(region, target_color, threshold=0.3):
    """
    检查指定区域内的颜色是否接近目标颜色。
    
    :param region: 区域坐标 (x, y, width, height)
    :param target_color: 目标颜色 (B, G, R)
    :param threshold: 颜色匹配阈值
    :return: 如果区域内颜色接近目标颜色返回 True，否则返回 False
    """
    x, y, width, height = region
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # 计算平均颜色
    avg_color_per_row = np.average(frame, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    
    # 计算颜色差异
    color_diff = np.linalg.norm(np.array(target_color) - avg_color)
    
    # 判断颜色是否接近目标颜色
    return color_diff < threshold * 255 * np.sqrt(3)




