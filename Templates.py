# Templates.py

import cv2
import numpy as np
import os
from sklearn.cluster import DBSCAN
import pyautogui
from concurrent.futures import ThreadPoolExecutor
from Window_Coordinates_Initial import get_window_rect


[x_o,y_o,x_ob,y_ob]=get_window_rect()

# ========== 模板缓存 ==========
template_cache = {}  # {template_path: (kp, des)}


# ========== 初始化 SIFT 和 FLANN ==========
sift = cv2.SIFT_create()

FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=30)  # 可调整：checks 越小越快，但可能影响精度

flann = cv2.FlannBasedMatcher(index_params, search_params)


# ========== 核心模板匹配函数 ==========
def match_template_and_get_boxes(template_path, screenshot_gray, c1=0.5, text=False):
    if template_path in template_cache:
        kp1, des1 = template_cache[template_path]
        if text:
            print(f"[调试] 模板已缓存: {template_path}, 关键点数: {len(kp1)}")
    else:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"[ERROR] 无法读取模板图像: {template_path}")
            return []
        kp1, des1 = sift.detectAndCompute(template, None)
        if des1 is None:
            print(f"[ERROR] 无法提取模板特征: {template_path}")
            return []
        template_cache[template_path] = (kp1, des1)
        if text:
            print(f"[调试] 模板特征提取: {template_path}, 关键点数: {len(kp1)}")

    kp2, des2 = sift.detectAndCompute(screenshot_gray, None)
    if text:
        print(f"[调试] 目标图特征提取: 关键点数: {len(kp2) if kp2 is not None else 0}")
        cv2.imshow("match_debug_target", screenshot_gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if des2 is None:
        return []

    matches = flann.knnMatch(des1, des2, k=2)
    good_matches = [m for m, n in matches if m.distance < c1 * n.distance]
    if text:
        print(f"[调试] 匹配点数: {len(good_matches)} (阈值c1={c1})")

    if len(good_matches) < 20:
        if text:
            print(f"[调试] 匹配点数不足: {len(good_matches)} < 20")
        return []

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 2)

    # 加回 DBSCAN 聚类
    clustering = DBSCAN(eps=50, min_samples=12).fit(dst_pts)
    labels = clustering.labels_
    if text:
        print(f"[调试] DBSCAN聚类标签: {set(labels)}")

    unique_labels = set(labels)
    boxes = []

    for label in unique_labels:
        cluster_pts = dst_pts[labels == label]
        if len(cluster_pts) < 10:  # 最少匹配点数
            if text:
                print(f"[调试] 聚类{label}点数不足: {len(cluster_pts)} < 10，跳过")
            continue

        # 计算该簇的平均 Homography
        cluster_indices = np.where(labels == label)[0]
        src_cluster = src_pts[cluster_indices]

        H, mask = cv2.findHomography(src_cluster, cluster_pts, cv2.RANSAC, 5.0)
        if H is None:
            if text:
                print(f"[调试] 聚类{label} Homography计算失败")
            continue

        h, w = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE).shape[:2]
        corners = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        transformed_corners = cv2.perspectiveTransform(corners, H)
        box_coords = np.int32(transformed_corners).reshape(4, 2).tolist()
        boxes.append(box_coords)
        if text:
            print(f"[调试] 聚类{label} 匹配到box: {box_coords}")

    return boxes


# ========== 多模板并行处理 ==========
def process_template(filename, templates_folder, screenshot_gray,c1):
    template_path = os.path.join(templates_folder, filename)
    boxes = match_template_and_get_boxes(template_path, screenshot_gray,c1)
    return filename, boxes


def find_all_templates_in_screenshot(templates_folder, region=None,c1=0.5):
    results = {}
    filenames = [f for f in os.listdir(templates_folder) if f.endswith(('.png', '.jpg'))]

    # 截图
    img = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    with ThreadPoolExecutor(max_workers=8) as executor:  # 可根据 CPU 核心数调整
        futures = [executor.submit(process_template, f, templates_folder, screenshot,c1) for f in filenames]
        for future in futures:
            try:
                filename, boxes = future.result()
                if boxes:
                    results[filename] = boxes
            except Exception as e:
                print(f"[ERROR] 模板处理异常: {e}")

    return results


# ========== 辅助函数 ==========
def get_min_x_from_box(box_coords):
    return min(p[0] for p in box_coords)


def extract_instance_info(all_boxes):
    instance_list = []
    for filename, coords_list in all_boxes.items():
        base_name = os.path.splitext(filename)[0]
        for coords in coords_list:
            min_x = get_min_x_from_box(coords)
            x_coords = [p[0] for p in coords]
            y_coords = [p[1] for p in coords]
            center_x = sum(x_coords) // len(x_coords)
            center_y = sum(y_coords) // len(y_coords)
            instance_list.append({
                "name": base_name,
                "box": coords,
                "min_x": min_x,
                "center": (center_x, center_y)
            })
    return instance_list


# ========== 对外接口函数 ==========
def detect_hand_card(state, templates_folder="Templates/MB_h", region=(x_o, y_o+700, x_ob, y_ob)):
    state.hand_card_ids.clear()

    # 模板匹配
    all_boxes = find_all_templates_in_screenshot(templates_folder, region=region,c1=0.5)
    instance_list = extract_instance_info(all_boxes)
    instance_list.sort(key=lambda x: x["min_x"])

    # 更新状态
    for item in instance_list:
        state.hand_card_ids.append(item['name'])


def detect_own_minion(state, templates_folder="Templates/MB_b", region=(x_o, y_o+400, x_ob, y_o+630)):
    state.own_minion_ids.clear()

    # 模板匹配
    all_boxes = find_all_templates_in_screenshot(templates_folder, region=region,c1=0.3)
    instance_list = extract_instance_info(all_boxes)
    instance_list.sort(key=lambda x: x["min_x"])

    # 更新状态
    for item in instance_list:
        state.own_minion_ids.append(item['name'])

# 加载模板（从指定目录加载所有 .png 文件）
def load_templates(template_dir, threshold=150):
    templates = []
    labels = []

    for file in sorted(os.listdir(template_dir)):
        if file.endswith('.png'):
            digit = file.split('.')[0]
            path = os.path.join(template_dir, file)
            img = cv2.imread(path, 0)  # 灰度图读取
            
            # 关键修改：使用普通二值化而非反色
            _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
            
            templates.append(binary)
            labels.append(digit)

    print(f"已加载 {len(templates)} 个模板 from {template_dir}")
    return templates, labels

# 模板匹配主函数
def template_match(region, templates, labels, threshold_match=0.8):
    screenshot = pyautogui.screenshot(region=region)
    img_array = np.array(screenshot)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # 固定预处理流程（与模板一致）
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    best_score = -1
    best_digit = None

    for i, template in enumerate(templates):
        if template.shape[0] > binary.shape[0] or template.shape[1] > binary.shape[1]:
            continue

        result = cv2.matchTemplate(binary, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_digit = labels[i]

    if best_score >= threshold_match:
        try:
            print(f"识别成功: {best_digit} （置信度: {best_score:.2f}）")
            return int(best_digit)
        except:
            # print("匹配结果非有效数字")
            return 0
    else:
        # print(f"未找到匹配项（最高置信度: {best_score:.2f}）")
        return 0