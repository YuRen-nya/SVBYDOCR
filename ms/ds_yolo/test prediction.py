import os
import cv2
import torch
from ultralytics import YOLO
import matplotlib.pyplot as plt

# 加载训练好的模型
model_path = 'bestv2.pt'  # 替换为你的模型路径
model = YOLO(model_path)

# 验证集路径
dataset_dir = 'ms/datav2'
val_images_dir = os.path.join(dataset_dir, 'images', 'val')
val_labels_dir = os.path.join(dataset_dir, 'labels', 'val')

# 评估模型
def evaluate_model():
    results = model.val(data=os.path.join(dataset_dir, 'data.yaml'), conf=0.4)
    return results

# 可视化预测结果
def visualize_predictions(image_paths, num_samples=5):
    for i in range(min(num_samples, len(image_paths))):
        image_path = image_paths[i]
        results = model.predict(source=image_path, conf=0.1, save=False)  # 设置置信度阈值
        for result in results:
            boxes = result.boxes.cpu().numpy()
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            for box in boxes:
                r = box.xyxy[0].astype(int)
                cls = int(box.cls[0])
                conf = box.conf[0]
                
                # 绘制边界框
                cv2.rectangle(img, (r[0], r[1]), (r[2], r[3]), (0, 255, 0), 2)
                label = f"{model.names[cls]} {conf:.2f}"
                cv2.putText(img, label, (r[0], r[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            plt.figure(figsize=(10, 10))
            plt.imshow(img)
            plt.title(f"Image: {os.path.basename(image_path)}")
            plt.axis('off')
            plt.show()

# 主流程
if __name__ == "__main__":
    # 评估模型
    eval_results = evaluate_model()
    print(eval_results)
    
    # 获取验证集中的图像路径
    val_image_files = [os.path.join(val_images_dir, f) for f in os.listdir(val_images_dir) if f.endswith('.jpg')]
    
    # 可视化部分验证集结果
    visualize_predictions(val_image_files, num_samples=5)



