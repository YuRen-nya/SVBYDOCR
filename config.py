# config.py

import cv2
from ultralytics import YOLO

# 定义识别区域
REGIONS = {
    'mana':         (878, 470, 34, 20),   # 费用
    'card_num':     (45, 743, 15, 22),    # 手牌数量
    'player_hp':    (570, 625, 30, 25),   # 玩家血量
    'opponent_hp':  (550, 105, 30, 25),   # 对手血量
}

# 卡片详细信息显示区域
DETAIL_REGION_LEFT_TOP = (55, 100, 250, 25)      # 左上角卡片详情区（用于 <3 随从 或非首个随从）
DETAIL_REGION_RIGHT_TOP = (670, 100, 250, 25)    # 右上角卡片详情区（用于 ≥3 随从 的第一个）

# 定义基础分数字典
BASE_CARD_SCORES = {
    "Indomitable Fighter": 3,
    "Leah, Bellringer Angel": 2,
    "Devious Lesser Mummy": 3,
    "Mino, Shrewd Reaper": 3,
    "Beryl, Nightmare Incarnate": 5,
    "Orthrus, Hellhound Blader": 4,
    "Rage of Serpents": 1,
    "Apollo, Heaven's Envoy": 2,
    "Little Miss Bonemancer": 3,
    "Balto, Dusk Bounty Hunter": 5,
    "Divine Thunder": 0,
    "Ceres, Blue Rose Maiden":4,
    "Mukan, Shadewcrypt Ward": 2,
    "Aragavy, Eternal Hunter": 5,
    "Cerberus, Hellfire Unleashed": 5,
    "Skeleton":1
}

# 定义每张卡牌的特定条件
CARD_CONDITION_RULES = {
    "Indomitable Fighter": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 2, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99},
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 4, 'adjustment': 4}
    ],
    "Leah, Bellringer Angel": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 2, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99}
    ],
    "Devious Lesser Mummy": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 2, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99},
        {'type': 'opponent_hp', 'operator': '<', 'param_index': 2, 'threshold': 15, 'adjustment': 1},
        {'type': 'dash_attack_total', 'operator': '>=', 'param_index': 2, 'threshold': 5, 'adjustment': 15}
    ],
    "Mino, Shrewd Reaper": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 2, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99},
        {'type': 'mana', 'operator': '>=', 'param_index': 0, 'threshold': 4, 'adjustment': -10}
    ],
    "Beryl, Nightmare Incarnate": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 2, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99}
    ],
    "Orthrus, Hellhound Blader": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 2, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99},
        {'type': 'enemy_minion_health', 'operator': '>', 'param_index': 0, 'threshold': 2, 'adjustment': 1}
    ],
    "Rage of Serpents": [
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 2, 'adjustment': -99},
        {'type': 'opponent_hp', 'operator': '<', 'param_index': 2, 'threshold': 10, 'adjustment': 5},
        {'type': 'dash_attack_total', 'operator': '>=', 'param_index': 2, 'threshold': 3, 'adjustment': 15}
    ],
    "Apollo, Heaven's Envoy": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 3, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 3, 'adjustment': -99},
        {'type': 'enemy_minion_health', 'operator': '==', 'param_index': 0, 'threshold': 1, 'adjustment': 2}
    ],
    "Little Miss Bonemancer": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 3, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 3, 'adjustment': -99}
    ],
    "Balto, Dusk Bounty Hunter": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 3, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 3, 'adjustment': -99}
    ],
    "Divine Thunder": [
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 4, 'adjustment': -99},
        {'type': 'enemy_minion_attack_and_health', 'operator': '>=', 'param_index': 0, 'threshold': 4, 'adjustment': 7}
    ],
    "Ceres, Blue Rose Maiden": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 4, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 4, 'adjustment': -99}
    ],
    "Mukan, Shadewcrypt Ward": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 4, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 4, 'adjustment': -99},
        {'type': 'enemy_minion_attack_and_health', 'operator': '>=', 'param_index': 0, 'threshold': 5, 'adjustment': 2}
    ],
    "Aragavy, Eternal Hunter": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 5, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 5, 'adjustment': -99}
    ],
    "Cerberus, Hellfire Unleashed": [
        {'type': 'mana', 'operator': '=', 'param_index': 0, 'threshold': 8, 'adjustment': 3},
        {'type': 'mana', 'operator': '<', 'param_index': 0, 'threshold': 8, 'adjustment': -99}
    ]
}

# 特殊卡牌动作字典
SPECIAL_CARDS_ACTIONS = {
    "Rage of Serpents": {"action": "left_click", "position": (475, 130)},  # 左键点击坐标 (475, 100)
    # 其他特殊卡牌...
}

# 手牌位置定义
HAND_CARD_POSITIONS = {
    1: [(500, 750)],
    2: [(450, 750), (550, 750)],
    3: [(400, 750), (500, 750), (600, 750)],
    4: [(350, 750), (450, 750), (550, 750), (650, 750)],
    5: [(300, 750), (400, 750), (500, 750), (600, 750), (700, 750)],
    6: [(275, 750), (375, 750), (475, 750), (575, 750), (675, 750), (775, 750)],
    7: [(240, 750), (330, 750), (420, 750), (510, 750), (600, 750), (690, 750), (780, 750)],
    8: [(220, 750), (300, 750), (380, 750), (460, 750), (540, 750), (620, 750), (700, 750), (780, 750)],
    9: [(200, 750), (270, 750), (340, 750), (410, 750), (480, 750), (550, 750), (620, 750), (690, 750), (760, 750)]
}

# 预处理函数：用于法力值
def preprocess_mana(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, ksize=3)
    resized = cv2.resize(denoised, None, fx=4, fy=5, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

# 预处理函数：用于手牌数量
def preprocess_card_num(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_LINEAR)
    _, binary = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY_INV)
    return binary



