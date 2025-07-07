# config.py
# 策略配置和执行模块
# 功能：定义游戏策略、动作映射、卡牌执行逻辑和策略选择算法
# 作者：SZBAI开发团队
# 版本：2.0
# 更新日期：2024年
#
# 主要内容：
# 1. 定义所有卡牌和策略的评分规则（CL字典）
# 2. 定义卡牌出牌、能量、特殊能量等操作的执行函数
# 3. 提供策略选择算法 find_best_strategy
# 4. 提供辅助的出牌、拖拽、右键等操作函数

from GameState import Get_b_i
import pyautogui
import time
import GameState
from ATT import perform_full_attack,drag_attack

# ===== 手牌位置配置 =====
# 不同手牌数量下的手牌位置坐标（用于模拟点击）
HAND_CARD_POSITIONS = {
    1: [(850, 800)],  # 1张手牌的位置
    2: [(750, 800), (950, 800)],  # 2张手牌的位置
    3: [(700, 800), (850, 800), (1050, 800)],  # 3张手牌的位置
    4: [(600, 800), (800, 800), (950, 800), (1100, 800)],  # 4张手牌的位置
    5: [(510, 800), (680, 800), (850, 800), (1020, 800), (1190, 800)],  # 5张手牌的位置
    6: [(450, 800), (600, 800), (780, 800), (950, 800), (1100, 800), (1250, 800)],  # 6张手牌的位置
    7: [(400, 800), (550, 800), (700, 800), (850, 800), (1000, 800), (1150, 800), (1300, 800)],  # 7张手牌的位置
    8: [(400, 800), (550, 800), (650, 800), (800, 800), (900, 800), (1050, 800), (1150, 800), (1300, 800)],  # 8张手牌的位置
    9: [(350, 800), (500, 800), (600, 800), (730, 800), (850, 800), (950, 800), (1050, 800), (1200, 800), (1350, 800)]  # 9张手牌的位置
}

def e_v(state, A, H):
    """
    计算能量值（E值）下的随从价值
    找出敌方所有生命值 < A+2 的随从中的最大攻击力
    
    Args:
        state: 游戏状态对象
        A: 攻击力
        H: 生命值
    
    Returns:
        int: 计算出的价值分数
    """
    # 找出敌方所有生命值 < A+2 的随从中的最大攻击力
    max_filtered_atk = max(
        [atk for atk, hp in zip(state.opponent_minion_attack, state.opponent_minion_health) if hp < A + 2],
        default=0
    )
    return (A + 2) + max(H + 2, max_filtered_atk)

def se_v(state, A, H):
    """
    计算特殊能量值（SE值）下的随从价值
    找出敌方生命值小于 A+3 的随从，并计算它们的 atk + hp
    
    Args:
        state: 游戏状态对象
        A: 攻击力
        H: 生命值
    
    Returns:
        int: 计算出的价值分数
    """
    # 找出敌方生命值小于 A+3 的随从，并计算它们的 atk + hp
    filtered_values = [
        atk + hp 
        for atk, hp in zip(state.opponent_minion_attack, state.opponent_minion_health)
        if hp < A + 3
    ]
    # 取最大值，如果没有则为 0
    max_filtered_value = max(filtered_values, default=0)
    
    # 返回总价值：攻+3 + 血+3 + 最大敌方组合值
    return (A + 3) + (H + 3) + max_filtered_value

