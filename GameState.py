# GameState.py
# 游戏状态识别模块
# 功能：识别游戏界面中的各种状态信息，包括生命值、法力值、随从信息、手牌等
# 作者：SZBAI开发团队
# 版本：2.0
# 更新日期：2024年
# 
# 主要功能：
# 1. 使用OCR技术识别游戏界面中的数值信息（生命值、法力值等）
# 2. 使用YOLO模型检测战场上的随从位置和属性
# 3. 使用图像分类模型识别随从状态（dash/normal/rush）和嘲讽状态
# 4. 提供完整的游戏状态数据结构，供策略选择模块使用

from ultralytics import YOLO
from Catch_image import get_screenshot_region
import cv2
import numpy as np
import pyautogui
import time
import os
from Window_Coordinates_Initial import get_window_rect
from PIL import Image
import torch
from torchvision import models, transforms
from Templates import detect_hand_card, detect_own_minion,load_templates,template_match

# ===== 窗口坐标初始化 =====
# 获取游戏窗口坐标，用于精确定位游戏界面元素
coords = get_window_rect()
if coords is None:
    print("[警告] 无法获取窗口坐标，使用默认值")
    [x_o, y_o, x_ob, y_ob] = [0, 0, 1920, 1080]  # 默认全屏坐标
else:
    [x_o, y_o, x_ob, y_ob] = coords

# ===== 模板匹配初始化 =====
# 加载各种数值识别的模板图像，用于OCR识别
phpt,phpl=load_templates("Templates/player_hp_img1")  # 玩家生命值模板
ohpt,ohpl=load_templates("Templates/opponent_hp_img1")  # 对手生命值模板
manat,manal=load_templates("Templates/mana_img1")  # 法力值模板
et,el=load_templates("Templates/e_img1")  # 能量值模板
set,sel=load_templates("Templates/se_img1")  # 特殊能量值模板
ppt,ppl=load_templates("Templates/pp_img1")  # PP值模板

# ===== YOLO模型初始化 =====
# YOLO模型，用于目标检测和数值识别
model1 = YOLO('best.pt')  # 随从目标检测模型 - 检测战场上的随从位置
model2 = YOLO('bestv2.pt')  # 数值检测模型 - 检测随从的攻击力和生命值

# ===== 图像分类模型1配置 =====
# 分类模型配置1 - 用于检测随从状态（dash/normal/rush）
# dash: 冲锋状态，可以立即攻击
# normal: 普通状态，需要等待一回合才能攻击
# rush: 突袭状态，可以攻击敌方随从但不能攻击英雄
class_names1 = ['dash','normal','rush']  # 随从状态类别
CLASS_COUNT1 = len(class_names1)

# 加载图像分类模型1
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")  # 选择GPU或CPU
model_cls1 = models.resnet18(weights=None)  # 使用ResNet18架构
num_ftrs = model_cls1.fc.in_features
model_cls1.fc = torch.nn.Linear(num_ftrs, CLASS_COUNT1)  # 修改最后一层以匹配类别数
try:
    model_cls1.load_state_dict(torch.load('image_classifier1.pth'))  # 加载训练好的权重
except Exception as e:
    raise FileNotFoundError(f"找不到分类模型文件 image_classifier1.pth:{e}")
model_cls1.to(device)  # 将模型移到指定设备
model_cls1.eval()  # 设置为评估模式

# ===== 图像分类模型2配置 =====
# 分类模型配置2 - 用于检测嘲讽状态（True/False）
# True: 嘲讽状态，敌方必须先攻击具有嘲讽的随从
# False: 非嘲讽状态，正常攻击规则
class_names2 = ['False', 'True']  # 嘲讽状态类别（字符串形式）
CLASS_COUNT2 = len(class_names2)

# 加载图像分类模型2
model_cls2 = models.resnet18(weights=None)  # 使用ResNet18架构
num_ftrs = model_cls2.fc.in_features
model_cls2.fc = torch.nn.Linear(num_ftrs, CLASS_COUNT2)  # 修改最后一层以匹配类别数
try:
    model_cls2.load_state_dict(torch.load('image_classifier2.pth'))  # 加载训练好的权重
except Exception as e:
    raise FileNotFoundError(f"找不到分类模型文件 image_classifier2.pth:{e}")
model_cls2.to(device)  # 将模型移到指定设备
model_cls2.eval()  # 设置为评估模式

# ===== 图像预处理配置 =====
# 图像分类模型预处理 - 标准化图像尺寸和像素值
# 这些参数是ImageNet预训练模型的标准参数
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # 调整图像尺寸为224x224
    transforms.ToTensor(),  # 转换为张量
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # 标准化
])

