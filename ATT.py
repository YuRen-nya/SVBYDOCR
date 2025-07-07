# ATT.py
# 攻击执行模块
# 功能：处理游戏中的攻击逻辑，包括攻击评分、目标选择和攻击执行

import time
import pyautogui  # 控制鼠标拖动攻击
from GameState import GameState
from GameState import Get_b_i


def is_special_minion(index, state: GameState):
    """
    判断是否是特殊角色
    特殊角色（如千金、美杜莎）有特殊的攻击评分机制
    
    Args:
        index: 随从索引
        state: 游戏状态对象
    
    Returns:
        bool: 是否为特殊角色
    """
    return state.own_minion_ids[index] in ['千金', 'e千金', '美杜莎', 'e美杜莎']


def calculate_score(attacker_index, enemy_index, state: GameState):
    """
    计算非守护单位的攻击评分
    用于评估攻击某个敌方随从的价值
    
    Args:
        attacker_index: 攻击者索引
        enemy_index: 敌方随从索引
        state: 游戏状态对象
    
    Returns:
        int: 攻击评分
    """
    if enemy_index < 0 or enemy_index >= state.opponent_minion_count:
        return 0

    enemy_atk = state.opponent_minion_attack[enemy_index]
    enemy_hp = state.opponent_minion_health[enemy_index]
    attacker_atk = state.own_minion_attack[attacker_index]

    if is_special_minion(attacker_index, state):
        # 特殊角色：攻击力+生命值
        return enemy_atk + enemy_hp
    elif enemy_hp < attacker_atk:
        # 能击杀目标：攻击力+生命值
        return enemy_atk + enemy_hp
    else:
        # 无法击杀：无价值
        return 0


def calculate_dash_score(attacker_index, enemy_index, state: GameState):
    """
    Dash 随从专属评分（包括英雄）
    Dash随从可以攻击英雄，有特殊的评分机制
    
    Args:
        attacker_index: 攻击者索引
        enemy_index: 敌方随从索引（-1表示攻击英雄）
        state: 游戏状态对象
    
    Returns:
        int: 攻击评分
    """
    if enemy_index == -1:
        # 攻击英雄：攻击力的平方 * 0.5
        return state.own_minion_attack[attacker_index] ** 2 * 0.5
    else:
        # 攻击随从：使用普通评分
        return calculate_score(attacker_index, enemy_index, state)


def perform_attack_drag(state: GameState, attacker_index, target_index):
    """
    执行一次拖动攻击动作
    控制鼠标从攻击者位置拖拽到目标位置
    
    Args:
        state: 当前游戏状态对象
        attacker_index: 我方随从索引
        target_index: 敌方随从索引 或 -1 表示攻击英雄
    """
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
    time.sleep(0.5)  # 等待动画完成


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
    pyautogui.moveTo(x2, y2, duration=0.2)  # 拖动动画持续时间
    pyautogui.mouseUp()

    print(f"拖动攻击完成: ({x1}, {y1}) → ({x2}, {y2})")


def find_best_attacker_for_target(target_index, attacker_indices, state):
    """
    在指定的攻击者中寻找最佳攻击者（用于攻击指定的目标）
    优先选择特殊角色，然后选择能击杀目标的最小攻击力随从
    
    Args:
        target_index: 目标索引（敌方随从）
        attacker_indices: 可选攻击者索引列表（如 rush 或 dash）
        state: 游戏状态
    
    Returns:
        int: 最佳攻击者索引或 None
    """
    target_hp = state.opponent_minion_health[target_index]
    scores = []

    for idx in attacker_indices:
        atk = state.own_minion_attack[idx]
        if is_special_minion(idx, state):
            # 特殊角色评分
            score = target_hp + atk
        elif atk > target_hp:
            # 能击杀目标
            score = target_hp + atk
        else:
            # 无法击杀
            score = 0
        scores.append((score, idx))

    # 排序：先选特殊角色，再选攻击力大于目标血量中最小攻击力的，最后选攻击力最大的
    scores.sort(key=lambda x: (-x[0], x[1]))
    return scores[0][1] if scores and scores[0][0] > 0 else None

def should_exit_attack_loop(state, remaining_rush, remaining_dash):
    """
    判断是否应该退出攻击循环
    
    Args:
        state: 游戏状态对象
        remaining_rush: 剩余可攻击的rush随从列表
        remaining_dash: 剩余可攻击的dash随从列表
    
    Returns:
        bool: 是否应该退出攻击循环
    """
    # 情况一：没有任何 rush/dash 随从还能攻击
    if not remaining_rush and not remaining_dash:
        # 并且敌方场上也没有随从（即没有目标）
        if state.opponent_minion_count == 0:
            print("[INFO] 没有随从可攻击，且敌方无随从，准备退出")
            return True
        else:
            # 敌方还有随从，但当前随从都无法攻击（可能是血量/机制问题）
            print("[INFO] 所有随从都已无法攻击，但敌方仍有随从，尝试结束攻击流程")
            return True
    return False

