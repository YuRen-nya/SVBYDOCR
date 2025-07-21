# action_playcard.py
import pyautogui
import time
from GameState import Get_b_i

# ===== 手牌位置配置 =====
# 不同手牌数量下的手牌位置坐标（用于模拟点击）
HAND_CARD_POSITIONS = {
    1: [(850, 800)],  # 1张手牌的位置
    2: [(750, 800), (950, 800)],  # 2张手牌的位置
    3: [(700, 800), (850, 800), (1050, 800)],  # 3张手牌的位置
    4: [(600, 800), (800, 800), (950, 800), (1100, 800)],  # 4张手牌的位置
    5: [(500, 800), (700, 800), (850, 800), (1000, 800), (1200, 800)],  # 5张手牌的位置
    6: [(450, 800), (600, 800), (780, 800), (950, 800), (1100, 800), (1250, 800)],  # 6张手牌的位置
    7: [(400, 800), (550, 800), (700, 800), (850, 800), (1000, 800), (1150, 800), (1300, 800)],  # 7张手牌的位置
    8: [(400, 800), (550, 800), (650, 800), (800, 800), (900, 800), (1050, 800), (1150, 800), (1300, 800)],  # 8张手牌的位置
    9: [(350, 800), (500, 800), (600, 800), (730, 800), (850, 800), (950, 800), (1050, 800), (1200, 800), (1350, 800)]  # 9张手牌的位置
}





def do_real_action(action, state):
    """
    根据AI输出的action字典，现实执行对应操作
    """
    action_type = action.get("action_type")
    if action_type == "play_card":
        play_card_action(action, state)
    elif action_type == "attack":
        attack_action(action, state)
    elif action_type == "evo":
        evo_action(action, state)
    elif action_type == "sevo":
        sevo_action(action, state)
    elif action_type == "end_turn":
        end_turn_action(action, state)
    else:
        print(f"⚠️ 未知动作类型: {action_type}")

def play_card_action(action, state):
    card_name = action.get("card_id")
    try:
        index = state.hand_card_ids.index(card_name)
    except ValueError:
        print(f"❌ 手牌中未找到卡牌：{card_name}")
        return None
    # 重新获取战场信息以确保手牌数量准确
    Get_b_i(state)
    count = state.hand_card_count
    positions = HAND_CARD_POSITIONS.get(count)
    if positions:
        positions = [[x + state.co[0], y + state.co[1]] for x,y in positions]  # 调整位置偏移
    if not positions:
        print(f"❌ 未知的手牌数量：{count}")
        return None
    if index >= len(positions):
        print(f"⚠️ 卡牌索引超出范围：{index}（手牌数量：{count}）")
        return None
    card_pos = positions[index]
    if card_pos is None:
        print("🚫 出牌失败：无法获取卡牌位置")
        return
    print(f"[出牌] 正在尝试出牌：{card_name}，位置：{card_pos}")
    # 右键点击卡牌
    pyautogui.moveTo(card_pos[0], card_pos[1], duration=0.1)
    pyautogui.rightClick()
    time.sleep(6)
    # ===== 特殊法术适配 =====
    if action is not None:
        # 死神挥镰
        if card_name == "死神挥镰":
            my_idx, enemy_idx = action.get("target_ids", [None, None])
            print(f"[死神挥镰] 选择目标：我方第{my_idx}号随从，敌方第{enemy_idx}号随从")
            # 点击我方目标随从
            if my_idx is not None and hasattr(state, "own_minion_positions") and my_idx < len(state.own_minion_positions):
                x1, y1, x2, y2 = state.own_minion_positions[my_idx]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                print(f"  → 点击我方随从{my_idx}中心点: ({cx}, {cy})")
                pyautogui.moveTo(cx, cy, duration=0.1)
                pyautogui.click()
                time.sleep(6)
            else:
                print(f"⚠️ 无效的我方随从索引: {my_idx}")
            # 点击敌方目标随从
            if enemy_idx is not None and hasattr(state, "opponent_minion_positions") and enemy_idx < len(state.opponent_minion_positions):
                x1, y1, x2, y2 = state.opponent_minion_positions[enemy_idx]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                print(f"  → 点击敌方随从{enemy_idx}中心点: ({cx}, {cy})")
                pyautogui.moveTo(cx, cy, duration=0.1)
                pyautogui.click()
                time.sleep(6)
            else:
                print(f"⚠️ 无效的敌方随从索引: {enemy_idx}")
            time.sleep(6)
        # 反转互换
        elif card_name == "反转互换":
            target_info = action.get("target_info", {})
            side = target_info.get("side")
            idx = target_info.get("index")
            print(f"[反转互换] 选择目标：{side}方第{idx}号随从")
            if side == "own":
                if idx is not None and hasattr(state, "own_minion_positions") and idx < len(state.own_minion_positions):
                    x1, y1, x2, y2 = state.own_minion_positions[idx]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    print(f"  → 点击我方随从{idx}中心点: ({cx}, {cy})")
                    pyautogui.moveTo(cx, cy, duration=0.1)
                    pyautogui.click()
                    time.sleep(6)
                else:
                    print(f"⚠️ 无效的我方随从索引: {idx}")
            elif side == "opponent":
                if idx is not None and hasattr(state, "opponent_minion_positions") and idx < len(state.opponent_minion_positions):
                    x1, y1, x2, y2 = state.opponent_minion_positions[idx]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    print(f"  → 点击敌方随从{idx}中心点: ({cx}, {cy})")
                    pyautogui.moveTo(cx, cy, duration=0.1)
                    pyautogui.click()
                    time.sleep(6)
                else:
                    print(f"⚠️ 无效的敌方随从索引: {idx}")
            else:
                print(f"⚠️ 未知side: {side}")
            time.sleep(6)
        # 蛇神的嗔怒
        elif card_name == "蛇神的嗔怒":
            target_info = action.get("target_info", {})
            side = target_info.get("side")
            idx = target_info.get("index")
            if side == "opponent":
                print(f"[蛇神的嗔怒] 选择目标：敌方第{idx}号随从")
                Get_b_i(state)  # 补全：点击前读取战场信息
                if idx is not None and hasattr(state, "opponent_minion_positions") and idx < len(state.opponent_minion_positions):
                    x1, y1, x2, y2 = state.opponent_minion_positions[idx]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    print(f"  → 点击敌方随从{idx}中心点: ({cx}, {cy})")
                    pyautogui.moveTo(cx, cy, duration=0.1)
                    pyautogui.click()
                    time.sleep(6)
                else:
                    print(f"⚠️ 无效的敌方随从索引: {idx}")
            elif side == "opponent_leader":
                print("[蛇神的嗔怒] 选择目标：敌方主战者")
                leader_x = 780 + state.co[0]
                leader_y = 110 + state.co[1]
                print(f"  → 点击敌方主战者中心点: ({leader_x}, {leader_y})")
                pyautogui.moveTo(leader_x, leader_y, duration=0.1)
                pyautogui.click()
                time.sleep(6)
            else:
                print(f"⚠️ 未知side: {side}")
            time.sleep(3)
    print("✔ 出牌完成")
    return


