import os
import imagehash
from PIL import Image
from collections import defaultdict
import shutil

IMG_DIR = "dataset/images"
OUTPUT_DIR = "dataset_deduplicated"
HASH_THRESHOLD = 12  # 可调高一点以容忍坐标差异
GROUP_LOG_PATH = os.path.join(OUTPUT_DIR, "similar_groups.txt")

def get_phash(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        return imagehash.phash(image)
    except Exception as e:
        print(f"跳过 {image_path}: {e}")
        return None

def group_similar_images(img_dir, threshold=12):
    image_list = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    phash_list = [(f, get_phash(os.path.join(img_dir, f))) for f in image_list]
    grouped = []
    used = set()

    for i, (f1, h1) in enumerate(phash_list):
        if f1 in used or h1 is None:
            continue
        group = [f1]
        used.add(f1)
        for j in range(i + 1, len(phash_list)):
            f2, h2 = phash_list[j]
            if f2 in used or h2 is None:
                continue
            if h1 - h2 <= threshold:
                group.append(f2)
                used.add(f2)
        grouped.append(group)
    return grouped

def clean_dataset_and_export_log(groups, img_dir, output_dir, log_path):
    os.makedirs(output_dir, exist_ok=True)
    log_lines = []
    keep_count = 0

    for idx, group in enumerate(groups):
        if not group:
            continue
        keep = group[0]
        shutil.copy2(os.path.join(img_dir, keep), os.path.join(output_dir, keep))
        keep_count += 1

        log_lines.append(f"# Group {idx}")
        log_lines.append(f"✓ keep: {keep}")
        for fname in group[1:]:
            log_lines.append(f"✗ drop: {fname}")
        log_lines.append("")  # 空行分隔

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"✅ 清洗完成：从 {sum(len(g) for g in groups)} 张中保留 {keep_count} 张")
    print(f"📝 分组对比文件已导出至：{log_path}")

# 主执行入口
if __name__ == "__main__":
    groups = group_similar_images(IMG_DIR, HASH_THRESHOLD)
    clean_dataset_and_export_log(groups, IMG_DIR, OUTPUT_DIR, GROUP_LOG_PATH)
