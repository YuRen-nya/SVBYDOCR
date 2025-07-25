# SZBAI 控制器项目

本项目为卡牌游戏影之诗自动化控制与数据采集系统，集成了游戏状态识别、自动策略执行功能。适用于自动化对局等场景。

## 主要功能

- **游戏自动化控制**：自动识别游戏状态，执行策略、自动点击、自动攻击等操作。
- **数据采集**：自动记录每回合状态、动作、奖励等数据，便于后续训练提高识别准确率，策略稳定性。

## 目录结构

```
OCRSZB2/
├── main.py                # 主程序入口，GUI与自动化主流程
├── ai_core.py             # AI推演与动作枚举、执行核心
├── action_playcard.py     # 动作复现与现实操作实现
├── action_de.py           # 卡牌动作与属性数据库（大字典）
├── GameState.py           # 游戏状态识别与数据结构
├── Templates/             # 模板图片与模板匹配脚本
│   ├── ...               # 各类图片与模板
│   └── ...
├── Window_Coordinates_Initial.py # 窗口坐标获取
├── requirements.txt       # 依赖库列表
├── README.md              # 项目说明文档
├── data/                  # 数据记录与保存
├── ...                    # 其它辅助脚本与目录
```

## 依赖环境

- Python 3.8 及以上
- 推荐使用 Anaconda 虚拟环境或 venv

### 主要依赖库

- numpy
- opencv-python
- pyautogui
- pillow
- scikit-learn
- tkinter（标准库，Windows 自带）
- threading（标准库）
- time、os、json、functools 等标准库

### 安装依赖

推荐使用 requirements.txt 一键安装：

```bash
pip install -r requirements.txt
```

如遇部分库未包含，可手动安装：

```bash
pip install numpy opencv-python pyautogui pillow scikit-learn
```

## 快速上手

1. **准备好游戏窗口**，确保分辨率为 1600\*900 设置。
2. **运行主程序**，python main.py
3. **功能介绍**，运行一次完整回合流程：单局测试用；切换自动运行开关状态：在一局对战的结束界面启动可以自动循环运行\*；手动触发主要游戏流程：换牌后点击可以自动运行一场对战。

## 运行方式

1. 启动 main.py：
   ```bash
   python main.py
   ```
2. 按照界面提示操作。

3. **使用 GUI 界面**进行手动/自动控制，查看日志与数据采集情况。
4. **数据与模型训练**：进入`ms/`目录，运行相应的训练/测试脚本（如 YOLO、ResNet18 等）。

如有问题请联系开发者或提交 issue

该项目雷点：
局外流程一坨；
弹个每日任务奖励就不自动循环了；
同名手牌连在一起认不出；
没做错误捕获导致一出错就卡死；
没 log

已知 bug：
关于部分卡的战场识别失效问题；
局外流程的超时 bug