class GameState:
    """
    游戏状态类
    存储当前游戏的所有状态信息，包括生命值、法力值、随从信息、手牌等
    这是整个AI系统的核心数据结构，所有策略决策都基于这个状态对象
    """
    def __init__(self):
        # 窗口偏移量 - 用于计算绝对坐标
        self.co = []

        # ===== 基础游戏信息 =====
        self.player_hp = 20  # 玩家当前HP，初始值为20
        self.opponent_hp = 20  # 敌方当前HP，初始值为20
        self.mana = 0  # 当前mana，每回合会增加

        # ===== 我方随从相关 =====
        self.own_minion_count = 0  # 我方随从数量
        self.own_minion_positions = []   # 随从位置列表 [(x1, y1, x2, y2), ...]
        self.own_minion_attack = []      # 攻击力列表 [atk1, atk2, ...]
        self.own_minion_health = []      # 生命值列表 [hp1, hp2, ...]
        self.own_minion_follows = []     # 随从状态列表（dash/normal/rush）
        self.own_minion_ids = []         # 随从ID列表 [id1, id2, ...] 用于标识每个随从

        # ===== 敌方随从相关 =====
        self.opponent_minion_count = 0  # 敌方随从数量
        self.opponent_minion_positions = []  # 随从位置列表
        self.opponent_minion_attack = []  # 攻击力列表
        self.opponent_minion_health = []  # 生命值列表
        self.opponent_minion_taunt = []  # 嘲讽状态列表 True/False 表示是否具有嘲讽守护状态

        # ===== 手牌信息 =====
        self.hand_card_count = 0  # 手牌数量
        self.hand_card_ids = []          # 手牌ID列表 [card_id1, card_id2, ...]

        # ===== 其他OCR获取的数值 =====
        self.e_value = 0                 # 当前e值（能量值），用于某些特殊卡牌
        self.se_value = 0                # 当前se值（特殊能量值），用于某些特殊卡牌
        self.PP1 = 0                     # 后手PP值，用于后手优势机制

    def print_state(self):
        """
        打印当前游戏状态
        用于调试和状态监控，输出所有重要的游戏信息
        """
        print("=== Game State ===")
        print(f"玩家 HP: {self.player_hp}")
        print(f"敌方 HP: {self.opponent_hp}")
        print(f"当前 Mana: {self.mana}")
        print(f"E 值: {self.e_value}")
        print(f"SE 值: {self.se_value}")
        print(f"后手 PP: {self.PP1}")

        print("\n【我方随从】")
        print(f"数量: {self.own_minion_count}")
        print(f"位置列表: {self.own_minion_positions}")
        print(f"攻击力列表: {self.own_minion_attack}")
        print(f"生命值列表: {self.own_minion_health}")
        print(f"ID 列表: {self.own_minion_ids}")
        print(f"是否可攻击: {self.own_minion_follows}")

        print("\n【敌方随从】")
        print(f"数量: {self.opponent_minion_count}")
        print(f"位置列表: {self.opponent_minion_positions}")
        print(f"攻击力列表: {self.opponent_minion_attack}")
        print(f"生命值列表: {self.opponent_minion_health}")
        print(f"是否有守护: {self.opponent_minion_taunt}")

        print("\n【手牌信息】")
        print(f"手牌数量: {self.hand_card_count}")
        print(f"手牌 ID 列表: {self.hand_card_ids}")
        print("==================")
    
def Get_GameState(state):
    """
    获取完整的游戏状态
    通过OCR和AI模型识别游戏界面中的各种信息
    这是状态识别的核心函数，会调用多个子函数来完成不同的识别任务
    
    Args:
        state: GameState对象，用于存储识别到的状态信息
    """
    # ===== 生命值检测 =====
    # 检测玩家生命值，使用模板匹配方法
    php=template_match((948 + x_o, 675 + y_o, 60, 40),phpt,phpl,0.5)
    state.player_hp = int(php)
    # 如果检测到生命值为0，尝试重新检测（可能是识别错误）
    # 通过点击屏幕来刷新界面显示
    if state.player_hp == 0:
        pyautogui.mouseDown(1225+x_o,900+y_o)
        time.sleep(0.5)
        pyautogui.mouseUp()
        php=template_match((948 + x_o, 675 + y_o, 60, 40),phpt,phpl,0.5)
        state.player_hp = int(php)
    
    # 检测对手生命值
    ohp=template_match((928 + x_o, 90 + y_o, 60, 40),ohpt,ohpl,0.5)
    state.opponent_hp = int(ohp)

    # ===== 法力值检测 =====
    mana=template_match((1448 + x_o, 560 + y_o, 45, 30),manat,manal)
    state.mana = int(mana)

    # ===== 战场检测 =====
    # 检测战场上的随从信息，使用YOLO模型
    Get_b_i(state)



    # ===== 手牌检测 =====
    # 识别手牌信息，使用模板匹配方法
    detect_hand_card(state,templates_folder="Templates/MB_h", region=(x_o, y_o+700, x_ob, y_ob))
    state.hand_card_count = len(state.hand_card_ids)
    
    # ===== 其他数值检测 =====
    # 检测能量值（E值）
    e_value = template_match((680 + x_o, 680 + y_o, 60, 30),et,el,0.9)
    state.e_value = int(e_value)
    # 检测特殊能量值（SE值）
    se_value = template_match((880 + x_o, 680 + y_o, 60, 30),set,sel,0.9)
    state.se_value = int(se_value)
    # 检测PP值（后手优势）
    PP = template_match((1330 + x_o, 660 + y_o, 40, 30),ppt,ppl)
    state.PP1 = int(PP)
    # 打印当前状态，用于调试和监控
    state.print_state()