# ===== 策略配置字典 =====
# CL字典结构：
# key: 策略ID（int）
# value: [卡名列表, 所需法力值, 使用情况(n/e/se), 基础分数, 条件分数函数, 驻场价值函数, 斩杀线]
# - 卡名列表：如['骷髅']
# - 所需法力值：如2
# - 使用情况：'n'普通，'e'能量，'se'特殊能量
# - 基础分数：策略基础分
# - 条件分数函数：根据state动态加分
# - 驻场价值函数：根据state动态加分
# - 斩杀线：用于判断斩杀机会
CL = {
    1:[['骷髅'],0,'n',60,0,lambda state: (1+1),0],  # 骷髅-普通情况
    2:[['骷髅'],0,'e',60,0,lambda state: e_v(state,1,1),0],  # 骷髅-能量情况
    3:[['剑斗士'],2,'n',40,0,lambda state: (2+2),0],  # 剑斗士-普通情况
    4:[['剑斗士'],2,'e',40,0,lambda state: e_v(state,2,2),0],  # 剑斗士-能量情况
    5:[['叮当'],2,'n',40,lambda state: (40 if state.player_hp < 10 else 0),lambda state: (2+2),0],  # 叮当-普通情况
    6:[['叮当'],2,'e',80,lambda state: (40 if state.player_hp < 10 else 0),lambda state: e_v(state,2,2),0],  # 叮当-能量情况
    7:[['叮当'],2,'se',80,lambda state: (40 if state.player_hp < 10 else 0),lambda state: se_v(state,2,2),1],  # 叮当-特殊能量情况
    8:[['爽朗天宫'],2,'n',60,0,lambda state: (2+2),0],  # 爽朗天宫-普通情况
    9:[['爽朗天宫'],2,'e',60,0,lambda state: e_v(state,2,2)+max([a + h for a, h in zip(state.opponent_minion_attack, state.opponent_minion_health)], default=0),0],  # 爽朗天宫-能量情况
    10:[['爽朗天宫'],2,'se',60,0,lambda state: se_v(state,2,2)+max([a + h for a, h in zip(state.opponent_minion_attack, state.opponent_minion_health)], default=0),1],  # 爽朗天宫-特殊能量情况
    11:[['木乃伊'],2,'n',60,lambda state: (20 if state.opponent_hp < 10 else 0),lambda state: (2+2),2],  # 木乃伊-普通情况
    12:[['木乃伊'],2,'e',60,lambda state: (20 if state.opponent_hp < 10 else 0),lambda state: (2+2),4],  # 木乃伊-能量情况
    13:[['木乃伊'],2,'se',60,lambda state: (20 if state.opponent_hp < 10 else 0),lambda state: se_v(state,2,2),5],  # 木乃伊-特殊能量情况
    14:[['蜜诺'],2,'n',60,0,lambda state: (2+2),0],  # 蜜诺-普通情况
    15:[['蜜诺'],2,'e',40,0,lambda state: e_v(state,2,2),0],  # 蜜诺-能量情况
    16:[['欧特鲁斯'],2,'n',80,lambda state: (40 if state.player_hp < 10 else 0),lambda state: (2+2),0],  # 欧特鲁斯-普通情况
    17:[['欧特鲁斯'],2,'e',80,lambda state: (40 if state.player_hp < 10 else 0),lambda state: e_v(state,2,2)+max(
        [atk for atk, hp in zip(state.opponent_minion_attack, state.opponent_minion_health) if hp < 2], default=0)*2,0],  # 欧特鲁斯-能量情况
    18:[['欧特鲁斯'],2,'se',60,lambda state: (40 if state.player_hp < 10 else 0),lambda state: e_v(state,2,2)+max(
        [atk for atk, hp in zip(state.opponent_minion_attack, state.opponent_minion_health) if hp < 2], default=0)*2,1],  # 欧特鲁斯-特殊能量情况
    19:[['蛇神之怒'],2,'n',20,lambda state:(40 if state.opponent_hp < 10 else 0),lambda state: (0),3],  # 蛇神之怒-普通情况
    20:[['鬼人'],3,'n',60,0,lambda state: (4+3),0],  # 鬼人-普通情况
    21:[['鬼人'],3,'e',60,0,lambda state: e_v(state,4,3),0],  # 鬼人-能量情况
    22:[['白骨'],3,'n',40,0,lambda state: (1+2+2+2),0],  # 白骨-普通情况
    23:[['白骨'],3,'e',40,0,lambda state: e_v(state,2+2,2+2),0],  # 白骨-能量情况
    24:[['千金'],4,'n',60,0,lambda state: (1+4),0],  # 千金-普通情况
    25:[['千金'],4,'e',60,0,lambda state: (1+2)+max((4+2), max(state.opponent_minion_attack, default=0)),0],  # 千金-能量情况
    26:[['千金'],4,'se',100,0,lambda state: (1+3)+(4+3)*2 + max(
        [atk for atk, hp in zip(state.opponent_minion_attack, state.opponent_minion_health)], default=0),1],  # 千金-特殊能量情况
    27:[['剑斗士'],4,'n',80,0,lambda state: (5+5),0],  # 剑斗士-普通情况
    28:[['剑斗士'],4,'e',80,0,lambda state: e_v(state,5,5),0],  # 剑斗士-能量情况
    29:[['蜜诺'],4,'n',0,0,lambda state: max(
        [atk for atk, hp in zip(state.opponent_minion_attack, state.opponent_minion_health) if not state.opponent_minion_taunt], default=0),0],  # 蜜诺-普通情况
    30:[['狼哥'],5,'n',100,0,lambda state: (4+3+max(sum(state.opponent_minion_health), 7)*2),0],  # 狼哥-普通情况
    31:[['狼哥'],5,'e',100,0,lambda state: e_v(state,4,3)+max(sum(state.opponent_minion_health), 7)*2,0],  # 狼哥-能量情况
    32:[['堕天使'],7,'n',60,0,lambda state: (4+4),0],  # 堕天使-普通情况
    33:[['堕天使'],7,'e',60,0,lambda state: e_v(state,4,4),0],  # 堕天使-能量情况
    # 34:[['堕天使'],7,'se',20,0,lambda state: (0)+(4+max([atk for atk in state.own_minion_attack if atk > 0], default=0)),2],  # 堕天使-特殊能量情况（已注释）
    35:[['美杜莎'],7,'n',60,0,lambda state: (3+7+sum(sorted(state.opponent_minion_attack)[:3])),0],  # 美杜莎-普通情况
    36:[['美杜莎'],7,'se',20,0,lambda state: (6+10+sum(sorted(state.opponent_minion_attack)[:3])),lambda state: max(3, state.opponent_minion_count)],  # 美杜莎-特殊能量情况
    37:[['堕天使+叮当'],7,'se',80,lambda state: (40 if state.player_hp < 10 else 0),lambda state: se_v(state,4,4)+se_v(state,2,2),2],  # 堕天使+叮当组合-特殊能量情况
    38:[['堕天使','爽朗天宫'],7,'se',80,0,lambda state: se_v(state,4,4)+se_v(state,2,2),2],  # 堕天使+爽朗天宫组合-特殊能量情况
    39:[['堕天使','木乃伊'],7,'se',80,lambda state: (20 if state.opponent_hp < 15 else 0),lambda state: se_v(state,4,4)+se_v(state,2,2),2],  # 堕天使+木乃伊组合-特殊能量情况
    40:[['堕天使','蜜诺'],7,'se',80, 0,lambda state: se_v(state,4,4)+se_v(state,2,2),2],  # 堕天使+蜜诺组合-特殊能量情况
    41:[['堕天使','欧特鲁斯'],7,'se', 80,lambda state: (40 if state.player_hp < 10 else 0),lambda state: se_v(state,4,4)+se_v(state,2,2),2],  # 堕天使+欧特鲁斯组合-特殊能量情况
    42:[['堕天使','蛇神之怒'],7,'n', 20,lambda state: (60 if state.opponent_hp < 10 else 0),lambda state: (4+4),4],  # 堕天使+蛇神之怒组合-普通情况
    43:[['狗妹'],8,'n',1000,0,lambda state: (0),lambda state: state.own_minion_count*2+2-2*max(state.own_minion_count-3, 0)],  # 狗妹-普通情况
    44:[['狗妹'],8,'e',1000,0,lambda state: (0),lambda state: state.own_minion_count*2+2-2*max(state.own_minion_count-3, 0)],  # 狗妹-能量情况
    45:[['狗妹'],8,'se',1000,0,lambda state: (0),lambda state: state.own_minion_count*2+1+(-state.own_minion_count**3+7*state.own_minion_count**2-16*state.own_minion_count+16)],  # 狗妹-特殊能量情况
    46:[['堕天使','鬼人'],8,'se',60,0,lambda state: (0),lambda state: 2],  # 堕天使+鬼人组合-特殊能量情况
    47:[['堕天使','白骨'],8,'se',60,0,lambda state: (0),lambda state: 2],  # 堕天使+白骨组合-特殊能量情况
    48:[['堕天使','千金'],9,'se',80,0,lambda state: (0),lambda state: 2],  # 堕天使+千金组合-特殊能量情况
    49:[['堕天使','狼哥'],10,'se',80,0,lambda state: (0),lambda state: 2],  # 堕天使+狼哥组合-特殊能量情况
    50:[['木乃伊','狗妹'],10,'n',20,0,lambda state: (0),lambda state: (4+2-2*max(state.own_minion_count-2, 0))],  # 木乃伊+狗妹组合-普通情况
    51:[['木乃伊','狗妹'],10,'se',20,0,lambda state: (0),lambda state: (4+1+(-state.own_minion_count**3+7*state.own_minion_count**2-16*state.own_minion_count+16))]  # 木乃伊+狗妹组合-特殊能量情况
}

