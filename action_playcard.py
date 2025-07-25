import pyautogui
import time
from GameState import Get_b_i

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
    action_type = action.get("type")
    if action_type.startswith("Play_Card"):
        play_card_action(action, state)
    elif action_type == "activate_card":
        activate_card_action(action, state)
    elif action_type == "attack":
        attack_action(action, state)
    elif action_type == "evo":
        evo_action(action, state)
    elif action_type == "sevo":
        sevo_action(action, state)
    elif action_type == "end_turn":
        end_turn_action(action, state)

def play_card_action(action, state):
    card_name = action.get("card_id")
    index = action.get("card_index")
    count = state.hand_card_count
    positions = HAND_CARD_POSITIONS.get(count)
    if positions:
        positions = [[x + state.co[0], y + state.co[1]] for x,y in positions]  # 调整位置偏移
    if index >= len(positions):
        print(f"⚠️ 卡牌索引超出范围：{index}（手牌数量：{count}）")
        return None
    card_pos = positions[index]
    pyautogui.moveTo(card_pos[0], card_pos[1], duration=0.1)
    pyautogui.rightClick()
    print(f"使用卡牌：{card_name}，索引：{index}，位置：{card_pos}")
    time.sleep(1)
    targets = action.get("targets")
    if targets != [None]:
        for target in targets:
            if target == "own_leader":
                pyautogui.moveTo(state.co[0], state.co[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target == "opponent_leader":
                pyautogui.moveTo(780+state.co[0], 110+state.co[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target.startswith("own_minion_"):
                idx = int(target.split("_")[2])
                minion_rect = state.own_minion_positions[idx]
                minion_center = (
                    (minion_rect[0] + minion_rect[2]) // 2,
                    (minion_rect[1] + minion_rect[3]) // 2
                )
                pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target.startswith("opponent_minion_"):
                idx = int(target.split("_")[2])
                minion_rect = state.opponent_minion_positions[idx]
                minion_center = (
                    (minion_rect[0] + minion_rect[2]) // 2,
                    (minion_rect[1] + minion_rect[3]) // 2
                )
                pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target == None:
                pass
            print(f"目标：{target}")
    time.sleep(3)

def activate_card_action(action, state):
    card_name = action.get("card_id")
    index = action.get("activate_index")
    minion_rect = state.own_minion_positions[index]
    minion_center = (
        (minion_rect[0] + minion_rect[2]) // 2,
        (minion_rect[1] + minion_rect[3]) // 2
    )
    pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.1)
    pyautogui.rightClick()
    print(f"激活卡牌：{card_name}，索引：{index}")
    time.sleep(1)
    if action.get("targets") != None:
        for target in action.get("targets"):
            if target == "own_leader":
                pyautogui.moveTo(state.co[0], state.co[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target == "opponent_leader":
                pyautogui.moveTo(780+state.co[0], 110+state.co[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target.startswith("own_minion_"):
                idx = int(target.split("_")[2])
                minion_rect = state.own_minion_positions[idx]
                minion_center = (
                    (minion_rect[0] + minion_rect[2]) // 2,
                    (minion_rect[1] + minion_rect[3]) // 2
                )
                pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            elif target.startswith("opponent_minion_"):
                idx = int(target.split("_")[2])
                minion_rect = state.opponent_minion_positions[idx]
                minion_center = (
                    (minion_rect[0] + minion_rect[2]) // 2,
                    (minion_rect[1] + minion_rect[3]) // 2
                )
                pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.1)
                pyautogui.leftClick()
                time.sleep(2)
            print(f"目标：{target}")
    time.sleep(3)

def attack_action(action, state):
    card_name = action.get("card_id")
    index = action.get("attacker_index")
    attacker_rect = state.own_minion_positions[index]
    attacker_center = (
        (attacker_rect[0] + attacker_rect[2]) // 2,
        (attacker_rect[1] + attacker_rect[3]) // 2
    )
    targets = action.get("target")
    print(f"攻击：{card_name}，索引：{index}，坐标：{attacker_center}，目标：{targets}")
    pyautogui.moveTo(state.co[0]+attacker_center[0], state.co[1]+attacker_center[1], duration=0.1)
    pyautogui.mouseDown()
    if targets == "opponent_leader":
        pyautogui.moveTo(780+state.co[0], 110+state.co[1], duration=0.5)
        pyautogui.mouseUp()
        time.sleep(2)
    elif targets.startswith("opponent_minion_"):
        idx = int(targets.split("_")[2])
        minion_rect = state.opponent_minion_positions[idx]
        minion_center = (
            (minion_rect[0] + minion_rect[2]) // 2,
            (minion_rect[1] + minion_rect[3]) // 2
        )
        pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.5)
        pyautogui.mouseUp()
        time.sleep(2)
    elif targets == None:
        pyautogui.mouseUp()
        time.sleep(3)
    print(f"攻击完成：{card_name}，索引：{index}，目标：{targets}")

def evo_action(action, state):
    card_name = action.get("card_id")
    index = action.get("evo_index")
    minion_rect = state.own_minion_positions[index]
    minion_center = (
        (minion_rect[0] + minion_rect[2]) // 2,
        (minion_rect[1] + minion_rect[3]) // 2
    )
    e_icon_x = 710 + state.co[0]
    e_icon_y = 695 + state.co[1]
    pyautogui.moveTo(e_icon_x, e_icon_y, duration=0.1)
    pyautogui.mouseDown()
    pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.2)
    pyautogui.mouseUp()
    state.own_minion_ids[index] = 'e' + state.own_minion_ids[index]
    state.own_minion_evo[index] = "evo"
    print(f"进化完成：{card_name}，索引：{index}")
    time.sleep(6)

def sevo_action(action, state):
    card_name = action.get("card_id")
    index = action.get("sevo_index")
    minion_rect = state.own_minion_positions[index]
    minion_center = (
        (minion_rect[0] + minion_rect[2]) // 2,
        (minion_rect[1] + minion_rect[3]) // 2
    )
    se_icon_x = 910 + state.co[0]
    se_icon_y = 695 + state.co[1]
    pyautogui.moveTo(se_icon_x, se_icon_y, duration=0.1)
    pyautogui.mouseDown()
    pyautogui.moveTo(state.co[0]+minion_center[0], state.co[1]+minion_center[1], duration=0.2)
    pyautogui.mouseUp()
    state.own_minion_ids[index] = 'e' + state.own_minion_ids[index]
    state.own_minion_evo[index] = "sevo"
    print(f"超进化完成：{card_name}，索引：{index}")
    time.sleep(6)

def end_turn_action(action, state):
    print("[结束回合]")
    pyautogui.mouseDown(1450 + state.co[0], 450 + state.co[1])
    time.sleep(0.2)
    pyautogui.mouseUp()

def replay_action_path(state, path, step_pause=False):
    for i, action in enumerate(path):
        print(f"\n第{i+1}步：{action}")
        Get_b_i(state)
        do_real_action(action, state)
        if step_pause:
            input("按回车执行下一步...")
# 示例用法
# for path, final_state in results:
#     print("==== 回放一条动作路径 ====")
#     replay_action_path(state, path, step_pause=True)  # 或 False


