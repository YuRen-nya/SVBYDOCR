# 1GS.py
# 图像预处理工具
# 功能：对采集的模板图像进行批量预处理，包括灰度化和二值化

import os
import cv2
import numpy as np
from PIL import Image

def preprocess(img_bgr, threshold=150):
    """
    图像预处理函数
    对图像进行灰度化和固定阈值二值化处理
    
    Args:
        img_bgr: 输入的BGR格式图像
        threshold: 二值化阈值，默认150
    
    Returns:
        numpy.ndarray: 处理后的二值化图像
    """
    # 转换为灰度图像
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # 固定阈值二值化（黑白反转）
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    return binary

def batch_preprocess_images(input_folder, output_folder, threshold=150):
    """
    批量预处理图像
    读取输入文件夹中的所有图像，进行预处理后保存到输出文件夹
    
    Args:
        input_folder: 输入图像文件夹路径
        output_folder: 输出图像文件夹路径
        threshold: 二值化阈值，默认150
    """
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 遍历输入文件夹中的所有图像文件
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        input_path = os.path.join(input_folder, filename)

        # 使用 PIL 读取图像（防止格式兼容问题），再转为 OpenCV BGR 格式
        pil_img = Image.open(input_path).convert('RGB')  # 强制 RGB
        img_array = np.array(pil_img)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # 应用预处理
        processed_img = preprocess(img_bgr, threshold)

        # 保存处理后的图像
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, processed_img)

        print(f"已处理: {filename}")

# ===== 示例调用 =====
# 处理换牌界面的数字模板
input_dir = 'Templates/change_img'      # 原始模板文件夹
output_dir = 'Templates/change_img1'    # 处理后模板文件夹
batch_preprocess_images(input_dir, output_dir, threshold=150)