# ===== 动作执行字典 =====
# 执行卡牌的函数映射，每个策略ID对应一个执行函数
ACTION = {
    1: lambda state: play_card(state, CL[1][2], CL[1][0][0]),  # 执行策略1：骷髅-普通
    2: lambda state: play_card(state, CL[2][2], CL[2][0][0]),  # 执行策略2：骷髅-能量
    3: lambda state: play_card(state, CL[3][2], CL[3][0][0]),  # 执行策略3：剑斗士-普通
    4: lambda state: play_card(state, CL[4][2], CL[4][0][0]),  # 执行策略4：剑斗士-能量
    5: lambda state: play_card(state, CL[5][2], CL[5][0][0]),  # 执行策略5：叮当-普通
    6: lambda state: play_card(state, CL[6][2], CL[6][0][0]),  # 执行策略6：叮当-能量
    7: lambda state: play_card(state, CL[7][2], CL[7][0][0]),  # 执行策略7：叮当-特殊能量
    8: lambda state: play_card(state, CL[8][2], CL[8][0][0]),  # 执行策略8：爽朗天宫-普通
    9: lambda state: (play_card(state, CL[9][2], CL[9][0][0]),extra_action(state, CL[9][0][0])),  # 执行策略9：爽朗天宫-能量+额外动作
    10: lambda state: (play_card(state, CL[10][2], CL[10][0][0]), extra_action(state, CL[10][0][0])),  # 执行策略10：爽朗天宫-特殊能量+额外动作
    11: lambda state: play_card(state, CL[11][2], CL[11][0][0]),  # 执行策略11：木乃伊-普通
    12: lambda state: play_card(state, CL[12][2], CL[12][0][0]),  # 执行策略12：木乃伊-能量
    13: lambda state: play_card(state, CL[13][2], CL[13][0][0]),  # 执行策略13：木乃伊-特殊能量
    14: lambda state: play_card(state, CL[14][2], CL[14][0][0]),  # 执行策略14：蜜诺-普通
    15: lambda state: play_card(state, CL[15][2], CL[15][0][0]),  # 执行策略15：蜜诺-能量
    16: lambda state: play_card(state, CL[16][2], CL[16][0][0]),  # 执行策略16：欧特鲁斯-普通
    17: lambda state: play_card(state, CL[17][2], CL[17][0][0]),  # 执行策略17：欧特鲁斯-能量
    18: lambda state: play_card(state, CL[18][2], CL[18][0][0]),  # 执行策略18：欧特鲁斯-特殊能量
    19: lambda state: (play_card(state, CL[19][2], CL[19][0][0]), extra_action(state, CL[19][0][0])),  # 执行策略19：蛇神之怒-普通+额外动作
    20: lambda state: play_card(state, CL[20][2], CL[20][0][0]),  # 执行策略20：鬼人-普通
    21: lambda state: play_card(state, CL[21][2], CL[21][0][0]),  # 执行策略21：鬼人-能量
    22: lambda state: play_card(state, CL[22][2], CL[22][0][0]),  # 执行策略22：白骨-普通
    23: lambda state: play_card(state, CL[23][2], CL[23][0][0]),  # 执行策略23：白骨-能量
    24: lambda state: play_card(state, CL[24][2], CL[24][0][0]),  # 执行策略24：千金-普通
    25: lambda state: play_card(state, CL[25][2], CL[25][0][0]),  # 执行策略25：千金-能量
    26: lambda state: play_card(state, CL[26][2], CL[26][0][0]),  # 执行策略26：千金-特殊能量
    27: lambda state: play_card(state, CL[27][2], CL[27][0][0]),  # 执行策略27：剑斗士-普通
    28: lambda state: play_card(state, CL[28][2], CL[28][0][0]),  # 执行策略28：剑斗士-能量
    29: lambda state: (play_card(state, CL[29][2], CL[29][0][0]), extra_action(state, CL[29][0][0])),  # 执行策略29：蜜诺-普通+额外动作
    30: lambda state: play_card(state, CL[30][2], CL[30][0][0]),  # 执行策略30：狼哥-普通
    31: lambda state: play_card(state, CL[31][2], CL[31][0][0]),  # 执行策略31：狼哥-能量
    32: lambda state: play_card(state, CL[32][2], CL[32][0][0]),  # 执行策略32：堕天使-普通
    33: lambda state: play_card(state, CL[33][2], CL[33][0][0]),  # 执行策略33：堕天使-能量
    # 34: lambda state: (play_card(state, 'n',CL[34][0][0]),extra_action(state, CL[34][0][0])),  # 执行策略34：堕天使-特殊能量（已注释）
    35: lambda state: play_card(state, CL[35][2], CL[35][0][0]),  # 执行策略35：美杜莎-普通
    36: lambda state: play_card(state, CL[36][2], CL[36][0][0]),  # 执行策略36：美杜莎-特殊能量
    37: lambda state: (play_card(state, 'n', CL[37][0][0]), play_card(state, 'n', CL[37][0][1]), extra_action(state, CL[37][0][0])),  # 执行策略37：堕天使+叮当组合
    38: lambda state: (play_card(state, 'n', CL[38][0][0]), play_card(state, 'n', CL[38][0][1]), extra_action(state, CL[38][0][0])),  # 执行策略38：堕天使+爽朗天宫组合
    39: lambda state: (play_card(state, 'n', CL[39][0][0]), play_card(state, 'n', CL[39][0][1]),extra_action(state, CL[39][0][0])),  # 执行策略39：堕天使+木乃伊组合
    40: lambda state: (play_card(state, 'n', CL[40][0][0]), play_card(state, 'n', CL[40][0][1]), extra_action(state, CL[40][0][0])),  # 执行策略40：堕天使+蜜诺组合
    41: lambda state: (play_card(state, 'n', CL[41][0][0]), play_card(state, 'n', CL[41][0][1]), extra_action(state, CL[41][0][0])),  # 执行策略41：堕天使+欧特鲁斯组合
    42: lambda state: (play_card(state, CL[42][2], CL[42][0][0]), play_card(state, CL[42][2], CL[42][0][1]), extra_action(state, CL[42][0][1])),  # 执行策略42：堕天使+蛇神之怒组合
    43: lambda state: (play_card(state, CL[43][2], CL[43][0][0])),  # 执行策略43：狗妹-普通
    44: lambda state: (play_card(state, CL[44][2], CL[44][0][0])),  # 执行策略44：狗妹-能量
    45: lambda state: (play_card(state, 'n', CL[45][0][0]), extra_action(state, CL[45][0][0])),  # 执行策略45：狗妹-特殊能量+额外动作
    46: lambda state: (play_card(state, 'n', CL[46][0][0]), play_card(state, 'n', CL[46][0][1]), extra_action(state, CL[46][0][0])),  # 执行策略46：堕天使+鬼人组合
    47: lambda state: (play_card(state, 'n', CL[47][0][0]), play_card(state, 'n', CL[47][0][1]), extra_action(state, CL[47][0][0])),  # 执行策略47：堕天使+白骨组合
    48: lambda state: (play_card(state, 'n', CL[48][0][0]), play_card(state, 'n', CL[48][0][1]), extra_action(state, CL[48][0][0])),  # 执行策略48：堕天使+千金组合
    49: lambda state: (play_card(state, 'n', CL[49][0][0]), play_card(state, 'n', CL[49][0][1]), extra_action(state, CL[49][0][0])),  # 执行策略49：堕天使+狼哥组合
    50: lambda state: (play_card(state, 'n', CL[50][0][0]), play_card(state, 'n', CL[50][0][1])),  # 执行策略50：木乃伊+狗妹组合-普通
    51: lambda state: (play_card(state, 'n', CL[51][0][0]), play_card(state, 'n', CL[51][0][1]), extra_action(state, CL[51][0][1])),  # 执行策略51：木乃伊+狗妹组合-特殊能量
}

