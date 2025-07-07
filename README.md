# 以下内容由AI生成！！！不负责真实性与实用性哈


# SZBAI 控制器项目

本项目为卡牌游戏自动化控制与数据采集系统，集成了游戏状态识别、自动策略执行、强化学习数据采集、深度学习模型训练与推理等功能。适用于自动化对局、AI 训练数据采集、模型测试等场景。

## 主要功能

- **游戏自动化控制**：自动识别游戏状态，执行策略、自动点击、自动攻击等操作。
- **数据采集与强化学习**：自动记录每回合状态、动作、奖励等数据，便于后续 AI 训练。
- **模板匹配与 OCR**：基于模板匹配和深度学习模型识别游戏界面中的数值与元素。
- **深度学习模型训练**：集成 YOLO、ResNet18 等模型的训练与推理脚本，支持自定义数据集。
- **可视化与 GUI**：自带 Tkinter 图形界面，便于手动/自动控制与日志查看。

## 目录结构

```
OCRSZB2/
│
├── main.py                  # 主程序，自动化控制与GUI入口
├── GameState.py             # 游戏状态识别与数据结构
├── Config.py                # 策略配置与动作定义
├── ATT.py                   # 攻击执行模块
├── Templates.py             # 模板加载与匹配工具
├── Window_Coordinates_Initial.py # 窗口坐标获取
├── Catch_image.py           # 屏幕截图工具
├── rl_trainer.py            # 强化学习训练脚本
├── rl_data_processor.py     # 强化学习数据处理
│
├── Templates/               # 所有模板图片文件夹（如*_img、MB_h等）
│
├── ms/                      # 数据与模型相关目录
│   ├── ds_yolo/             # YOLO相关训练/测试脚本
│   ├── ds_resnet18/         # ResNet18相关训练/测试脚本
│   ├── datav2/              # YOLO数据集
│   ├── prepared_dataset1/   # 分类模型数据集1
│   ├── prepared_dataset2/   # 分类模型数据集2
│
├── data/                    # 自动采集的游戏数据（json/csv）
├── dataset/                 # 其他数据集
├── backup/                  # 备份代码
├── runs/                    # 训练结果与日志
│
├── best.pt                  # YOLO模型权重
├── bestv2.pt                # YOLO模型权重
├── yolo11n.pt               # YOLO模型权重
├── yolov5nu.pt              # YOLO模型权重
├── image_classifier1.pth    # 分类模型权重1
├── image_classifier2.pth    # 分类模型权重2
│
└── ...                      # 其他辅助文件
```

## 依赖环境

- Python 3.8+
- 主要依赖包（部分功能需 GPU 支持）：
  - opencv-python
  - numpy
  - torch
  - torchvision
  - pyautogui
  - scikit-learn
  - tkinter（标准库）
  - 其他：Pillow、concurrent.futures 等

安装依赖（推荐使用虚拟环境）：

```bash
pip install -r requirements.txt
```

> 如无 requirements.txt，可根据实际用到的包手动安装。

## 快速上手

1. **准备好游戏窗口**，确保分辨率与坐标设置一致。
2. **运行主程序**：

   ```bash
   python main.py
   ```

3. **使用 GUI 界面**进行手动/自动控制，查看日志与数据采集情况。
4. **数据与模型训练**：进入`ms/`目录，运行相应的训练/测试脚本（如 YOLO、ResNet18 等）。

## 数据与模型说明

- **Templates/**：所有模板图片，支持自定义扩展。
- **ms/ds_yolo/**、**ms/ds_resnet18/**：包含训练、验证、数据处理等脚本，适配 ms 目录结构。
- **ms/datav2/**、**ms/prepared_dataset1/**、**ms/prepared_dataset2/**：存放数据集，结构已适配代码。
- **data/**：自动采集的对局数据，便于后续 AI 训练。
