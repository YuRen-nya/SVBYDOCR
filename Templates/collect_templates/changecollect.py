# changecollect.py
# 模板采集工具 - 数字采集器
# 功能：通过GUI界面采集游戏中的数字模板，用于数值识别

import cv2
import numpy as np
import pyautogui
from time import sleep
import os
import tkinter as tk
from tkinter import messagebox
from Window_Coordinates_Initial import get_window_rect

# ===== 窗口坐标初始化 =====
# 获取游戏窗口的位置信息
[x_o, y_o, x_ob, y_ob] = get_window_rect()

# ===== 模板保存目录 =====
# 数字模板保存的文件夹
TEMPLATE_DIR = 'change_img'

# 如果目录不存在，则创建
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

# ===== 截图区域定义 =====
# 定义截图区域（请根据你的屏幕实际位置调整）
# 格式：(x坐标, y坐标, 宽度, 高度)
REGION = (450 + x_o, 450 + y_o, 500, 50)

# ===== 数字范围 =====
# 需要采集的数字模板：0 ~ 20
DIGITS = [str(i) for i in range(0, 21)]

def save_screenshot_as_template(digit):
    """
    截图并保存模板
    截取指定区域的图像并保存为数字模板
    
    Args:
        digit: 要采集的数字
    """
    status_label.config(text=f"正在采集数字 {digit} 的模板，请确保屏幕上显示该数字...")
    root.update()
    sleep(0.5)  # 等待用户准备
    
    try:
        # 截取指定区域的图像
        screenshot = pyautogui.screenshot(region=REGION)
        template_path = os.path.join(TEMPLATE_DIR, f'{digit}.png')
        screenshot.save(template_path)
        
        # 更新状态显示
        status_label.config(text=f"已保存 {digit}.png 到 {TEMPLATE_DIR}")
        print(f"已保存 {digit}.png 到 {TEMPLATE_DIR}")
    except Exception as e:
        messagebox.showerror("错误", f"保存模板失败: {e}")

def create_button_callback(digit):
    """
    创建按钮点击事件
    为每个数字按钮创建对应的回调函数
    
    Args:
        digit: 数字
    
    Returns:
        function: 按钮回调函数
    """
    def callback():
        save_screenshot_as_template(digit)
    return callback

# ===== GUI界面创建 =====
# 创建主窗口
root = tk.Tk()
root.title("模板采集器 - 数字采集")
root.geometry("600x400")

# 标题说明
title_label = tk.Label(root, text="=== 模板采集器 ===\n请点击下方按钮采集数字模板\n采集前请手动在屏幕上显示对应数字", font=("Arial", 14))
title_label.pack(pady=10)

# 动态状态栏
status_label = tk.Label(root, text="准备就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# 按钮区域
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# 创建 0~20 的按钮
for digit in DIGITS:
    btn = tk.Button(button_frame, text=digit, width=5, height=2,
                    command=create_button_callback(digit))
    btn.pack(side=tk.LEFT, padx=5)

# 退出按钮
exit_btn = tk.Button(root, text="退出", width=10, height=2, command=root.quit)
exit_btn.pack(pady=20)

# ===== 主程序入口 =====
if __name__ == "__main__":
    print("=== 模板采集程序（GUI 版本） ===")
    print("请依次展示数字，并点击对应按钮进行采集。")
    root.mainloop()