def Get_b_i(state):
    """
    获取战场信息（Battlefield Information）
    使用YOLO模型检测战场上的随从并识别其属性
    这是最复杂的识别函数，涉及目标检测、数值识别和状态分类
    
    Args:
        state: GameState对象，用于存储战场信息
    """
    # ===== 清空之前的数据 =====
    # 重置所有随从相关的数据，确保数据的一致性
    state.own_minion_count = 0
    state.opponent_minion_count = 0

    state.own_minion_positions.clear()
    state.opponent_minion_positions.clear()

    state.own_minion_attack.clear()
    state.opponent_minion_attack.clear()

    state.own_minion_health.clear()
    state.opponent_minion_health.clear()

    state.own_minion_follows.clear()
    state.opponent_minion_taunt.clear()

    state.own_minion_ids.clear()

    # ===== 目标检测 =====
    # 截取战场区域的图像，这是随从所在的主要区域
    image = get_screenshot_region(250+x_o,210+y_o,1050,420)
    image1 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # 使用YOLO模型检测随从，置信度阈值为0.4
    results = model1.predict(source=image1, conf=0.4, save=False,verbose=False)
    
    # ===== 数据分类 =====
    minions = []  # 我方随从列表
    enemy_minions = []  # 敌方随从列表

    # 处理检测结果，根据位置区分敌我随从
    # 通过Y坐标判断：上半部分是敌方，下半部分是我方
    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            r0 = box.xyxy[0].astype(int)  # 相对坐标（相对于截取区域）
            r=[r0[0]+250+x_o,r0[1]+210+y_o,r0[2]+250+x_o,r0[3]+210+y_o]  # 绝对坐标（相对于屏幕）
            cls = int(box.cls[0])  # 类别
            conf = box.conf[0]  # 置信度
            label = f"{model1.names[cls]} {conf:.2f}"
            y_max = r[3]
            # 根据Y坐标判断是敌方还是我方随从
            if y_max < 500 + y_o:
                enemy_minions.append((r0, r, cls, conf))  # 敌方随从
            else:
                minions.append((r0, r, cls, conf))  # 我方随从

    # 按X坐标排序，确保随从顺序一致，便于后续处理
    enemy_minions.sort(key=lambda x: x[0][0])
    minions.sort(key=lambda x: x[0][0])
    
    # ===== 数据集管理 =====
    # 检测已有图片数量，用于生成新的文件名
    # 这些图片用于模型训练和数据集扩充
    existing_files = [f for f in os.listdir('dataset\images') if f.startswith('image_') and f.endswith('.png')]
    next_index = len(existing_files)

    # ===== 敌方随从处理 =====
    for idx, (r0, r, cls, conf) in enumerate(enemy_minions):
        label = f"{model1.names[cls]} {conf:.2f}"
        print(f"检测到对象: {label}, 坐标: {r}")

        # 确保 r 是包含四个整数的元组
        r_tuple = tuple(r)
        
        # 保存随从图像到数据集，用于模型训练
        filename = f"image_{next_index:04d}.png"
        save_minion_image(r_tuple, os.path.join('dataset\images', filename))
        next_index += 1

        # 更新状态信息
        state.opponent_minion_count += 1
        state.opponent_minion_positions.append(r)
        
        # 提取随从图像用于数值检测
        minion_img = image1[r0[1]:r0[3], r0[0]:r0[2]]
        results = model2.predict(source=minion_img, conf=0.4,verbose=False)
        
        # ===== 数值检测 =====
        digits = [] # 临时排序用变量
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                r = box.xyxy[0].astype(int)
                cls = int(box.cls[0])
                label = model2.names[cls]
                digits.append((label, r[0]))# 保存数字和它的x坐标  
                print(f"检测到对象: {label}, 坐标: {r}")
        
        # 根据X坐标排序，左边是攻击力，右边是生命值
        digits.sort(key=lambda x: x[1])
        if len(digits) == 2:
            attack = digits[0][0]  # 左边是攻击力
            health = digits[1][0]  # 右边是生命值
        else:
            # 如果没有检测到两个数字，则设为0
            attack = 0
            health = 0
        state.opponent_minion_attack.append(int(attack))
        state.opponent_minion_health.append(int(health))
        
        # ===== 嘲讽状态检测 =====
        # 转换为 RGB 并转换成 PIL 图像，用于分类模型
        img_pil = Image.fromarray(cv2.cvtColor(minion_img, cv2.COLOR_BGR2RGB)).convert('RGB')
        img_tensor = transform(img_pil).unsqueeze(0).to(device)

        # 使用分类模型检测嘲讽状态
        with torch.no_grad():
            output = model_cls2(img_tensor)
            _, preds = torch.max(output, 1)
            label = class_names2[preds.item()]
        # 将字符串转换为布尔值
        state.opponent_minion_taunt.append(label == 'True')

    # ===== 我方随从处理 =====
    for idx, (r0,r, cls, conf) in enumerate(minions):
        label = f"{model1.names[cls]} {conf:.2f}"
        print(f"检测到对象: {label}, 坐标: {r}")

         # 确保 r 是包含四个整数的元组
        r_tuple = tuple(r)
        
        # 保存随从图像到数据集
        filename = f"image_{next_index:04d}.png"
        save_minion_image(r_tuple, os.path.join('dataset\images', filename))
        next_index += 1

        # 更新状态信息
        state.own_minion_count += 1
        state.own_minion_positions.append(r)
        
        # 提取随从图像用于数值检测
        minion_img = image1[r0[1]:r0[3], r0[0]:r0[2]]
        results = model2.predict(source=minion_img, conf=0.4,verbose=False)
        
        # ===== 数值检测 =====
        digits = [] # 临时排序用变量
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                r = box.xyxy[0].astype(int)
                cls = int(box.cls[0])
                label = model2.names[cls]
                digits.append((label, r[0]))# 保存数字和它的x坐标
        digits.sort(key=lambda x: x[1])
        if len(digits) == 2:
            # 根据x坐标排序，左边是攻击，右边是生命
            attack = digits[0][0]
            health = digits[1][0]
        else:
            # 如果没有检测到两个数字，则设为0
            attack = 0
            health = 0
        state.own_minion_attack.append(int(attack))
        state.own_minion_health.append(int(health))
        
        # ===== 随从状态检测 =====
        # 转换为 RGB 并转换成 PIL 图像
        img_pil = Image.fromarray(cv2.cvtColor(minion_img, cv2.COLOR_BGR2RGB)).convert('RGB')
        img_tensor = transform(img_pil).unsqueeze(0).to(device)

        # 使用分类模型检测随从状态（dash/normal/rush）
        with torch.no_grad():
            output = model_cls1(img_tensor)
            _, preds = torch.max(output, 1)
            label = class_names1[preds.item()]
        state.own_minion_follows.append(label)
    
    # ===== 随从ID检测 =====
    # 使用原始的detect_own_minion逻辑，但集成到Get_b_i中
    # 清空之前的ID列表
    state.own_minion_ids.clear()
    
    # 模板匹配
    from Templates import find_all_templates_in_screenshot, extract_instance_info
    region = (x_o, y_o+400, 1400, 230)  # 我方随从区域
    # a=pyautogui.screenshot(region=region)  # 截图区域
    # a.show()  # 调试
    all_boxes = find_all_templates_in_screenshot("MB_b", region=region, c1=0.3)
    instance_list = extract_instance_info(all_boxes)
    instance_list.sort(key=lambda x: x["min_x"])
    
    # 更新状态 - 只添加与检测到的随从数量匹配的ID
    for i, item in enumerate(instance_list):
        if i < state.own_minion_count:  # 确保ID数量不超过实际随从数量
            state.own_minion_ids.append(item['name'])
    
    # 如果ID数量不足，用默认值填充
    while len(state.own_minion_ids) < state.own_minion_count:
        state.own_minion_ids.append("未知随从")
        




def save_minion_image(minion_pos, filename):
    """
    保存随从图像到文件
    用于数据集收集和训练，为模型改进提供数据支持
    
    Args:
        minion_pos: 随从位置坐标 (x1, y1, x2, y2)
        filename: 保存的文件名
    """
    # 正确计算 region 参数
    x = int(minion_pos[0])
    y = int(minion_pos[1])
    width = int(minion_pos[2]) - int(minion_pos[0])
    height = int(minion_pos[3]) - int(minion_pos[1])
    
    # 截取指定区域的图像并保存
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot.save(filename)

class DecisionInformation:
    """
    决策信息类
    用于存储决策相关的信息（预留接口）
    为未来的决策优化功能预留扩展空间
    """
    def __init__(self):
        pass