def find_best_strategy(state, CL):
    """
    寻找最佳策略
    根据当前游戏状态选择最优的策略
    
    Args:
        state: 游戏状态对象
        CL: 策略配置字典
    
    Returns:
        int: 最佳策略ID，如果没有可用策略则返回None
    """
    current_mana = state.mana
    hand_cards_set = set(state.hand_card_ids)  # 转成集合提高效率

    # 判断当前状态模式
    if state.se_value > 0:
        mode = 'se'  # 特殊能量模式
    elif state.e_value > 0:
        mode = 'e'   # 能量模式
    else:
        mode = 'n'   # 普通模式

    print(f"[策略匹配] 当前状态: {mode}, 当前Mana: {current_mana}, PP: {state.PP1}")

    best_strategy_id = None
    best_score = -float('inf')
    pp_used = False  # 标记是否使用了PP

    # 提前计算我方 dash 随从攻击力总和
    own_dash_attack_sum = 0
    for i in range(state.own_minion_count):
        if state.own_minion_follows[i] == 'dash':
            own_dash_attack_sum += state.own_minion_attack[i]

    print(f"[斩杀检测] 我方 dash 随从总攻击力: {own_dash_attack_sum}")
    print(f"[斩杀检测] 敌方当前HP: {state.opponent_hp}")

    # 检查是否需要使用PP
    if state.PP1 == 1:
        if current_mana == 1:
            print(f"[PP机制] 当前Mana=1, PP=1，点击PP后可在Mana=2中搜索策略")
            # 点击PP按钮
            pp_x = 1450 + state.co[0]
            pp_y = 660 + state.co[1]
            pyautogui.mouseDown(pp_x, pp_y)
            time.sleep(0.5)
            pyautogui.mouseUp()
            time.sleep(1)
            pp_used = True
            current_mana = 2
            print(f"[PP机制] 已点击PP，当前Mana更新为: {current_mana}")
        elif current_mana == 7:
            print(f"[PP机制] 当前Mana=7, PP=1，点击PP后可在Mana=8中搜索策略")
            # 点击PP按钮
            pp_x = 1330 + state.co[0]
            pp_y = 660 + state.co[1]
            pyautogui.mouseDown(pp_x, pp_y)
            time.sleep(0.5)
            pyautogui.mouseUp()
            time.sleep(1)
            pp_used = True
            current_mana = 8
            print(f"[PP机制] 已点击PP，当前Mana更新为: {current_mana}")

    # ===== Mana 回退机制（改进版） =====
    # 从当前法力值开始，逐步降低法力值寻找可用策略
    for mana in range(current_mana, -1, -1):
        print(f"  → 尝试Mana={mana}下的策略")

        candidates = []  # 候选策略列表

        # 遍历所有策略配置
        for strategy_id, strategy_info in CL.items():
            card_names, required_mana, strategy_mode, base_score, cond_score_func, field_value_func, kill_line = strategy_info
            base_score = int(base_score)

            # 跳过不符合Mana的策略
            if required_mana != mana:
                continue

            # ===== 根据当前模式选择允许的策略类型 =====
            if mode == 'se':
                if strategy_mode not in ['se', 'n']:  # 特殊能量模式下只允许se和n策略
                    continue
            elif mode == 'e':
                if strategy_mode not in ['e', 'n']:  # 能量模式下只允许e和n策略
                    continue
            elif mode == 'n':
                if strategy_mode != 'n':  # 普通模式下只允许n策略
                    continue

            # ===== 检查手牌是否包含所需卡牌（支持多个） =====
            required_cards = set(card_names)
            if not required_cards.issubset(hand_cards_set):
                continue

            # ===== 计算条件分和驻场价值分 =====
            try:
                cond_score = cond_score_func(state) if callable(cond_score_func) else cond_score_func
                field_score = field_value_func(state) if callable(field_value_func) else field_score_func
            except Exception as e:
                print(f"⚠️ 策略{strategy_id}评分出错：{e}")
                continue

            # 计算总分
            total_score = base_score + cond_score + field_score

            # 计算斩杀线
            kill_line = kill_line(state) if callable(kill_line) else kill_line

            # ===== 斩杀加分机制 =====
            # 如果当前dash随从攻击力+斩杀线能击败对手，给予大幅加分
            if (own_dash_attack_sum + kill_line) > state.opponent_hp:
                total_score += 10000
                print(f"    🔥 斩杀机会！策略{strategy_id}额外+10000分")

            candidates.append((total_score, strategy_id))
            print(f"    ✔ 匹配成功：策略{strategy_id} ({card_names}, {strategy_mode}) | 综合评分: {total_score}")

        # ===== 如果在这个 mana 下有候选策略，则选最好的并退出循环 =====
        if candidates:
            candidates.sort(reverse=True)  # 按分数降序排序
            best_score_current = candidates[0][0]
            best_strategy_current = candidates[0][1]

            if best_score_current > best_score:
                best_score = best_score_current
                best_strategy_id = best_strategy_current

            print(f"✅ 在 mana={mana} 找到有效策略，停止回退")
            break  # 跳出整个 mana 循环

    # ===== 返回最终结果 =====
    if best_strategy_id is not None:
        if pp_used:
            print(f"✅ 最终选择策略：{best_strategy_id}，综合评分：{best_score} (使用了PP)")
        else:
            print(f"✅ 最终选择策略：{best_strategy_id}，综合评分：{best_score}")
        return best_strategy_id
    else:
        print("❌ 没有可执行的策略，准备结束回合")
        return None

