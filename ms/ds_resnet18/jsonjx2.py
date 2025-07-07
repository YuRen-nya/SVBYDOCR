# prepare_dataset.py

import os
import json
from shutil import copyfile
import random

# 设置路径
json_file_path = 'label_studio_output2.json'  # 替换为你的JSON文件路径
image_base_dir = 'D:/喵~/OCRSZB2/dataset/images'  # 替换为你的实际路径
output_dir = './prepared_dataset2'  # 输出目录
train_dir = os.path.join(output_dir, 'train')
val_dir = os.path.join(output_dir, 'val')
split_ratio = 0.8  # 训练集比例

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# 加载 JSON 数据
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 按照 inner_id 排序，确保顺序一致
data.sort(key=lambda x: x.get('inner_id', 0))  # 使用get方法并提供默认值0以防inner_id不存在

# 处理每个标注
for idx, item in enumerate(data):
    # 构造本地文件名：image_0000.png, image_0001.png ...
    filename = f"image_{idx:04d}.png"

    source_image_path = os.path.join(image_base_dir, filename)

    if not os.path.exists(source_image_path):
        print(f"⚠️ 跳过，找不到文件: {source_image_path}")
        continue

    annotations = item.get('annotations', [])
    if not annotations or len(annotations) == 0 or 'result' not in annotations[0]:
        print(f"⚠️ 跳过，没有有效的注解: {source_image_path}")
        continue

    result = annotations[0].get('result', [])
    if not result or len(result) == 0 or 'value' not in result[0]:
        print(f"⚠️ 跳过，没有有效的结果: {source_image_path}")
        continue

    value = result[0].get('value', {})
    choices = value.get('choices', [])
    if not choices or len(choices) == 0:
        print(f"⚠️ 跳过，没有有效的选择: {source_image_path}")
        continue

    annotation = choices[0]

    # 随机分配到 train 或 val
    target_folder = os.path.join(train_dir if random.random() < split_ratio else val_dir, annotation)
    os.makedirs(target_folder, exist_ok=True)

    # 构造目标路径
    destination_image_path = os.path.join(target_folder, filename)

    # 复制文件
    try:
        copyfile(source_image_path, destination_image_path)
        print(f"✅ 复制成功: {filename} -> {target_folder}")
    except Exception as e:
        print(f"❌ 复制失败: {filename} -> {target_folder}, 错误信息: {str(e)}")

print("✅ 数据集准备完成")