def perform_full_attack(state: GameState):
    """
    主攻击流程：每次攻击前重新读场，并选择最佳攻击目标。
    不再使用 used_targets，每次攻击都基于最新场上状态进行判断。
    
    攻击优先级：
    1. 优先攻击守护随从（最大生命值）
    2. Rush随从攻击非守护随从
    3. Dash随从攻击非守护随从或英雄
    
    Args:
        state: 游戏状态对象
    """
    # 保存那些在之前轮次中没有可攻击目标的随从索引
    no_target_attacker_indices = set()

    while True:
        # ====== 每次攻击前重新读场 ======
        Get_b_i(state)

        # 构建 Rush/Dash 列表（不包含 normal）
        own_rush = [i for i in range(state.own_minion_count) if state.own_minion_follows[i] == 'rush']
        own_dash = [i for i in range(state.own_minion_count) if state.own_minion_follows[i] == 'dash']

        # 当前轮次中未被标记"无目标"的 rush 和 dash 随从
        current_rush = [i for i in own_rush if i not in no_target_attacker_indices]
        current_dash = [i for i in own_dash if i not in no_target_attacker_indices]

        # ====== Step 1: 判断是否存在守护随从 ======
        guard_indices = [
            i for i in range(state.opponent_minion_count)
            if state.opponent_minion_taunt[i]
        ]

        if guard_indices:
            print("[INFO] 发现守护随从，优先攻击最大生命值随从")

            # 找出最大生命值的守护随从
            max_hp_guard = max(guard_indices,
                               key=lambda i: state.opponent_minion_health[i])

            # 尝试用 Rush 攻击
            best_attacker = find_best_attacker_for_target(max_hp_guard, current_rush, state)
            if best_attacker is not None:
                perform_attack_drag(state, best_attacker, max_hp_guard)
                continue

            # 再尝试用 Dash 攻击
            best_attacker = find_best_attacker_for_target(max_hp_guard, current_dash, state)
            if best_attacker is not None:
                perform_attack_drag(state, best_attacker, max_hp_guard)
                continue

            print("[INFO] 没有合适的攻击者可以攻击守护随从")
            break  # 没有攻击者可攻击守护随从，跳出循环

        else:
            print("[INFO] 当前无守护随从，开始攻击非守护目标")

            # 收集所有非守护敌人 + 英雄（仅 dash 可选）
            non_guard_enemies = [
                i for i in range(state.opponent_minion_count)
                if not state.opponent_minion_taunt[i]
            ]

            # ====== Step 2: 处理 Rush 随从 ======
            for attacker_index in current_rush:
                # 计算攻击每个非守护敌人的评分
                scores = [(calculate_score(attacker_index, e, state), e) for e in non_guard_enemies]
                scores.sort(reverse=True)
                if scores and scores[0][0] > 0:
                    # 有可攻击目标，执行攻击
                    _, best_enemy = scores[0]
                    perform_attack_drag(state, attacker_index, best_enemy)
                else:
                    # 没有可攻击目标，记录该随从
                    no_target_attacker_indices.add(attacker_index)
                    print(f"[记录] 随从 {attacker_index} 没有可攻击目标（Rush）")

            # ====== Step 3: 处理 Dash 随从 ======
            targets = non_guard_enemies + [-1]  # 包括英雄
            for attacker_index in current_dash:
                # 计算攻击每个目标（包括英雄）的评分
                scores = [(calculate_dash_score(attacker_index, t, state), t) for t in targets]
                scores.sort(reverse=True)
                if scores and scores[0][0] > 0:
                    # 有可攻击目标，执行攻击
                    _, best_target = scores[0]
                    perform_attack_drag(state, attacker_index, best_target)
                else:
                    # 没有可攻击目标，记录该随从
                    no_target_attacker_indices.add(attacker_index)
                    print(f"[记录] 随从 {attacker_index} 没有可攻击目标（Dash）")

            # ====== Step 4: 检查是否还有可攻击的随从 ======
            remaining_rush = [i for i in own_rush if i not in no_target_attacker_indices]
            remaining_dash = [i for i in own_dash if i not in no_target_attacker_indices]

            # ====== Step 4: 检查是否应该退出攻击循环 ======
            if should_exit_attack_loop(state, remaining_rush, remaining_dash):
                break

    print("[INFO] 攻击阶段完成")