# ===== 辅助函数 =====
# 这些函数用于实现具体的出牌、拖拽、右键、特殊动作等操作

def right_click(x, y):
    """
    右键点击指定坐标
    用于模拟右键操作（如出牌、激活卡牌等）
    Args:
        x, y: 点击坐标
    """
    pyautogui.rightClick(x, y)

def drag_to(x1, y1, x2, y2, duration=0.5):
    """
    从起点拖拽到终点
    用于模拟拖动能量、特殊能量等操作
    Args:
        x1, y1: 起点坐标
        x2, y2: 终点坐标
        duration: 拖拽持续时间
    """
    pyautogui.moveTo(x1, y1)
    pyautogui.mouseDown()
    pyautogui.moveTo(x2, y2, duration=duration)
    pyautogui.mouseUp()

def get_rightmost_minion_pos(state):
    """
    返回最右边我方随从的位置坐标 (x, y)
    用于能量/特殊能量进化目标定位
    Args:
        state: 游戏状态对象
    Returns:
        tuple: 随从中心坐标 (x, y) 或 None
    """
    if state.own_minion_count == 0:
        return None  # 没有随从不能进化
    # 假设 positions 是按从左到右顺序排列的
    return [(state.own_minion_positions[-1][0]+state.own_minion_positions[-1][2]) * 0.5, (state.own_minion_positions[-1][1]+state.own_minion_positions[-1][3]) * 0.5]

def get_card_position(state, card_name):
    """
    根据 card_name 在 state.hand_card_ids 中的索引，返回其对应的屏幕坐标。
    用于模拟点击手牌出牌
    Args:
        state: 游戏状态对象，包含 hand_card_ids、hand_card_count
        card_name: 要查找的卡牌名称
    Returns:
        tuple: 卡牌坐标 (x, y) 或 None
    """
    try:
        index = state.hand_card_ids.index(card_name)
    except ValueError:
        print(f"❌ 手牌中未找到卡牌：{card_name}")
        return None
    # 重新获取战场信息以确保手牌数量准确
    Get_b_i(state)
    count = state.hand_card_count
    positions = HAND_CARD_POSITIONS.get(count)
    positions = [[x + state.co[0], y + state.co[1]] for x,y in positions]  # 调整位置偏移
    if not positions:
        print(f"❌ 未知的手牌数量：{count}")
        return None
    if index >= len(positions):
        print(f"⚠️ 卡牌索引超出范围：{index}（手牌数量：{count}）")
        return None
    return positions[index]

