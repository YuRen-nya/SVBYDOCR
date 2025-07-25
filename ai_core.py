from action_de import actions_d
import re
import itertools
import random
import time

def enumerate_all_possible_actions(state):
    """
    枚举当前状态下所有可执行动作，返回动作字典列表。

    主要流程：
    1. 枚举所有手牌的出牌动作（支持多目标、特殊出牌方式，自动处理优先级和目标模式）。
    2. 枚举所有己方随从的攻击动作。
    3. 枚举所有己方随从的进化/超进化动作（支持多目标，目标模式与出牌一致）。
    4. 添加“结束回合”动作。

    返回值：
        actions_list: List[dict]
        每个元素为一个动作字典，结构如下：

        # 出牌动作（多目标）
        {
            "type": "Play_Card" 或 "Play_Card_1_burst" 等,  # 出牌类型
            "card_id": "卡牌名",
            "card_index": 卡牌索引,
            "cost": 费用,
            "value": 数值,
            "targets": [target1, target2, ...],  # 多目标，顺序与 play_target_n 一致
            "priority": 0,  # 优先级（如有）
            # 其它可选字段
        }

        # 主动技能
        {
            "type": "activate_card",
            "card_id": "随从id",
            "activate_index": 随从在己方场上的索引,
            "targets": [target1, target2, ...]  # 多目标，顺序与 activate_target_n 一致
        }
        # 随从攻击动作
        {
            "type": "attack",
            "card_id": "随从id",
            "target":  "opponent_leader" / "opponent_minion_n" / None,
            "attacker_index": 0,  # 随从在己方场上的索引
        }

        # 进化/超进化动作（多目标）
        {
            "type": "evo" 或 "sevo",
            "card_id": "随从id",
            "evo_index" 或 "sevo_index": idx,  # 随从在己方场上的索引
            "targets": [target1, target2, ...]  # 多目标，顺序与 evo_target_n/sevo_target_n 一致
        }

        # 结束回合动作
        {
            "type": "end_turn"
        }

    目标命名统一为：
        - "own_leader"：我方主战者
        - "own_minion_n"：我方第n号随从
        - "opponent_leader"：对方主战者
        - "opponent_minion_n"：对方第n号随从
        - None：无目标（如允许无目标时）

    """
    
    actions_list = []

    # 1. 手牌出牌
    # 1.1 判断是否收录
    # 1.2 判断是否可以出牌，有没有特殊出牌方式
    # 1.3 判断费用是否足够
    # 1.4 判断是否可以无目标出牌
    # 1.5 判断是否有目标，如果有，枚举所有目标
    # 1.6 只保留优先级最高的出牌方式
    for card in state.hand_card_ids:
        card_info = actions_d.get(card)
        if not card_info:
            continue # 跳过未收录的卡牌

        # 找出所有 Play_Card 相关 key
        play_card_keys = [k for k in card_info if k.startswith("Play_Card")]
        if not play_card_keys:
            continue # 跳过没有出牌方式的卡牌

        play_card_action_list = []

        for playcard_key in play_card_keys:
            play_card_info = card_info[playcard_key]
            play_target_mode = play_card_info.get("target_mode", "ordered_unique")
            play_card_index = state.hand_card_ids.index(card)
            play_cost = play_card_info.get("play_cost")
            play_value = play_card_info.get("play_value")
            if play_cost is None or play_cost > state.mana:
                continue # 跳过费用不足的卡牌

            # 用正则提取优先级和类型
            m = re.match(r"Play_Card(?:_(\d+))?(_[a-zA-Z]+)?", playcard_key)
            priority = int(m.group(1)) if m and m.group(1) else 0
            type_suffix = m.group(2) if m and m.group(2) else ""

            # 特殊条件检定
            if type_suffix == "_burst":
                burst_cost = play_card_info.get("burst_cost")
                if burst_cost is not None and  burst_cost > state.e_value:
                    continue # 跳过爆能值不足的卡牌
            elif type_suffix == "_necro":
                necro_cost = play_card_info.get("necro_cost")
                if necro_cost is not None and necro_cost > state.graveyard_count:
                    continue # 跳过死灵术值不足的卡牌
            # 你可以继续添加更多特殊条件分支...

            # 1. 收集所有 play_target_* 字段
            play_target_keys = [k for k in play_card_info if k.startswith("play_target")]
            play_target_keys.sort()  # 保证顺序一致

            # 2. 枚举每个目标位的所有可能目标
            all_target_options = []
            for key in play_target_keys:
                target_dict = play_card_info[key]
                options = []
                if target_dict.get("target_area1"):
                    options.append("own_leader")
                if target_dict.get("target_area2"):
                    for idx in range(state.own_minion_count):
                        options.append(f"own_minion_{idx}")
                if target_dict.get("target_area3"):
                    options.append("opponent_leader")
                if target_dict.get("target_area4"):
                    for idx in range(state.opponent_minion_count):
                        options.append(f"opponent_minion_{idx}")
                # 如果没有目标且允许无目标
                if not options and play_card_info.get("play_less_target_use_able", False):
                    options.append(None)
                all_target_options.append(options)

            # 3. 根据 target_mode 枚举所有目标组合
            target_mode = play_card_info.get("target_mode", "ordered_unique")
            if not all_target_options:
                continue  # 没有目标位，跳过

            if target_mode == "ordered_unique":
                # 有序不可重复
                for targets in itertools.product(*all_target_options):
                    if len(set(targets)) == len(targets):  # 不可重复
                        actions_list.append({
                            "type": "Play_Card",
                            "card_id": card,
                            "card_index": play_card_index,
                            "cost": play_cost,
                            "value": play_value,
                            "targets": list(targets)
                        })
            elif target_mode == "ordered_repeat":
                # 有序可重复
                for targets in itertools.product(*all_target_options):
                    actions_list.append({
                        "type": "Play_Card",
                        "card_id": card,
                        "card_index": play_card_index,
                        "cost": play_cost,
                        "value": play_value,
                        "targets": list(targets)
                    })
            elif target_mode == "unordered_unique":
                # 无序不可重复
                seen = set()
                for targets in itertools.product(*all_target_options):
                    tset = frozenset(targets)
                    if len(set(targets)) == len(targets) and tset not in seen:
                        seen.add(tset)
                        actions_list.append({
                            "type": "Play_Card",
                            "card_id": card,
                            "cost": play_cost,
                            "value": play_value,
                            "targets": list(targets)
                        })
            elif target_mode == "unordered_repeat":
                # 无序可重复
                seen = set()
                for targets in itertools.product(*all_target_options):
                    tset = frozenset(targets)
                    if tset not in seen:
                        seen.add(tset)
                        actions_list.append({
                            "type": "Play_Card",
                            "card_id": card,
                            "card_index": play_card_index,
                            "cost": play_cost,
                            "value": play_value,
                            "targets": list(targets)
                        })
            else:
                # 默认有序不可重复
                for targets in itertools.product(*all_target_options):
                    if len(set(targets)) == len(targets):
                        actions_list.append({
                            "type": "Play_Card",
                            "card_id": card,
                            "card_index": play_card_index,
                            "cost": play_cost,
                            "value": play_value,
                            "targets": list(targets)
                        })

        # 只保留优先级最高的出牌方式
        if play_card_action_list:
            max_priority = max(a["priority"] for a in play_card_action_list)
            for action in play_card_action_list:
                if action["priority"] == max_priority:
                    actions_list.append(action)
    
    # 2 主动技能（Activate_Card）
    for idx, minion_id in enumerate(getattr(state, 'own_minion_ids', [])):
        card_info = actions_d.get(minion_id)
        if not card_info:
            continue
        activate_card = card_info.get("Activate_Card")
        if not activate_card:
            continue

        # 支持多目标
        activate_target_keys = [k for k in activate_card if k.startswith("activate_target")]
        activate_target_keys.sort()
        all_target_options = []
        for key in activate_target_keys:
            target_dict = activate_card[key]
            options = []
            if target_dict.get("target_area1"):
                options.append("own_leader")
            if target_dict.get("target_area2"):
                for i in range(state.own_minion_count):
                    options.append(f"own_minion_{i}")
            if target_dict.get("target_area3"):
                options.append("opponent_leader")
            if target_dict.get("target_area4"):
                for i in range(state.opponent_minion_count):
                    options.append(f"opponent_minion_{i}")
            if not options:
                options.append(None)
            all_target_options.append(options)

        activate_target_mode = activate_card.get("target_mode", "ordered_unique")
        if not all_target_options:
            continue

        if activate_target_mode == "ordered_unique":
            for targets in itertools.product(*all_target_options):
                if len(set(targets)) == len(targets):
                    actions_list.append({
                        "type": "activate_card",
                        "card_id": minion_id,
                        "activate_index": idx,
                        "targets": list(targets)
                    })
        elif activate_target_mode == "ordered_repeat":
            for targets in itertools.product(*all_target_options):
                actions_list.append({
                    "type": "activate_card",
                    "card_id": minion_id,
                    "activate_index": idx,
                    "targets": list(targets)
                })
        elif activate_target_mode == "unordered_unique":
            seen = set()
            for targets in itertools.product(*all_target_options):
                tset = frozenset(targets)
                if len(set(targets)) == len(targets) and tset not in seen:
                    seen.add(tset)
                    actions_list.append({
                        "type": "activate_card",
                        "card_id": minion_id,
                        "activate_index": idx,
                        "targets": list(targets)
                    })
        elif activate_target_mode == "unordered_repeat":
            seen = set()
            for targets in itertools.product(*all_target_options):
                tset = frozenset(targets)
                if tset not in seen:
                    seen.add(tset)
                    actions_list.append({
                        "type": "activate_card",
                        "card_id": minion_id,
                        "activate_index": idx,
                        "targets": list(targets)
                    })
        else:
            for targets in itertools.product(*all_target_options):
                if len(set(targets)) == len(targets):
                    actions_list.append({
                        "type": "activate_card",
                        "card_id": minion_id,
                        "activate_index": idx,
                        "targets": list(targets)
                    })

    # 3 随从攻击
    for idx, minion_id in enumerate(getattr(state, 'own_minion_ids', [])):
        follow_type = state.own_minion_follows[idx] if idx < len(state.own_minion_follows) else None
        taunt_targets = [i for i, t in enumerate(getattr(state, 'opponent_minion_taunt', [])) if t]
        opponent_minion_ids = [f"opponent_minion_{i}" for i in range(getattr(state, 'opponent_minion_count', 0))]
        opponent_leader = "opponent_leader"
        own_leader = "own_leader"
        own_minion_ids = [f"own_minion_{i}" for i in range(getattr(state, 'own_minion_count', 0))]
        if follow_type == "rush":
            if taunt_targets:
                targets = [opponent_minion_ids[i] for i in taunt_targets]
            else:
                targets = opponent_minion_ids
            for target in targets:
                actions_list.append({
                    "type": "attack",
                    "card_id": minion_id,
                    "target": target,
                    "attacker_index": idx
                })
            # 可以加上无目标攻击防止循环
            actions_list.append({
                "type": "attack",
                "card_id": minion_id,
                "target": None,
                "attacker_index": idx
            })
        elif follow_type == "dash":
            if taunt_targets:
                targets = [opponent_minion_ids[i] for i in taunt_targets]
            else:
                targets = opponent_minion_ids + [opponent_leader]
            for target in targets:
                actions_list.append({
                    "type": "attack",
                    "card_id": minion_id,
                    "target": target,
                    "attacker_index": idx
                })
            actions_list.append({
                "type": "attack",
                "card_id": minion_id,
                "target": None,
                "attacker_index": idx
            })
    

    # 4 进化/超进化
    # 4.1 判断是否有进化机会
    # 4.2 判断是否在字典中
    # 4.3 判断是否可以进化
    # 4.4 判断是否有目标，如果有，枚举所有目标
    if not getattr(state, "evo_or_sevo_used", False):
        for idx, minion_id in enumerate(getattr(state, 'own_minion_ids', [])):
            card_info = actions_d.get(minion_id)
            if not card_info:
                continue

            # ===== 进化 =====
            evo_card = card_info.get("Evo_Card")
            if evo_card and evo_card.get("evo_able", True) and getattr(state, 'e_value', 0) > 0:
                # 支持多目标
                evo_target_keys = [k for k in evo_card if k.startswith("evo_target")]
                evo_target_keys.sort()
                all_target_options = []
                for key in evo_target_keys:
                    target_dict = evo_card[key]
                    options = []
                    if target_dict.get("target_area1"):
                        options.append("own_leader")
                    if target_dict.get("target_area2"):
                        for i in range(state.own_minion_count):
                            options.append(f"own_minion_{i}")
                    if target_dict.get("target_area3"):
                        options.append("opponent_leader")
                    if target_dict.get("target_area4"):
                        for i in range(state.opponent_minion_count):
                            options.append(f"opponent_minion_{i}")
                    if not options:
                        options.append(None)
                    all_target_options.append(options)

                evo_target_mode = evo_card.get("target_mode", "ordered_unique")
                if not all_target_options:
                    continue

                if evo_target_mode == "ordered_unique":
                    for targets in itertools.product(*all_target_options):
                        if len(set(targets)) == len(targets):
                            actions_list.append({
                                "type": "evo",
                                "card_id": minion_id,
                                "evo_index": idx,
                                "targets": list(targets)
                            })
                elif evo_target_mode == "ordered_repeat":
                    for targets in itertools.product(*all_target_options):
                        actions_list.append({
                            "type": "evo",
                            "card_id": minion_id,
                            "evo_index": idx,
                            "targets": list(targets)
                        })
                elif evo_target_mode == "unordered_unique":
                    seen = set()
                    for targets in itertools.product(*all_target_options):
                        tset = frozenset(targets)
                        if len(set(targets)) == len(targets) and tset not in seen:
                            seen.add(tset)
                            actions_list.append({
                                "type": "evo",
                                "card_id": minion_id,
                                "evo_index": idx,
                                "targets": list(targets)
                            })
                elif evo_target_mode == "unordered_repeat":
                    seen = set()
                    for targets in itertools.product(*all_target_options):
                        tset = frozenset(targets)
                        if tset not in seen:
                            seen.add(tset)
                            actions_list.append({
                                "type": "evo",
                                "card_id": minion_id,
                                "evo_index": idx,
                                "targets": list(targets)
                            })
                else:
                    # 默认有序不可重复
                    for targets in itertools.product(*all_target_options):
                        if len(set(targets)) == len(targets):
                            actions_list.append({
                                "type": "evo",
                                "card_id": minion_id,
                                "evo_index": idx,
                                "targets": list(targets)
                            })

            # ===== 超进化 =====
            sevo_card = card_info.get("Sevo_Card")
            if sevo_card and sevo_card.get("sevo_able", True) and getattr(state, 'se_value', 0) > 0:
                sevo_target_keys = [k for k in sevo_card if k.startswith("sevo_target")]
                sevo_target_keys.sort()
                all_target_options = []
                for key in sevo_target_keys:
                    target_dict = sevo_card[key]
                    options = []
                    if target_dict.get("target_area1"):
                        options.append("own_leader")
                    if target_dict.get("target_area2"):
                        for i in range(state.own_minion_count):
                            options.append(f"own_minion_{i}")
                    if target_dict.get("target_area3"):
                        options.append("opponent_leader")
                    if target_dict.get("target_area4"):
                        for i in range(state.opponent_minion_count):
                            options.append(f"opponent_minion_{i}")
                    if not options:
                        options.append(None)
                    all_target_options.append(options)

                sevo_target_mode = sevo_card.get("target_mode", "ordered_unique")
                if not all_target_options:
                    continue

                if sevo_target_mode == "ordered_unique":
                    for targets in itertools.product(*all_target_options):
                        if len(set(targets)) == len(targets):
                            actions_list.append({
                                "type": "sevo",
                                "card_id": minion_id,
                                "sevo_index": idx,
                                "targets": list(targets)
                            })
                elif sevo_target_mode == "ordered_repeat":
                    for targets in itertools.product(*all_target_options):
                        actions_list.append({
                            "type": "sevo",
                            "card_id": minion_id,
                            "sevo_index": idx,
                            "targets": list(targets)
                        })
                elif sevo_target_mode == "unordered_unique":
                    seen = set()
                    for targets in itertools.product(*all_target_options):
                        tset = frozenset(targets)
                        if len(set(targets)) == len(targets) and tset not in seen:
                            seen.add(tset)
                            actions_list.append({
                                "type": "sevo",
                                "card_id": minion_id,
                                "sevo_index": idx,
                                "targets": list(targets)
                            })
                elif sevo_target_mode == "unordered_repeat":
                    seen = set()
                    for targets in itertools.product(*all_target_options):
                        tset = frozenset(targets)
                        if tset not in seen:
                            seen.add(tset)
                            actions_list.append({
                                "type": "sevo",
                                "card_id": minion_id,
                                "sevo_index": idx,
                                "targets": list(targets)
                            })
                else:
                    for targets in itertools.product(*all_target_options):
                        if len(set(targets)) == len(targets):
                            actions_list.append({
                                "type": "sevo",
                                "card_id": minion_id,
                                "sevo_index": idx,
                                "targets": list(targets)
                            })
    # 5 结束回合
    actions_list.append({
        "type": "end_turn"
    })
    return actions_list

