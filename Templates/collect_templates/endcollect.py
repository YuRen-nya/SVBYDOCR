import cv2
import numpy as np
import pyautogui
from time import sleep
import os
import tkinter as tk
from tkinter import messagebox
from Window_Coordinates_Initial import get_window_rect

# 获取窗口偏移量
[x_o, y_o, x_ob, y_ob] = get_window_rect()

# 模板保存目录
TEMPLATE_DIR = 'end_img'

# 如果目录不存在，则创建
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

# 定义截图区域（请根据你的屏幕实际位置调整）
REGION = (1400 + x_o, 425 + y_o, 100, 50)  # 示例：玩家生命值显示区域

# 数字范围：0 ~ 20
DIGITS = [str(i) for i in range(0, 21)]


# 截图并保存模板
def save_screenshot_as_template(digit):
    status_label.config(text=f"正在采集数字 {digit} 的模板，请确保屏幕上显示该数字...")
    root.update()
    sleep(0.5)
    try:
        screenshot = pyautogui.screenshot(region=REGION)
        template_path = os.path.join(TEMPLATE_DIR, f'{digit}.png')
        screenshot.save(template_path)
        status_label.config(text=f"已保存 {digit}.png 到 {TEMPLATE_DIR}")
        print(f"已保存 {digit}.png 到 {TEMPLATE_DIR}")
    except Exception as e:
        messagebox.showerror("错误", f"保存模板失败: {e}")


# 创建按钮点击事件
def create_button_callback(digit):
    def callback():
        save_screenshot_as_template(digit)
    return callback


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

# 启动 GUI 主循环
if __name__ == "__main__":
    print("=== 模板采集程序（GUI 版本） ===")
    print("请依次展示数字，并点击对应按钮进行采集。")
    root.mainloop()