def play_card(state, strategy_info, card_name):
    """
    根据 strategy_info 和 card_name 执行出牌动作
    支持普通、能量、特殊能量三种出牌方式
    Args:
        state: 游戏状态对象
        strategy_info: 策略类型（'n', 'e', 'se'）
        card_name: 卡牌名称
    """
    card_type = strategy_info
    # 获取卡牌位置
    card_pos = get_card_position(state, card_name)
    if card_pos is None:
        print("🚫 出牌失败：无法获取卡牌位置")
        return
    print(f"[出牌] 正在尝试以模式 '{card_type}' 出牌：{card_name}，位置：{card_pos}")
    # 右键点击卡牌
    pyautogui.moveTo(card_pos[0], card_pos[1], duration=0.1)
    pyautogui.rightClick()
    time.sleep(3)
    # ===== 根据卡牌类型执行不同操作 =====
    if card_type == 'n':
        # 普通出牌
        time.sleep(3)
        print("✔ 标准出牌完成")
    elif card_type == 'e':
        # 能量出牌（进化）
        Get_b_i(state)  # 重新获取战场信息
        rightmost_pos = get_rightmost_minion_pos(state)
        if rightmost_pos is None:
            print("❌ 当前没有我方随从，无法进行进化")
            return
        # 拖拽能量图标到最右随从
        e_icon_x = 710 + state.co[0]
        e_icon_y = 695 + state.co[1]
        drag_to(e_icon_x, e_icon_y, *rightmost_pos)
        time.sleep(6)
        print("✔ 进化操作完成")
    elif card_type == 'se':
        # 特殊能量出牌（超进化）
        Get_b_i(state)  # 重新获取战场信息
        rightmost_pos = get_rightmost_minion_pos(state)
        if rightmost_pos is None:
            print("❌ 当前没有我方随从，无法进行超进化")
            return
        # 拖拽特殊能量图标到最右随从
        se_icon_x = 910 + state.co[0]
        se_icon_y = 695 + state.co[1]
        drag_to(se_icon_x, se_icon_y, *rightmost_pos)
        time.sleep(6)
        print("✔ 超进化操作完成")
    else:
        print(f"⚠️ 不支持的卡牌类型: {card_type}")

from Templates import detect_own_minion

def extra_action(state, card_name):
    """
    执行卡牌的额外动作
    针对特定卡牌（如爽朗天宫、蛇神之怒、蜜诺、堕天使、狗妹）实现特殊操作
    Args:
        state: 游戏状态对象
        card_name: 卡牌名称
    """
    if card_name == '爽朗天宫':
        # 爽朗天宫的额外操作：点击敌方最高攻击随从
        time.sleep(3)
        print("[INFO] 触发 爽朗天宫 的额外操作：点击敌方最高攻击随从")
        max_atk = -1
        target_index = -1
        # 找出敌方攻击力最高的随从
        for i in range(state.opponent_minion_count):
            if state.opponent_minion_attack[i] > max_atk:
                max_atk = state.opponent_minion_attack[i]
                target_index = i
        if target_index != -1 and target_index < len(state.opponent_minion_positions):
            x, y = (state.opponent_minion_positions[target_index][0]+state.opponent_minion_positions[target_index][2])*0.5, (state.opponent_minion_positions[target_index][1]+state.opponent_minion_positions[target_index][3])*0.5
            print(f"[INFO] 目标随从位于位置 {target_index}，坐标 ({x}, {y})")
            pyautogui.mouseDown(x=x, y=y)
            time.sleep(0.5)
            pyautogui.mouseUp()
            time.sleep(0.3)
        else:
            print("[INFO] 敌方场上没有可选目标。")
    # ...（后续每个卡牌的特殊动作都加详细注释，略）

def click_attack(start_pos, end_pos):
    """
    执行攻击操作：从起点拖拽到终点
    用于狗妹等特殊卡牌的攻击流程
    Args:
        start_pos: 起点坐标 (x, y)
        end_pos: 终点坐标 (x, y)
    """
    pyautogui.moveTo(*start_pos)
    pyautogui.mouseDown()
    time.sleep(0.2)
    pyautogui.moveTo(*end_pos)
    time.sleep(0.2)
    pyautogui.mouseUp()

def get_card_position(state, card_name):
    """
    根据 card_name 在 state.hand_card_ids 中的索引，返回其对应的屏幕坐标。
    用于模拟点击手牌出牌
    Args:
        state: 游戏状态对象，包含 hand_card_ids、hand_card_count
        card_name: 要查找的卡牌名称
    Returns:
        tuple: 卡牌坐标 (x, y) 或 None
    """
    try:
        index = state.hand_card_ids.index(card_name)
    except ValueError:
        print(f"❌ 手牌中未找到卡牌：{card_name}")
        return None
    
    # 重新获取战场信息以确保手牌数量准确
    Get_b_i(state)
    count = state.hand_card_count
    positions = HAND_CARD_POSITIONS.get(count)
    positions = [[x + state.co[0], y + state.co[1]] for x,y in positions]  # 调整位置偏移

    if not positions:
        print(f"❌ 未知的手牌数量：{count}")
        return None

    if index >= len(positions):
        print(f"⚠️ 卡牌索引超出范围：{index}（手牌数量：{count}）")
        return None

    return positions[index]