def attack_action(action, state):
    # 现实攻击操作
    attacker_id = action.get("card_id")
    attacker_index = action.get("attacker_index")
    targets = action.get("target_ids", [])
    print(f"[攻击] {attacker_id} -> {targets}")

    # 获取攻击者index
    if attacker_index is None or attacker_index < 0 or attacker_index >= state.own_minion_count:
        print(f"❌ 攻击者索引无效: {attacker_index}")
        return

    # 处理目标
    if not targets:
        print("⚠️ 无攻击目标，跳过")
        return

    target = targets[0]
    # 判断目标类型
    if isinstance(target, int):
        # 目标为敌方随从index
        target_index = target
    elif isinstance(target, str) and target.startswith("enemy_") and target[6:].isdigit():
        target_index = int(target[6:])
    elif target == "enemy_leader":
        target_index = -1  # 约定-1为攻击主战者
    else:
        print(f"⚠️ 未知目标类型: {target}")
        return

    if attacker_index < 0 or attacker_index >= state.own_minion_count:
        print(f"[错误] 攻击者索引无效: {attacker_index}")
        return

    # 获取攻击者位置：矩形区域 -> 取中心点
    attacker_rect = state.own_minion_positions[attacker_index]
    attacker_center = (
        (attacker_rect[0] + attacker_rect[2]) // 2,
        (attacker_rect[1] + attacker_rect[3]) // 2
    )

    # 判断目标是否为英雄
    if target_index == -1:
        # 攻击英雄
        hero_pos = (780 + state.co[0], 110 + state.co[1])
        target_center = hero_pos
        print(f"[攻击] {state.own_minion_ids[attacker_index]} 攻击敌方英雄")
    elif 0 <= target_index < state.opponent_minion_count:
        # 攻击敌方随从
        target_rect = state.opponent_minion_positions[target_index]
        target_center = (
            (target_rect[0] + target_rect[2]) // 2,
            (target_rect[1] + target_rect[3]) // 2
        )
        print(f"[攻击] {state.own_minion_ids[attacker_index]} 攻击敌人 [{target_index}]")
    else:
        print(f"[错误] 目标索引无效: {target_index}")
        return

    # 执行拖动攻击
    drag_attack(attacker_center, target_center)

