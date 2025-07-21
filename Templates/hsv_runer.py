import cv2
import numpy as np

# 读取两张图片
img_path1 = 'dataset_deduplicated/image_0112.png'  # 第一张图片路径
img_path2 = 'dataset_deduplicated/image_0100.png'  # 第二张图片路径
img1 = cv2.imread(img_path1)
img2 = cv2.imread(img_path2)
if img1 is None or img2 is None:
    print("图片读取失败！")
    exit()

hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

def nothing(x):
    pass

# 创建窗口和滑动条
cv2.namedWindow('HSV调参', cv2.WINDOW_NORMAL)
cv2.resizeWindow('HSV调参', 600, 600)
cv2.createTrackbar('H_min', 'HSV调参', 0, 179, nothing)
cv2.createTrackbar('H_max', 'HSV调参', 179, 179, nothing)
cv2.createTrackbar('S_min', 'HSV调参', 0, 255, nothing)
cv2.createTrackbar('S_max', 'HSV调参', 255, 255, nothing)
cv2.createTrackbar('V_min', 'HSV调参', 0, 255, nothing)
cv2.createTrackbar('V_max', 'HSV调参', 255, 255, nothing)

while True:
    # 获取滑动条的值
    h_min = cv2.getTrackbarPos('H_min', 'HSV调参')
    h_max = cv2.getTrackbarPos('H_max', 'HSV调参')
    s_min = cv2.getTrackbarPos('S_min', 'HSV调参')
    s_max = cv2.getTrackbarPos('S_max', 'HSV调参')
    v_min = cv2.getTrackbarPos('V_min', 'HSV调参')
    v_max = cv2.getTrackbarPos('V_max', 'HSV调参')

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    # 处理第一张图片
    mask1 = cv2.inRange(hsv1, lower, upper)
    result1 = cv2.bitwise_and(img1, img1, mask=mask1)
    # 处理第二张图片
    mask2 = cv2.inRange(hsv2, lower, upper)
    result2 = cv2.bitwise_and(img2, img2, mask=mask2)

    # 放大显示
    scale = 2
    img1_show = cv2.resize(img1, (img1.shape[1]*scale, img1.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
    mask1_show = cv2.resize(mask1, (mask1.shape[1]*scale, mask1.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
    result1_show = cv2.resize(result1, (result1.shape[1]*scale, result1.shape[0]*scale), interpolation=cv2.INTER_NEAREST)

    img2_show = cv2.resize(img2, (img2.shape[1]*scale, img2.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
    mask2_show = cv2.resize(mask2, (mask2.shape[1]*scale, mask2.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
    result2_show = cv2.resize(result2, (result2.shape[1]*scale, result2.shape[0]*scale), interpolation=cv2.INTER_NEAREST)

    # 显示
    cv2.imshow('原图1', img1_show)
    cv2.imshow('mask1', mask1_show)
    cv2.imshow('HSV调参1', result1_show)

    cv2.imshow('原图2', img2_show)
    cv2.imshow('mask2', mask2_show)
    cv2.imshow('HSV调参2', result2_show)

    key = cv2.waitKey(1)
    if key == 27:  # 按ESC退出
        break

cv2.destroyAllWindows()