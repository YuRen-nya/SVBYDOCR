import os
import re

def rename_images(folder):
    # 匹配image_数字.png
    pattern = re.compile(r"^image_(\d+)\.png$")
    files = []
    for fname in os.listdir(folder):
        m = pattern.match(fname)
        if m:
            num = int(m.group(1))
            files.append((num, fname))
    files.sort()  # 按数字排序
    for idx, (num, fname) in enumerate(files):
        new_name = f"img_{idx:04d}.png"
        src = os.path.join(folder, fname)
        dst = os.path.join(folder, new_name)
        os.rename(src, dst)
        print(f"{fname} -> {new_name}")

if __name__ == "__main__":
    folder = "dataset_deduplicated"
    rename_images(folder) 