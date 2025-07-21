import cv2
import numpy as np
import os

# 配置参数
input_dir = 'dataset_deduplicated'  # 待测试图片文件夹
output_dir = 'hsv_mask_results'     # mask结果保存文件夹

# HSV阈值（可根据调参结果修改）
h_min, h_max = 60,90
s_min, s_max = 60,210
v_min, v_max = 140,255

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.lower().endswith('.png'):
        img_path = os.path.join(input_dir, filename)
        img = cv2.imread(img_path)
        if img is None:
            print(f"无法读取: {filename}")
            continue
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)

        # 创建外圈mask（矩形环，75%比例）
        h, w = img.shape[:2]
        outer_mask = np.zeros((h, w), np.uint8)
        # 外矩形：整张图
        cv2.rectangle(outer_mask, (0, 0), (w, h), (255,), -1)
        # 内矩形：中心75%
        rect_scale = 0.7  # 可调整
        x1 = int(w * (1 - rect_scale) / 2)
        y1 = int(h * (1 - rect_scale) / 2)
        x2 = int(w * (1 + rect_scale) / 2)
        y2 = int(h * (1 + rect_scale) / 2)
        cv2.rectangle(outer_mask, (x1, y1), (x2, y2), (0,), -1)

        # 只保留外圈的黄色区域
        mask = cv2.bitwise_and(mask, outer_mask)

        # 只统计外圈mask区域的像素
        hsv_masked = hsv[mask == 255]
        if len(hsv_masked) > 0:
            mean_hue = np.mean(hsv_masked[:, 0])
            mean_sat = np.mean(hsv_masked[:, 1])
            mean_val = np.mean(hsv_masked[:, 2])
            
            # 计算外圈区域的形状特征
            mask_area = len(hsv_masked)
            outer_area = np.sum(outer_mask == 255)  # 外圈总面积
            mask_ratio = mask_area / outer_area  # 黄色区域占外圈的比例
            
            # 计算边缘清晰度（使用Sobel算子）
            sobel_x = cv2.Sobel(mask, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(mask, cv2.CV_64F, 0, 1, ksize=3)
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            edge_strength = np.mean(edge_magnitude)
            
            # 判断是否为黄色边框（根据外圈黄色区域面积）
            if mask_ratio > 0.1:  # 外圈黄色区域占比大于30%
                classification = "yellow_border"
            else:
                classification = "others"
        else:
            classification = "others"

        # 保存mask结果，文件名包含分类信息
        mask_vis = cv2.bitwise_and(img, img, mask=mask)
        name_without_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        new_filename = f"{name_without_ext}_{classification}{ext}"
        save_path = os.path.join(output_dir, new_filename)
        cv2.imwrite(save_path, mask_vis)

print("批量HSV过滤与统计完成！")
