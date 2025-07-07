from ultralytics import YOLO

# 加载预训练的YOLOv5s模型
model = YOLO('yolov5n.pt')

# 训练模型
results = model.train(
    data='ms/datav2/data.yaml', 
    epochs=50,                                   # 训练轮数
    imgsz=640,                                   # 输入图像大小
    batch=16,                                    # 批次大小
    lr0=0.01,                                    # 初始学习率
    device=None,                                 # 训练设备（自动检测）
    save_period=-1,                              # 每个epoch保存一次检查点
    workers=0
    )

# 评估模型
metrics = model.val()
print(metrics)


 