def drag_attack(start_pos, end_pos):
    """
    模拟鼠标拖动攻击动作
    控制鼠标从起点拖拽到终点
    
    Args:
        start_pos: 起始位置 (x, y)
        end_pos: 结束位置 (x, y)
    """
    x1, y1 = start_pos
    x2, y2 = end_pos

    pyautogui.moveTo(x1, y1)
    pyautogui.mouseDown()
    pyautogui.moveTo(x2, y2, duration=0.5)  # 拖动动画持续时间
    pyautogui.mouseUp()

    print(f"拖动攻击完成: ({x1}, {y1}) → ({x2}, {y2})")
    time.sleep(3)


def evo_action(action, state):
    # 现实进化操作
    minion = action.get("card_id")
    attacker_index = action.get("attacker_index")
    print(f"[进化] {minion}")
    # 获取目标随从index
    idx = attacker_index
    if idx is None or idx < 0 or idx >= len(state.own_minion_ids):
        print(f"❌ 未找到进化目标 {minion} 的索引 {attacker_index} 在我方随从列表中")
        return
    # 获取目标随从中心点
    if hasattr(state, "own_minion_positions") and idx < len(state.own_minion_positions):
        x1, y1, x2, y2 = state.own_minion_positions[idx]
        target_x = (x1 + x2) // 2
        target_y = (y1 + y2) // 2
    else:
        print(f"⚠️ 无效的随从位置索引: {idx}")
        return
    # 能量图标坐标
    e_icon_x = 710 + state.co[0]
    e_icon_y = 695 + state.co[1]
    # 拖动能量到目标随从
    pyautogui.moveTo(e_icon_x, e_icon_y)
    pyautogui.mouseDown()
    pyautogui.moveTo(target_x, target_y, duration=0.2)
    pyautogui.mouseUp()
    # 进化后id前加'e'
    if not state.own_minion_ids[idx].startswith('e'):
        state.own_minion_ids[idx] = 'e' + state.own_minion_ids[idx]
    print(f"✔ 进化操作完成: 能量({e_icon_x},{e_icon_y}) → 随从{idx}({target_x},{target_y})")
    time.sleep(6)

def sevo_action(action, state):
    # 现实超进化操作
    minion = action.get("card_id")
    attacker_index = action.get("attacker_index")
    print(f"[超进化] {minion}")
    # 获取目标随从index
    idx = attacker_index
    if idx is None or idx < 0 or idx >= len(state.own_minion_ids):
        print(f"❌ 未找到超进化目标 {minion} 的索引 {attacker_index} 在我方随从列表中")
        return
    # 获取目标随从中心点
    if hasattr(state, "own_minion_positions") and idx < len(state.own_minion_positions):
        x1, y1, x2, y2 = state.own_minion_positions[idx]
        target_x = (x1 + x2) // 2
        target_y = (y1 + y2) // 2
    else:
        print(f"⚠️ 无效的随从位置索引: {idx}")
        return
    # 超进化能量图标坐标
    se_icon_x = 910 + state.co[0]
    se_icon_y = 695 + state.co[1]
    # 拖动能量到目标随从
    pyautogui.moveTo(se_icon_x, se_icon_y)
    pyautogui.mouseDown()
    pyautogui.moveTo(target_x, target_y, duration=0.2)
    pyautogui.mouseUp()
    # 超进化后id前加'e'
    if not state.own_minion_ids[idx].startswith('e'):
        state.own_minion_ids[idx] = 'e' + state.own_minion_ids[idx]
    print(f"✔ 超进化操作完成: 能量({se_icon_x},{se_icon_y}) → 随从{idx}({target_x},{target_y})")
    time.sleep(6)

def end_turn_action(action, state):
    print("[结束回合]")
    # 使用mouseDown/mouseUp模拟真实点击，提高稳定性
    pyautogui.mouseDown(1450 + state.co[0], 450 + state.co[1])
    time.sleep(0.5)
    pyautogui.mouseUp()

# 主复现函数
def replay_action_path(state, path, step_pause=False):
    for i, action in enumerate(path):
        print(f"\n第{i+1}步：{action}")
        Get_b_i(state)  # 每步都读取战场信息
        
        do_real_action(action, state)
        if step_pause:
            input("按回车执行下一步...")

# 你可以在main或其它入口调用
# best_path, state = exhaustive_ai_search(...)
# replay_action_path(state, best_path)