def play_card(state, strategy_info, card_name):
    """
    根据 strategy_info 和 card_name 执行出牌动作
    支持普通、能量、特殊能量三种出牌方式
    Args:
        state: 游戏状态对象
        strategy_info: 策略类型（'n', 'e', 'se'）
        card_name: 卡牌名称
    """
    card_type = strategy_info

    # 获取卡牌位置
    card_pos = get_card_position(state, card_name)
    if card_pos is None:
        print("🚫 出牌失败：无法获取卡牌位置")
        return

    print(f"[出牌] 正在尝试以模式 '{card_type}' 出牌：{card_name}，位置：{card_pos}")

    # 右键点击卡牌
    pyautogui.moveTo(card_pos[0], card_pos[1], duration=0.1)
    pyautogui.rightClick()
    time.sleep(3)

    # ===== 根据卡牌类型执行不同操作 =====
    if card_type == 'n':
        # 普通出牌
        time.sleep(1.5)
        print("✔ 标准出牌完成")

    elif card_type == 'e':
        # 能量出牌（进化）
        Get_b_i(state)  # 重新获取战场信息
        rightmost_pos = get_rightmost_minion_pos(state)
        if rightmost_pos is None:
            print("❌ 当前没有我方随从，无法进行进化")
            return

        # 拖拽能量图标到最右随从
        e_icon_x = 710 + state.co[0]
        e_icon_y = 695 + state.co[1]
        drag_to(e_icon_x, e_icon_y, *rightmost_pos)
        time.sleep(6)
        print("✔ 进化操作完成")

    elif card_type == 'se':
        # 特殊能量出牌（超进化）
        Get_b_i(state)  # 重新获取战场信息
        rightmost_pos = get_rightmost_minion_pos(state)
        if rightmost_pos is None:
            print("❌ 当前没有我方随从，无法进行超进化")
            return

        # 拖拽特殊能量图标到最右随从
        se_icon_x = 910 + state.co[0]
        se_icon_y = 695 + state.co[1]
        drag_to(se_icon_x, se_icon_y, *rightmost_pos)
        time.sleep(6)
        print("✔ 超进化操作完成")

    else:
        print(f"⚠️ 不支持的卡牌类型: {card_type}")

from Templates import detect_own_minion

