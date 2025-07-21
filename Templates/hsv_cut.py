import cv2
import numpy as np

# 读取图片
img = cv2.imread('dataset_deduplicated/image_0100.png')
h, w = img.shape[:2]

# 计算中心75%区域
crop_w, crop_h = int(w * 0.75), int(h * 0.75)
x1 = (w - crop_w) // 2
y1 = (h - crop_h) // 2
x2 = x1 + crop_w
y2 = y1 + crop_h
center_img = img[y1:y2, x1:x2]

# 转HSV
hsv = cv2.cvtColor(center_img, cv2.COLOR_BGR2HSV)

# 设置阈值
lower = np.array([29, 120,255])
upper = np.array([31, 180,255 ])

# 掩码
mask = cv2.inRange(hsv, lower, upper)
result = cv2.bitwise_and(center_img, center_img, mask=mask)

cv2.imshow('center_crop', center_img)
cv2.imshow('hsv_mask', mask)
cv2.imshow('result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 如需保存
cv2.imwrite('center_crop.png', center_img)
cv2.imwrite('hsv_mask.png', mask)
cv2.imwrite('hsv_result.png', result)