def execute_action(action, state):
    if action["type"].startswith("Play_Card"):
        return execute_play_card(action, state)
    elif action["type"] == "activate_card":
        return execute_activate_card(action, state)
    elif action["type"] == "attack":
        return execute_attack(action, state)
    elif action["type"] == "evo":
        return execute_evo(action, state)
    elif action["type"] == "sevo":
        return execute_sevo(action, state)
    elif action["type"] == "end_turn":
        return execute_end_turn(action, state)

def execute_play_card(action, state):
    mana_cost = action.get("cost", 0)
    state.mana -= mana_cost
    if state.mana < 0:
        state.mana = 0
    if action["value"] != 0:
        if len(state.own_minion_ids) < 5:
            state.own_minion_count += 1
            state.own_minion_ids.append(action["card_id"])
            state.own_minion_attack.append(action["value"]//100)
            state.own_minion_health.append(action["value"]%100)
            state.own_minion_evo.append("normal")
            state.own_minion_evo_rush.append(True)
            keywords = actions_d[action["card_id"]].get("Const_Card", {}).get("keywords", [])
            if "rush" in keywords:
                state.own_minion_follows.append("rush")
            elif "dash" in keywords:
                state.own_minion_follows.append("dash")
            else:
                state.own_minion_follows.append("normal")
    execute_play_card_special(action, state)
    state.hand_card_ids.pop(action["card_index"])
    state.hand_card_count -= 1
    return state

def execute_play_card_special(action, state):
    if action["card_id"] == "死神挥镰":
        target_info_1 = action.get("targets", {})[0]
        target_info_2 = action.get("targets", {})[1]
        own_minion_die(state, target_info_1)
        opponent_minion_die(state, target_info_2)

    if action["card_id"] == "反转互换":
        target_info = action.get("targets", {})[0]
        if isinstance(target_info, str) and target_info.startswith("own_minion_"):
            idx = int(target_info.split("_")[-1])
            state.own_minion_attack[idx] += 2
            state.own_minion_health[idx] -= 2
            if state.own_minion_health[idx] < 0:
                own_minion_die(state, idx)
        elif isinstance(target_info, str) and target_info.startswith("opponent_minion_"):
            idx = int(target_info.split("_")[-1])
            state.opponent_minion_attack[idx] += 2
            state.opponent_minion_health[idx] -= 2
            if state.opponent_minion_health[idx] < 0:
                opponent_minion_die(state, idx)

    elif action["card_id"] == "凶恶的小木乃伊":
        if action["type"].endswith("necro"):
            state.own_minion_follows[-1] = "dash"
    
    elif action["card_id"] == "夢魔‧維莉":
        state.player_hp -= 3
    
    elif action["card_id"] == "蛇神的嗔怒":
        target_info = action.get("targets", {})[0]
        if target_info == "opponent_leader":
            state.opponent_hp -= 3
        elif isinstance(target_info, str) and target_info.startswith("opponent_minion_"):
            idx = int(target_info.split("_")[-1])
            state.opponent_minion_health[idx] -= 3
            if state.opponent_minion_health[idx] <= 0:
                opponent_minion_die(state, idx)
        state.player_hp -= 2

    elif action["card_id"] == "役使蝙蝠":
        for _ in range(2):
            if len(state.own_minion_ids) < 5:
                state.own_minion_count += 1
                state.own_minion_ids.append("蝙蝠")
                state.own_minion_attack.append(1)
                state.own_minion_health.append(1)
                state.own_minion_follows.append("normal")
                state.own_minion_evo.append("normal")
                state.own_minion_evo_rush.append(True)
    
    elif action["card_id"] == "暗夜鬼人":
        state.player_hp -= 1
    
    elif action["card_id"] == "法外的賞金獵人‧巴爾特":
        state.player_hp -= 1
        state.opponent_hp -= 1
    
    elif action["card_id"] == "暮夜魔將‧艾瑟菈":
        n = len(state.own_minion_ids)
        state.own_minion_attack[-1] += n
    
    elif action["card_id"] == "無盡獵人‧阿拉加維":
        if state.opponent_minion_count > 0:
            state.opponent_minion_health[-1] -= 7
            while state.opponent_minion_health[-1] <= 0:
                if state.opponent_minion_count > 1:
                    state.opponent_minion_health[-2] += state.opponent_minion_health[-1]
                else:
                    break
                opponent_minion_die(state, -1)
    return state
    
def own_minion_die(state, idx):
    state.own_minion_ids.pop(idx)
    state.own_minion_attack.pop(idx)
    state.own_minion_health.pop(idx)
    state.own_minion_follows.pop(idx)
    state.own_minion_evo.pop(idx)
    state.own_minion_evo_rush.pop(idx)
    state.own_minion_count -= 1
    if state.own_minion_count < 0:
        state.own_minion_count = 0

def opponent_minion_die(state, idx):
    state.opponent_minion_attack.pop(idx)
    state.opponent_minion_health.pop(idx)
    state.opponent_minion_taunt.pop(idx)
    state.opponent_minion_count -= 1
    if state.opponent_minion_count < 0:
        state.opponent_minion_count = 0

def execute_activate_card(action, state):
    pass

def execute_attack(action, state):
    if action["target"] == "opponent_leader":
        state.opponent_hp -= state.own_minion_attack[action["attacker_index"]]
    elif action["target"] == "opponent_minion_n":
        idx = int(action["target"].split("_")[-1])
        if state.own_minion_evo[action["attacker_index"]] == "sevo":
            state.opponent_minion_health[idx] -= state.own_minion_attack[action["attacker_index"]]
            if state.opponent_minion_health[idx] <= 0:
                opponent_minion_die(state, idx)
                state.opponent_hp -= 1
        else:
            state.opponent_minion_health[idx] -= state.own_minion_attack[action["attacker_index"]]
            state.own_minion_health[action["attacker_index"]] -= state.opponent_minion_attack[idx]
            if state.opponent_minion_health[idx] <= 0:
                opponent_minion_die(state, idx)
            if state.own_minion_health[action["attacker_index"]] <= 0:
                own_minion_die(state, action["attacker_index"])
    elif action["target"] == None:
        pass
    state.own_minion_follows[action["attacker_index"]]="normal"
    state.own_minion_evo_rush[action["attacker_index"]]=False
    if "吸血" in actions_d[action["card_id"]].get("Const_Card", {}).get("keywords", []):
        state.player_hp += state.own_minion_attack[action["attacker_index"]]
    return state

def execute_evo(action, state):
    card_id = action["card_id"]
    idx=action["evo_index"]
    state.own_minion_attack[idx]+=2
    state.own_minion_health[idx]+=2
    state.own_minion_evo[idx]="evo"
    if state.own_minion_follows[idx]!="dash":
        if state.own_minion_evo_rush[idx]:
            state.own_minion_follows[idx]="rush"
        else:
            state.own_minion_follows[idx]="normal"
    state.evo_or_sevo_used=True
    state.e_value -= 1
        
    if card_id == "夢魔‧維莉":
        state.player_hp += 5
    elif card_id == "盛燃的魔劍‧歐特魯斯":
        if state.graveyard_count>=4:
            if sum(state.opponent_minion_health)>0:
                state.graveyard_count-=4
                for _ in range(2):
                    if sum(state.opponent_minion_health)>0:
                        idxo=random.randint(0,state.opponent_minion_count-1)
                        state.opponent_minion_health[idxo]-=2
                        if state.opponent_minion_health[idxo]<=0:
                            opponent_minion_die(state, idxo)
    if card_id == "無盡獵人‧阿拉加維":
        state.player_hp -= 3
        state.opponent_hp -= 3
    return state

def execute_sevo(action, state):
    card_id = action["card_id"]
    idx=action["sevo_index"]
    state.own_minion_attack[idx]+=3
    state.own_minion_health[idx]+=3
    state.own_minion_evo[idx]="sevo"
    if state.own_minion_follows[idx]!="dash":
        if state.own_minion_evo_rush[idx]:
            state.own_minion_follows[idx]="rush"
        else:
            state.own_minion_follows[idx]="normal"
    state.evo_or_sevo_used=True
    state.se_value -= 1
        
    if card_id == "夢魔‧維莉":
        state.player_hp += 5
    elif card_id == "盛燃的魔劍‧歐特魯斯":
        if state.graveyard_count>=4:
            if sum(state.opponent_minion_health)>0:
                state.graveyard_count-=4
                for _ in range(2):
                    if sum(state.opponent_minion_health)>0:
                        idxo=random.randint(0,state.opponent_minion_count-1)
                        state.opponent_minion_health[idxo]-=2
                        if state.opponent_minion_health[idxo]<=0:
                            opponent_minion_die(state, idxo)
    if card_id == "無盡獵人‧阿拉加維":
        state.player_hp -= 3
        state.opponent_hp -= 3
    return state

def execute_end_turn(action, state):
    state.evo_or_sevo_used=False
    # PP1恢复机制
    used_pp1 = action.get("extra", {}).get("used_pp1", False)
    if used_pp1 and getattr(state, "mana", 0) > 0:
        state.PP1 = 1
    return state

# ===== 自定义评分函数与AI循环 =====
def custom_evaluate_state(prev_state, new_state, return_detail=False):
    """
    评分函数，基于变量变化和权重。
    e、se为本回合消耗量，系数为负；hand为手牌数变化，少了减分多了加分。
    return_detail: 若为True，返回(总分, 评分项字典)
    """
    # 变量定义
    dmg = prev_state.opponent_hp - new_state.opponent_hp
    eatk = sum(new_state.opponent_minion_attack) if hasattr(new_state, "opponent_minion_attack") else 0
    edef = sum(new_state.opponent_minion_health) if hasattr(new_state, "opponent_minion_health") else 0
    matk = sum(new_state.own_minion_attack) if hasattr(new_state, "own_minion_attack") else 0
    mdef = sum(new_state.own_minion_health) if hasattr(new_state, "own_minion_health") else 0
    heal = new_state.player_hp - prev_state.player_hp  # 我方主战者回复
    hand = (len(new_state.hand_card_ids) - len(prev_state.hand_card_ids)) if hasattr(new_state, "hand_card_ids") else 0
    # e、se为消耗量（用前-后，消耗为正数）
    e = max(0, prev_state.e_value - new_state.e_value) if hasattr(prev_state, "e_value") and hasattr(new_state, "e_value") else 0
    se = max(0, prev_state.se_value - new_state.se_value) if hasattr(prev_state, "se_value") and hasattr(new_state, "se_value") else 0

    detail = {
        'dmg': (dmg, dmg ** 2),
        'eatk': (eatk, -3 * eatk),
        'edef': (edef, -2.5 * edef),
        'matk': (matk, 1.5 * matk),
        'mdef': (mdef, 1.25 * mdef),
        'heal': (heal, 0.5 * heal),
        'hand': (hand, 1 * hand),
        'e': (e, -6 * e),
        'se': (se, -9 * se),
    }
    score = sum([v[1] for v in detail.values()])
    if return_detail:
        return score, detail
    return score

def enumerate_all_action_paths(state, path=[], max_depth=20, debug_depth=0, visited=None):
    if visited is None:
        visited = set()
    """
    穷举所有动作路径（以end_turn为终点），返回所有路径及其最终状态。
    增加死锁/未推进剪枝、递归深度警告和调试信息。
    """
    from copy import deepcopy
    if max_depth <= 0:
        print(f"[警告] 超过最大递归深度，剪枝！当前路径长度: {len(path)}，动作序列: {path}")
        return []
    actions = enumerate_all_possible_actions(state)
    if not any(a.get("type") == "end_turn" for a in actions):
        actions.append({"type": "end_turn"})
    results = []
    state_snapshot = str([
        getattr(state, 'player_hp', None),
        getattr(state, 'opponent_hp', None),
        getattr(state, 'mana', None),
        getattr(state, 'own_minion_count', None),
        getattr(state, 'own_minion_attack', []),
        getattr(state, 'own_minion_health', []),
        getattr(state, 'own_minion_follows', []),
        getattr(state, 'own_minion_evo', []),
        getattr(state, 'own_minion_evo_rush', []),
        getattr(state, 'opponent_minion_count', None),
        getattr(state, 'opponent_minion_attack', []),
        getattr(state, 'opponent_minion_health', []),
        getattr(state, 'opponent_minion_taunt', []),
        getattr(state, 'hand_card_count', None),
        getattr(state, 'hand_card_ids', []),
        getattr(state, 'e_value', None),
        getattr(state, 'se_value', None),
        getattr(state, 'graveyard_count', None),
        getattr(state, 'PP1', None)
    ])
    visit_key = state_snapshot  # 只用状态，不加深度
    if visit_key in visited:
        print(f"[全局剪枝] 状态重复，路径终止，深度: {debug_depth}，动作序列: {path}")
        return []
    visited.add(visit_key)
    for action in actions:
        if debug_depth < 3:
            print(f"[递归] 深度: {debug_depth}，动作: {action}")
        if action.get("type") == "end_turn":
            sim_state = deepcopy(state)
            execute_action(action, sim_state)
            results.append((path + [action], sim_state))
        else:
            sim_state = deepcopy(state)
            execute_action(action, sim_state)
            sub_results =   enumerate_all_action_paths(sim_state, path + [action], max_depth-1, debug_depth=debug_depth+1, visited=visited)
            # 类型防御：只允许list类型
            if not isinstance(sub_results, list):
                print(f'[警告] 递归返回非list类型: {type(sub_results)}, 已丢弃')
                sub_results = []
            results.extend(sub_results)
    return results if isinstance(results, list) else []

def exhaustive_ai_search(state):
    """
    穷举所有动作路径，输出每条路径及评分，找出最优路径。
    只保留最必要的print。
    """
    print("\n【开始穷举所有动作路径】")
    start_time = time.time()
    # ===== PP1消耗机制 =====
    used_pp1 = False
    if getattr(state, 'PP1', 0) > 0 and not used_pp1:
        pp_x = 1450 + state.co[0]
        pp_y = 660 + state.co[1]
        import pyautogui
        pyautogui.mouseDown(pp_x, pp_y)
        time.sleep(0.5)
        pyautogui.mouseUp()
        state.mana += 1
        used_pp1 = True
    # if state is None:
        # 构造测试state
        # # class DummyState:
        # #     def __init__(self):
        # #         # 从actions_d中随机取三个不同的卡牌名
        # #         self.hand_card_ids = random.sample(list(actions_d.keys()), 3)
        # #         self.mana = 10
        # #         self.graveyard_count = 5
        # #         self.own_minion_ids = ["妖惑魅魔‧莉莉姆", "不屈的剑斗士"]
        # #         self.own_minion_attack = [1, 2]
        # #         self.own_minion_health = [1, 3]
        # #         self.own_minion_follows = ["dash", "dash"]
        # #         self.own_minion_evo = ["normal", "normal"]
        # #         self.own_minion_evo_rush = [True, True]  # 或根据你场上随从数量初始化
        # #         self.own_minion_count = 2
        # #         self.opponent_minion_attack = [3, 2]
        # #         self.opponent_minion_health = [2, 2]
        # #         self.opponent_minion_taunt = [True, False]
        # #         self.opponent_minion_count = 2
        # #         self.player_hp = 18
        # #         self.opponent_hp = 15
        # #         self.e_value = 1
        # #         self.se_value = 0
        # #         self.PP1 = 0
        # #         self.hand_card_count = 3
        # #         self.evo_or_sevo_used = False
        # #     def print_state(self):
        # #         print("\n=== 当前游戏状态 ===")
        # #         print(f"我方主战者HP: {self.player_hp}, 敌方主战者HP: {self.opponent_hp}, Mana: {self.mana}, 墓地: {self.graveyard_count}")
        # #         print(f"手牌: {self.hand_card_ids}")
        # #         print(f"我方随从: {self.own_minion_ids}")
        # #         print(f"我方随从攻: {self.own_minion_attack}")
        # #         print(f"我方随从血: {self.own_minion_health}")
        # #         print(f"我方随从状态: {self.own_minion_follows}")
        # #         print(f"敌方随从攻: {self.opponent_minion_attack}")
        # #         print(f"敌方随从血: {self.opponent_minion_health}")
        # #         print(f"敌方随从守护: {self.opponent_minion_taunt}")
        # #         print("====================")
        # state = DummyState()
        # print("\n【初始状态】")
        # state.print_state()
    all_paths = enumerate_all_action_paths(state, visited=None)
    if not isinstance(all_paths, list):
        return
    scored_paths = []
    total = len(all_paths)
    # 打印初始游戏状态
    print("\n【初始游戏状态】")
    if hasattr(state, "print_state"):
        state.print_state()
    print(f"\n【穷举路径总数】：{total}")
    
    import copy
    for item in all_paths:
        if not (isinstance(item, tuple) and len(item) == 2):
            continue
        path, final_state = item
        try:
            init_state_for_score = copy.deepcopy(state)
            result = custom_evaluate_state(init_state_for_score, final_state, return_detail=True)
            if isinstance(result, tuple) and len(result) == 2:
                score, detail = result
            else:
                score, detail = result, {}
        except Exception as e:
            continue
        scored_paths.append((score, path, final_state))
    scored_paths = [x for x in scored_paths if isinstance(x, tuple) and len(x) == 3]
    scored_paths.sort(reverse=True, key=lambda x: float(x[0]))
    if scored_paths:
        print("\n【最优路径动作序列】")
        best_score, best_path, best_state = scored_paths[0]
        for i, action in enumerate(best_path):
            print(f"  {i+1}. {action}")
        print(f"\n最终评分：{best_score:.2f}")
        if hasattr(best_state, "print_state"):
            best_state.print_state()
        return best_path, state
    else:
        print("未找到可行路径！")
        return None, state

# def main():
#     """
#     命令行测试入口。
#     只支持test_full模式。
#     """
#     print(f"\n【测试模式】test_full")
#     # 构造测试state
#     class DummyState:
#         def __init__(self, hand_count=3, minion_count=2, opponent_minion_count=2):
#             # 只选不带'e'前缀的卡牌名
#             non_e_cards = [k for k in actions_d.keys() if not k.startswith('e')]
#             self.hand_card_ids = random.sample(non_e_cards, hand_count)
#             self.mana = 10
#             self.graveyard_count = 10
#             # 随机抽取minion_count个不带e前缀的随从
#             self.own_minion_ids = random.sample(non_e_cards, minion_count)
#             self.own_minion_attack = [random.randint(1, 5) for _ in range(minion_count)]
#             self.own_minion_health = [random.randint(1, 5) for _ in range(minion_count)]
#             # 随从状态随机
#             self.own_minion_follows = [random.choice(["normal", "dash", "rush"]) for _ in range(minion_count)]
#             self.own_minion_evo = ["normal" for _ in range(minion_count)]
#             self.own_minion_evo_rush = [True for _ in range(minion_count)]
#             self.own_minion_count = minion_count
#             # 敌方随从
#             self.opponent_minion_attack = [random.randint(1, 5) for _ in range(opponent_minion_count)]
#             self.opponent_minion_health = [random.randint(1, 5) for _ in range(opponent_minion_count)]
#             self.opponent_minion_taunt = [random.choice([True, False]) for _ in range(opponent_minion_count)]
#             self.opponent_minion_count = opponent_minion_count
#             self.player_hp = 18
#             self.opponent_hp = 15
#             self.e_value = 1
#             self.se_value = 0
#             self.PP1 = 0
#             self.hand_card_count = hand_count
#             self.evo_or_sevo_used = False
#         def print_state(self):
#             print("\n=== 当前游戏状态 ===")
#             print(f"我方主战者HP: {self.player_hp}, 敌方主战者HP: {self.opponent_hp}, Mana: {self.mana}, 墓地: {self.graveyard_count}")
#             print(f"手牌: {self.hand_card_ids}")
#             print(f"我方随从: {self.own_minion_ids}")
#             print(f"我方随从攻: {self.own_minion_attack}")
#             print(f"我方随从血: {self.own_minion_health}")
#             print(f"我方随从状态: {self.own_minion_follows}")
#             print(f"敌方随从攻: {self.opponent_minion_attack}")
#             print(f"敌方随从血: {self.opponent_minion_health}")
#             print(f"敌方随从守护: {self.opponent_minion_taunt}")
#             print("====================")
#     state = DummyState()
#     print("\n【初始状态】")
#     state.print_state()
#     exhaustive_ai_search(state)

# if __name__ == '__main__':
#     main()    