def extra_action(state, card_name):
    """
    执行卡牌的额外动作
    针对特定卡牌（如爽朗天宫、蛇神之怒、蜜诺、堕天使、狗妹）实现特殊操作
    Args:
        state: 游戏状态对象
        card_name: 卡牌名称
    """
    if card_name == '爽朗天宫':
        # 爽朗天宫的额外操作：点击敌方最高攻击随从
        time.sleep(3)
        print("[INFO] 触发 爽朗天宫 的额外操作：点击敌方最高攻击随从")

        max_atk = -1
        target_index = -1

        # 找出敌方攻击力最高的随从
        for i in range(state.opponent_minion_count):
            if state.opponent_minion_attack[i] > max_atk:
                max_atk = state.opponent_minion_attack[i]
                target_index = i

        if target_index != -1 and target_index < len(state.opponent_minion_positions):
            x, y = (state.opponent_minion_positions[target_index][0]+state.opponent_minion_positions[target_index][2])*0.5, (state.opponent_minion_positions[target_index][1]+state.opponent_minion_positions[target_index][3])*0.5
            print(f"[INFO] 目标随从位于位置 {target_index}，坐标 ({x}, {y})")
            pyautogui.mouseDown(x=x, y=y)
            time.sleep(0.5)
            pyautogui.mouseUp()
            time.sleep(6)
        else:
            print("[INFO] 敌方场上没有可选目标。")

    elif card_name == '蛇神之怒':
        # 蛇神之怒的额外操作：点击对方英雄头像并按住0.5秒
        time.sleep(3)
        print("[INFO] 触发 蛇神之怒 的额外操作：点击对方英雄头像并按住0.5秒")
        hero_x = 780 + state.co[0]
        hero_y = 110 + state.co[1]

        print(f"[INFO] 点击对方英雄头像，坐标 ({hero_x}, {hero_y})，持续0.5秒")
        pyautogui.mouseDown(x=hero_x, y=hero_y)
        time.sleep(0.5)
        pyautogui.mouseUp()

    elif card_name == '蜜诺':
        # 蜜诺的额外操作：拖动最右我方随从到敌方最高血量随从位置
        time.sleep(3)
        Get_b_i(state)  # 重新获取战场信息
        print("[INFO] 触发 蜜诺 的额外操作：拖动最右我方随从到敌方最高血量随从位置")

        if state.own_minion_count == 0:
            print("[INFO] 我方没有随从，无法触发蜜诺效果")
            return

        # 找出最右边的我方随从（x 坐标最大）
        own_rightmost_idx = max(range(state.own_minion_count),
                                key=lambda i: state.own_minion_positions[i][0])

        own_x, own_y = (state.own_minion_positions[own_rightmost_idx][0] + state.own_minion_positions[own_rightmost_idx][2]) * 0.5,(state.own_minion_positions[own_rightmost_idx][1] + state.own_minion_positions[own_rightmost_idx][3]) * 0.5

        # 找出敌方目标随从（优先有守护的，否则最高血量）
        target_index = -1
        max_hp = -1

        for i in range(state.opponent_minion_count):
            if state.opponent_minion_taunt[i]:
                target_index = i
                break  # 优先选择第一个守护随从
        if target_index == -1:
            # 没有守护随从时，找血最多的
            for i in range(state.opponent_minion_count):
                if state.opponent_minion_health[i] > max_hp:
                    max_hp = state.opponent_minion_health[i]
                    target_index = i

        if target_index != -1 and target_index < len(state.opponent_minion_positions):
            target_x, target_y = (state.opponent_minion_positions[target_index][0] + state.opponent_minion_positions[target_index][2]) * 0.5, (state.opponent_minion_positions[target_index][1] + state.opponent_minion_positions[target_index][3]) * 0.5
            print(f"[INFO] 拖动随从 ({own_x}, {own_y}) 到 ({target_x}, {target_y})")
            pyautogui.moveTo(x=own_x, y=own_y)
            pyautogui.mouseDown()
            time.sleep(0.2)
            pyautogui.moveTo(x=target_x, y=target_y, duration=0.3)
            time.sleep(0.2)
            pyautogui.mouseUp()
        else:
            print("[INFO] 敌方场上无目标随从")

    elif card_name == '堕天使':
        # 堕天使的额外操作：读场，拖SE到右边第2个随从，左键点击右边第1个随从
        time.sleep(3)
        print("[INFO] 触发 堕天使 的额外操作：读场，拖SE到右边第2个随从，左键点击右边第1个随从")

        x_o, y_o = state.co[0], state.co[1]

        # 第一步：读场，识别所有随从信息
        print("[INFO] 正在读场，识别随从ID")
        Get_b_i(state)

        # 提取我方随从
        own_minions = state.own_minion_ids

        if len(own_minions) < 2:
            print("[INFO] 随从数量不足，无法触发堕天使效果")
            return

        # 获取 SE 按钮位置
        se_icon_x = 910 + state.co[0]
        se_icon_y = 695 + state.co[1]
        print(f"[INFO] SE 按钮位置为 ({se_icon_x}, {se_icon_y})")

        # 第二步：拖动 SE 到右边第二个随从
        print(f"[INFO] 拖动 SE 到右边第二个随从位置：{state.own_minion_positions[-2]}")
        pyautogui.moveTo(x=se_icon_x, y=se_icon_y)
        pyautogui.mouseDown()
        time.sleep(3)
        pyautogui.moveTo(x=(state.own_minion_positions[-2][0]+state.own_minion_positions[-2][2])*0.5, y=(state.own_minion_positions[-2][1]+state.own_minion_positions[-2][3])*0.5, duration=0.3)
        time.sleep(0.5)
        pyautogui.mouseUp()

        # 第三步：左键点击右边第一个随从
        print(f"[INFO] 左键点击右边第一个随从位置：{state.own_minion_positions[-1]}")
        pyautogui.mouseDown(x=(state.own_minion_positions[-1][0]+state.own_minion_positions[-1][2])*0.5, y=(state.own_minion_positions[-1][1]+state.own_minion_positions[-1][3])*0.5)
        time.sleep(0.5)
        pyautogui.mouseUp()
        time.sleep(3)

    elif card_name == '狗妹':
        # 狗妹的额外操作：复杂的攻击和进化流程
        try:
            time.sleep(3)
            print("[INFO] 触发 狗妹 的额外操作")

            # Step 1: 第一次读场，更新 state
            Get_b_i(state)

            # Step 2: 查找 米米
            try:
                mi_mi_index = state.own_minion_ids.index('米米')
                mi_mi_pos = state.own_minion_positions[mi_mi_index]
                mi_mi_center = (
                    (mi_mi_pos[0] + mi_mi_pos[2]) // 2,
                    (mi_mi_pos[1] + mi_mi_pos[3]) // 2
                )
                print(f"[INFO] 发现 米米，位于 {mi_mi_center}")

                # Step 3: 收集所有敌方目标，并按守护和攻击力排序
                taunt_enemies = []   # 带守护的敌人
                non_taunt_enemies = []  # 不带守护的敌人

                for i in range(state.opponent_minion_count):
                    enemy_id = state.opponent_minion_ids[i]
                    enemy_atk = state.opponent_minion_attack[i]
                    is_taunt = state.opponent_minion_taunt[i]

                    enemy_data = {
                        'index': i,
                        'id': enemy_id,
                        'attack': enemy_atk,
                    }

                    if is_taunt:
                        taunt_enemies.append(enemy_data)
                    else:
                        non_taunt_enemies.append(enemy_data)

                # Step 4: 选择攻击目标
                target = None

                if taunt_enemies:
                    # 有守护敌人，选攻击力最高的
                    target = max(taunt_enemies, key=lambda x: x['attack'])
                    print(f"[INFO] 选择攻击带守护敌人：{target['id']}（攻击力 {target['attack']}）")
                elif non_taunt_enemies:
                    # 没有守护敌人，选攻击力最高的非守护敌人
                    target = max(non_taunt_enemies, key=lambda x: x['attack'])
                    print(f"[INFO] 选择攻击非守护敌人：{target['id']}（攻击力 {target['attack']}）")
                else:
                    return

                # Step 5: 攻击指定敌人
                target_index = target['index']
                target_pos = state.opponent_minion_positions[target_index]
                target_center = (
                    (target_pos[0] + target_pos[2]) // 2,
                    (target_pos[1] + target_pos[3]) // 2
                )
                print(f"[INFO] 攻击敌人 {target['id']}，位置 {target_center}")
                click_attack(mi_mi_center, target_center)
                time.sleep(1)

            except ValueError:
                print("[INFO] 没有发现名为 米米 的随从，跳过攻击流程")

            # Step 6: 再次读场
            Get_b_i(state)

            # Step 7: 查找 狗妹
            try:
                gou_mei_index = state.own_minion_ids.index('狗妹')
                gou_mei_pos = state.own_minion_positions[gou_mei_index]
                gou_mei_center = (
                    (gou_mei_pos[0] + gou_mei_pos[2]) // 2,
                    (gou_mei_pos[1] + gou_mei_pos[3]) // 2
                )
                print(f"[INFO] 找到 狗妹，位于中心点 {gou_mei_center}")

                # Step 8: 获取 SE 图标位置
                se_icon_x = 910 + state.co[0]
                se_icon_y = 695 + state.co[1]
                print(f"[INFO] SE 按钮位置为 ({se_icon_x}, {se_icon_y})")

                # Step 9: 拖动 SE 到 狗妹
                drag_attack((se_icon_x, se_icon_y), gou_mei_center)
                time.sleep(3)

            except ValueError:
                print("[INFO] 没有找到名为 狗妹 的随从")

        except Exception as e:
            print(f"[ERROR] 狗妹额外操作发生异常：{e}")

def click_attack(start_pos, end_pos):
    """
    执行攻击操作：从起点拖拽到终点
    用于狗妹等特殊卡牌的攻击流程
    Args:
        start_pos: 起点坐标 (x, y)
        end_pos: 终点坐标 (x, y)
    """
    pyautogui.moveTo(*start_pos)
    pyautogui.mouseDown()
    time.sleep(0.2)
    pyautogui.moveTo(*end_pos)
    time.sleep(0.2)
    pyautogui.mouseUp()