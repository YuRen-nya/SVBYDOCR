# ai_core.py

from action_definitions import *
import sys
import time
from copy import deepcopy
from collections import defaultdict

# ===== 主要函数与核心逻辑 =====

def execute_action(action, state):
    """
    执行单个action，直接修改state，不做真实操作。
    主要分支：
    - play_card：出牌（随从/法术/特殊卡）
    - attack：随从攻击
    - evo/sevo：进化/超进化
    - end_turn：结束回合
    特殊卡牌有专属分支，普通卡牌走通用逻辑。
    """
    if action["action_type"] == "play_card":
        # 扣除法力
        mana_cost = None
        if "extra" in action:
            if "burst_cost" in action["extra"]:
                mana_cost = action["extra"]["burst_cost"]
            elif "necro_cost" in action["extra"]:
                mana_cost = action.get("cost", 0)  # 死灵术消耗不影响费用，仍用cost
        if mana_cost is None:
            mana_cost = action.get("cost", 0)
        if hasattr(state, "mana") and mana_cost is not None:
            state.mana -= mana_cost
            if state.mana < 0:
                state.mana = 0
        # 统一：所有play_card都先从手牌移除
        if hasattr(state, "hand_card_ids") and action["card_id"] in state.hand_card_ids:
            state.hand_card_ids.remove(action["card_id"])
            if hasattr(state, "hand_card_count"):
                state.hand_card_count -= 1
        # ======== 特殊卡牌分支实现 ========
        # 1. 夢魔‧維莉
        if action["card_id"] == "夢魔‧維莉":
            if action["card_id"] in state.hand_card_ids:
                state.hand_card_ids.remove(action["card_id"])
                state.hand_card_count -= 1
            # 召唤
            if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                state.own_minion_ids.append(action["card_id"])
                state.own_minion_attack.append(action["attack"])
                state.own_minion_health.append(action["health"])
                if hasattr(state, "own_minion_follows"):
                    state.own_minion_follows.append("normal")
                if hasattr(state, "own_minion_evo_rush"):
                    state.own_minion_evo_rush.append(True)
                state.own_minion_count = len(state.own_minion_ids)
            # fanfare: effect=damage_leader
            extra = action.get("extra", {})
            fanfare = extra.get("fanfare")
            if fanfare:
                if isinstance(fanfare, dict):
                    fanfare = [fanfare]
                for eff in fanfare:
                    if eff.get("effect") == "damage_leader" and eff.get("target") == "player":
                        value = eff.get("value", 0)
                        if hasattr(state, "player_hp"):
                            state.player_hp -= value
        # 2. 盛燃的魔劍‧歐特魯斯
        elif action["card_id"] == "盛燃的魔劍‧歐特魯斯":
            if action["card_id"] in state.hand_card_ids:
                state.hand_card_ids.remove(action["card_id"])
                state.hand_card_count -= 1
            if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                state.own_minion_ids.append(action["card_id"])
                state.own_minion_attack.append(action["attack"])
                state.own_minion_health.append(action["health"])
                if hasattr(state, "own_minion_follows"):
                    state.own_minion_follows.append("normal")
                state.own_minion_count = len(state.own_minion_ids)
        # 3. 無盡獵人‧阿拉加維
        elif action["card_id"] == "無盡獵人‧阿拉加維":
            if action["card_id"] in state.hand_card_ids:
                state.hand_card_ids.remove(action["card_id"])
                state.hand_card_count -= 1
            if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                state.own_minion_ids.append(action["card_id"])
                state.own_minion_attack.append(action["attack"])
                state.own_minion_health.append(action["health"])
                if hasattr(state, "own_minion_follows"):
                    state.own_minion_follows.append("normal")
                state.own_minion_count = len(state.own_minion_ids)
        # 4. 反转互换
        elif action["card_id"] == "反转互换":
            target_info = action.get("target_info", {})
            side = target_info.get("side")
            idx = target_info.get("index")
            if side == "own":
                if hasattr(state, "own_minion_attack") and idx is not None and idx < len(state.own_minion_attack):
                    state.own_minion_attack[idx] += 2
                    state.own_minion_health[idx] -= 2
                    if state.own_minion_health[idx] < 0:
                        for arr in [
                            state.own_minion_ids,
                            state.own_minion_attack,
                            state.own_minion_health,
                            state.own_minion_follows,
                            state.own_minion_evo
                        ]:
                            if idx < len(arr):
                                arr.pop(idx)
                        state.own_minion_count = len(state.own_minion_ids)
            elif side == "opponent":
                if hasattr(state, "opponent_minion_attack") and idx is not None and idx < len(state.opponent_minion_attack):
                    state.opponent_minion_attack[idx] += 2
                    state.opponent_minion_health[idx] -= 2
                    if state.opponent_minion_health[idx] < 0:
                        for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                            if idx < len(arr):
                                arr.pop(idx)
                        state.opponent_minion_count = len(state.opponent_minion_attack)
        # 5. 蛇神的嗔怒
        elif action["card_id"] == "蛇神的嗔怒":
            target_info = action.get("target_info", {})
            if target_info.get("side") == "opponent":
                idx = target_info.get("index")
                if hasattr(state, "opponent_minion_health") and idx is not None and idx < len(state.opponent_minion_health):
                    state.opponent_minion_health[idx] -= 3
                    if state.opponent_minion_health[idx] <= 0:
                        for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                            if idx < len(arr):
                                arr.pop(idx)
                        state.opponent_minion_count = len(state.opponent_minion_attack)
            elif target_info.get("side") == "opponent_leader":
                if hasattr(state, "opponent_hp"):
                    state.opponent_hp -= 3
            if hasattr(state, "player_hp"):
                state.player_hp -= 2
        # 6. 死神挥镰
        elif action["card_id"] == "死神挥镰":
            target_ids = action.get("target_ids", [])
            if len(target_ids) == 2:
                my_idx, opp_idx = target_ids
                # 移除我方目标随从
                if hasattr(state, "own_minion_attack") and my_idx is not None and my_idx < len(state.own_minion_attack):
                    for arr in [
                        state.own_minion_ids,
                        state.own_minion_attack,
                        state.own_minion_health,
                        state.own_minion_follows,
                        state.own_minion_evo
                    ]:
                        if my_idx < len(arr):
                            arr.pop(my_idx)
                    state.own_minion_count = len(state.own_minion_ids)
                # 移除敌方目标随从
                if hasattr(state, "opponent_minion_attack") and opp_idx is not None and opp_idx < len(state.opponent_minion_attack):
                    for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                        if opp_idx < len(arr):
                            arr.pop(opp_idx)
                    state.opponent_minion_count = len(state.opponent_minion_attack)
            return
        # 7. 役使蝙蝠
        elif action["card_id"] == "役使蝙蝠":
            for _ in range(2):
                if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                    state.own_minion_ids.append("蝙蝠")
                    state.own_minion_attack.append(1)
                    state.own_minion_health.append(1)
                    if hasattr(state, "own_minion_follows"):
                        state.own_minion_follows.append("normal")
            if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) > 5:
                over = len(state.own_minion_ids) - 5
                for _ in range(over):
                    for arr in [state.own_minion_ids, state.own_minion_attack, state.own_minion_health, state.own_minion_follows]:
                        if arr:
                            arr.pop()
            state.own_minion_count = len(state.own_minion_ids)
        # 8. 法外的賞金獵人‧巴爾特
        elif action["card_id"] == "法外的賞金獵人‧巴爾特":
            if hasattr(state, "player_hp"):
                state.player_hp -= 1
            if hasattr(state, "opponent_hp"):
                state.opponent_hp -= 1
        # 9. 暮夜魔將‧艾瑟菈
        elif action["card_id"] == "暮夜魔將‧艾瑟菈":
            if action["card_id"] in state.hand_card_ids:
                state.hand_card_ids.remove(action["card_id"])
                state.hand_card_count -= 1
            if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                cur_count = len(state.own_minion_ids)
                atk = action["attack"] + cur_count
                state.own_minion_ids.append(action["card_id"])
                state.own_minion_attack.append(atk)
                state.own_minion_health.append(action["health"])
                if hasattr(state, "own_minion_follows"):
                    state.own_minion_follows.append("dash")
                state.own_minion_count = len(state.own_minion_ids)
        # 10. 凶恶的小木乃伊
        elif action["card_id"] == "凶恶的小木乃伊":
            if action["card_id"] in state.hand_card_ids:
                state.hand_card_ids.remove(action["card_id"])
                state.hand_card_count -= 1
            if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                state.own_minion_ids.append(action["card_id"])
                state.own_minion_attack.append(action["attack"])
                state.own_minion_health.append(action["health"])
                if "necro_cost" in action.get("extra", {}):
                    if hasattr(state, "own_minion_follows"):
                        state.own_minion_follows.append("dash")
                else:
                    if hasattr(state, "own_minion_follows"):
                        state.own_minion_follows.append("normal")
                state.own_minion_count = len(state.own_minion_ids)
        # ======== 其他随从/法术通用实现 ========
        else:
            # 先从手牌移除
            if action["card_id"] in state.hand_card_ids:
                state.hand_card_ids.remove(action["card_id"])
                state.hand_card_count -= 1
            # 判断是否随从卡
            if action["attack"] is not None and action["health"] is not None:
                # 最多5个随从
                if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                    # 暮夜魔將‧艾瑟菈特殊处理
                    if action["card_id"] == "暮夜魔將‧艾瑟菈":
                        # 召唤时攻击力=原始攻击力+场上已有随从数（不+1）
                        cur_count = len(state.own_minion_ids)
                        atk = action["attack"] + cur_count
                        state.own_minion_ids.append(action["card_id"])
                        state.own_minion_attack.append(atk)
                        state.own_minion_health.append(action["health"])
                        if hasattr(state, "own_minion_follows"):
                            state.own_minion_follows.append("dash")
                        if hasattr(state, "own_minion_evo_rush"):
                            state.own_minion_evo_rush.append(True)
                    else:
                        state.own_minion_ids.append(action["card_id"])
                        state.own_minion_attack.append(action["attack"])
                        state.own_minion_health.append(action["health"])
                        # 判断是否死灵术凶恶的小木乃伊
                        if action["card_id"] == "凶恶的小木乃伊" and "necro_cost" in action.get("extra", {}):
                            if hasattr(state, "own_minion_follows"):
                                state.own_minion_follows.append("dash")
                            if hasattr(state, "own_minion_evo_rush"):
                                state.own_minion_evo_rush.append(True)
                        else:
                            if hasattr(state, "own_minion_follows"):
                                state.own_minion_follows.append("normal")
                            if hasattr(state, "own_minion_evo_rush"):
                                state.own_minion_evo_rush.append(True)
                    state.own_minion_count = len(state.own_minion_ids)
            # fanfare: effect=damage_leader/add_graveyard
            extra = action.get("extra", {})
            fanfare = extra.get("fanfare")
            if fanfare:
                # 支持dict或list
                if isinstance(fanfare, dict):
                    fanfare = [fanfare]
                for eff in fanfare:
                    if eff.get("effect") == "damage_leader" and eff.get("target") == "player":
                        value = eff.get("value", 0)
                        if hasattr(state, "player_hp"):
                            state.player_hp -= value
                    if eff.get("effect") == "add_graveyard":
                        value = eff.get("value", 0)
                        if hasattr(state, "graveyard_count"):
                            state.graveyard_count += value
            # 死神挥镰、反转互换、役使蝙蝠、蛇神的嗔怒、巴尔特、阿拉加维等特殊法术
            elif action["card_id"] == "死神挥镰":
                # 选择我方攻+血最小随从
                if hasattr(state, "own_minion_attack") and state.own_minion_attack:
                    idx_my = min(range(len(state.own_minion_attack)), key=lambda i: state.own_minion_attack[i]+state.own_minion_health[i])
                    for arr in [state.own_minion_ids, state.own_minion_attack, state.own_minion_health, state.own_minion_follows]:
                        if idx_my < len(arr):
                            arr.pop(idx_my)
                    state.own_minion_count = len(state.own_minion_ids)
                # 选择敌方攻+血最大随从
                if hasattr(state, "opponent_minion_attack") and state.opponent_minion_attack:
                    idx_enemy = max(range(len(state.opponent_minion_attack)), key=lambda i: state.opponent_minion_attack[i]+state.opponent_minion_health[i])
                    for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                        if idx_enemy < len(arr):
                            arr.pop(idx_enemy)
                    state.opponent_minion_count = len(state.opponent_minion_attack)
            # 反转互换法术
            elif action["card_id"] == "反转互换":
                target_info = action.get("target_info", {})
                side = target_info.get("side")
                idx = target_info.get("index")
                if side == "own":
                    if hasattr(state, "own_minion_attack") and idx is not None and idx < len(state.own_minion_attack):
                        state.own_minion_attack[idx] += 2
                        state.own_minion_health[idx] -= 2
                        if state.own_minion_health[idx] < 0:
                            for arr in [state.own_minion_ids, state.own_minion_attack, state.own_minion_health, state.own_minion_follows]:
                                if idx < len(arr):
                                    arr.pop(idx)
                            state.own_minion_count = len(state.own_minion_attack)
                elif side == "opponent":
                    if hasattr(state, "opponent_minion_attack") and idx is not None and idx < len(state.opponent_minion_attack):
                        state.opponent_minion_attack[idx] += 2
                        state.opponent_minion_health[idx] -= 2
                        if state.opponent_minion_health[idx] < 0:
                            for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                                if idx < len(arr):
                                    arr.pop(idx)
                            state.opponent_minion_count = len(state.opponent_minion_attack)
            # 役使蝙蝠
            elif action["card_id"] == "役使蝙蝠":
                # 召唤2个1-1蝙蝠，超过5个只保留最先上的5个
                for _ in range(2):
                    if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) < 5:
                        state.own_minion_ids.append("蝙蝠")
                        state.own_minion_attack.append(1)
                        state.own_minion_health.append(1)
                        if hasattr(state, "own_minion_follows"):
                            state.own_minion_follows.append("normal")
                # 若添加后超过5个，移除多余的
                if hasattr(state, "own_minion_ids") and len(state.own_minion_ids) > 5:
                    over = len(state.own_minion_ids) - 5
                    for _ in range(over):
                        for arr in [state.own_minion_ids, state.own_minion_attack, state.own_minion_health, state.own_minion_follows]:
                            if arr:
                                arr.pop()
                state.own_minion_count = len(state.own_minion_ids)
            # 蛇神的嗔怒
            elif action["card_id"] == "蛇神的嗔怒":
                target_info = action.get("target_info", {})
                # 目标为敌方随从
                if target_info.get("side") == "opponent":
                    idx = target_info.get("index")
                    if hasattr(state, "opponent_minion_health") and idx is not None and idx < len(state.opponent_minion_health):
                        state.opponent_minion_health[idx] -= 3
                        # 若随从死亡自动移除
                        if state.opponent_minion_health[idx] <= 0:
                            for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                                if idx < len(arr):
                                    arr.pop(idx)
                            state.opponent_minion_count = len(state.opponent_minion_attack)
                # 目标为敌方主战者
                elif target_info.get("side") == "opponent_leader":
                    if hasattr(state, "opponent_hp"):
                        state.opponent_hp -= 3
                # 无论目标是谁，我方主战者生命值-2
                if hasattr(state, "player_hp"):
                    state.player_hp -= 2
            elif action["card_id"] == "法外的賞金獵人‧巴爾特":
                # 直接让敌我主战者生命值各-1
                if hasattr(state, "player_hp"):
                    state.player_hp -= 1
                if hasattr(state, "opponent_hp"):
                    state.opponent_hp -= 1
            elif action["card_id"] == "無盡獵人‧阿拉加維":
                # 对敌方最先进入战场（索引最小）的随从造成7点伤害，超出顺延，死亡立即移除
                damage = 7
                idx = 0
                while damage > 0 and hasattr(state, "opponent_minion_health") and idx < len(state.opponent_minion_health):
                    state.opponent_minion_health[idx] -= damage
                    if state.opponent_minion_health[idx] <= 0:
                        # 伤害溢出，顺延到下一个
                        overflow = -state.opponent_minion_health[idx]
                        # 死亡判定：移除该随从所有信息
                        for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                            if idx < len(arr):
                                arr.pop(idx)
                        state.opponent_minion_count = len(state.opponent_minion_attack)
                        damage = overflow
                        # 不递增idx，因为移除了当前随从，后面随从前移
                    else:
                        # 伤害用完或随从未死
                        damage = 0
    elif action["action_type"] == "attack":
        """
        随从攻击通用逻辑：
        - 双方生命互减对方攻击力，生命≤0立即移除（死亡判定）
        - sevo随从攻击时自己不受伤害，若击杀对方随从则对方主战者-1
        - 蝙蝠攻击时吸血
        - 攻击后rush/dash转normal
        """
        card_id = action["card_id"]
        attacker_index = action.get("attacker_index")
        target_ids = action.get("target_ids")
        if isinstance(target_ids, list) and len(target_ids) > 0:
            target = target_ids[0]
        else:
            target = None
        # 只处理随从攻击随从或主战者
         # 攻击方在我方随从
        if hasattr(state, "own_minion_ids") and attacker_index is not None and 0 <= attacker_index < len(state.own_minion_ids):
            atk_idx = attacker_index
            attacker_atk = state.own_minion_attack[atk_idx]
            attacker_hp = state.own_minion_health[atk_idx]
            # 判断是否sevo
            is_sevo = False
            if hasattr(state, "own_minion_evo") and atk_idx < len(state.own_minion_evo):
                is_sevo = (state.own_minion_evo[atk_idx] == "sevo")
            # 目标为敌方随从（支持int和'enemy_N'字符串）
            if (isinstance(target, int)) or (isinstance(target, str) and target.startswith("enemy_") and target[6:].isdigit()):
                tgt_idx = target if isinstance(target, int) else int(target[6:])
                if hasattr(state, "opponent_minion_attack") and tgt_idx is not None and tgt_idx < len(state.opponent_minion_attack):
                    defender_atk = state.opponent_minion_attack[tgt_idx]
                    defender_hp = state.opponent_minion_health[tgt_idx]
                    # 互相扣血（sevo不受伤害）
                    if not is_sevo:
                        state.own_minion_health[atk_idx] -= defender_atk
                    state.opponent_minion_health[tgt_idx] -= attacker_atk
                    # 死亡判定
                    killed_attacker = False
                    killed_defender = False
                    # 先判定防守方死亡
                    if state.opponent_minion_health[tgt_idx] <= 0:
                        killed_defender = True
                        # 同步删除所有敌方随从相关信息
                        for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                            if tgt_idx < len(arr):
                                arr.pop(tgt_idx)
                        if hasattr(state, "opponent_minion_positions") and tgt_idx < len(state.opponent_minion_positions):
                            state.opponent_minion_positions.pop(tgt_idx)
                        state.opponent_minion_count = len(state.opponent_minion_attack)
                    # 再判定攻击方死亡
                    if state.own_minion_health[atk_idx] <= 0:
                        killed_attacker = True
                        # 同步删除所有我方随从相关信息
                        for arr in [state.own_minion_ids, state.own_minion_attack, state.own_minion_health, state.own_minion_follows]:
                            if atk_idx < len(arr):
                                arr.pop(atk_idx)
                        if hasattr(state, "own_minion_positions") and atk_idx < len(state.own_minion_positions):
                            state.own_minion_positions.pop(atk_idx)
                        if hasattr(state, 'own_minion_evo_rush') and atk_idx < len(state.own_minion_evo_rush):
                            state.own_minion_evo_rush.pop(atk_idx)
                        if hasattr(state, 'own_minion_evo') and atk_idx < len(state.own_minion_evo):
                            state.own_minion_evo.pop(atk_idx)
                        state.own_minion_count = len(state.own_minion_ids)
                    # sevo击杀对方随从时对方主站者-1
                    if is_sevo and killed_defender:
                        state.opponent_hp -= 1
                    # 蝙蝠吸血
                    if card_id == "蝙蝠":
                        state.player_hp += attacker_atk
            # 目标为敌方主战者
            elif target == "enemy_leader":
                state.opponent_hp -= attacker_atk
                # 蝙蝠吸血
                if card_id == "蝙蝠":
                    state.player_hp += attacker_atk
            elif not target or target is None:
                pass
                # print("⚠️ 无攻击目标，跳过")
            else:
                print(f"⚠️ 未知目标类型: {target}")
        # 攻击后，若该随从为rush/dash，转变为normal
        if hasattr(state, "own_minion_follows") and attacker_index is not None and 0 <= attacker_index < len(state.own_minion_follows):
            if state.own_minion_follows[attacker_index] in ("rush", "dash"):
                state.own_minion_follows[attacker_index] = "normal"
        # 攻击后，evo_rush=False
        if hasattr(state, "own_minion_evo_rush") and attacker_index is not None and 0 <= attacker_index < len(state.own_minion_evo_rush):
            state.own_minion_evo_rush[attacker_index] = False
    elif action["action_type"] == "evo":
        card_id = action["card_id"]
        # ====== 特殊evo优先 ======
        # 夢魔‧維莉 evo：回复我方主战者5点生命
        if card_id == "夢魔‧維莉":
            if hasattr(state, "player_hp"):
                state.player_hp += 5
            # 赋予rush和+2/+2
            if hasattr(state, "own_minion_ids") and card_id in state.own_minion_ids:
                idx = state.own_minion_ids.index(card_id)
                if hasattr(state, "own_minion_follows"):
                    while len(state.own_minion_follows) < len(state.own_minion_ids):
                        state.own_minion_follows.append("normal")
                    state.own_minion_follows[idx] = "rush"
                # +2/+2
                if hasattr(state, "own_minion_attack") and idx < len(state.own_minion_attack):
                    state.own_minion_attack[idx] += 2
                if hasattr(state, "own_minion_health") and idx < len(state.own_minion_health):
                    state.own_minion_health[idx] += 2
            if hasattr(state, "e_value"):
                state.e_value = max(0, state.e_value - 1)
            state.evo_or_sevo_used = True
            return
        # 盛燃的魔劍‧歐特魯斯 evo：死灵术4，随机2次对敌随从2伤害
        if card_id == "盛燃的魔劍‧歐特魯斯":
    # 只有有敌方随从时才消耗墓地
            if hasattr(state, "opponent_minion_health") and len(state.opponent_minion_health) > 0 and getattr(state, "graveyard_count", 0) >= 4:
                import random
                n = len(state.opponent_minion_health)
                if n == 1:
                    # 只有一个目标，打两次（如果第一次就死了，第二次不再打）
                    for _ in range(2):
                        state.opponent_minion_health[0] -= 2
                        if state.opponent_minion_health[0] <= 0:
                            for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                                if len(arr) > 0:
                                    arr.pop(0)
                            state.opponent_minion_count = len(state.opponent_minion_attack)
                            break  # 死了就不再打第二次
                else:
                    # 随机选2个不同目标
                    idxs = random.sample(range(n), 2)
                    # 先大后小，避免pop时索引错位
                    idxs.sort(reverse=True)
                    for idx in idxs:
                        state.opponent_minion_health[idx] -= 2
                        if state.opponent_minion_health[idx] <= 0:
                            for arr in [state.opponent_minion_attack, state.opponent_minion_health, state.opponent_minion_taunt]:
                                if idx < len(arr):
                                    arr.pop(idx)
                            state.opponent_minion_count = len(state.opponent_minion_attack)
                state.graveyard_count -= 4
            # 赋予rush和+2/+2
            if hasattr(state, "own_minion_ids") and card_id in state.own_minion_ids:
                idx = state.own_minion_ids.index(card_id)
                if hasattr(state, "own_minion_follows"):
                    while len(state.own_minion_follows) < len(state.own_minion_ids):
                        state.own_minion_follows.append("normal")
                    state.own_minion_follows[idx] = "rush"
                # +2/+2
                if hasattr(state, "own_minion_attack") and idx < len(state.own_minion_attack):
                    state.own_minion_attack[idx] += 2
                if hasattr(state, "own_minion_health") and idx < len(state.own_minion_health):
                    state.own_minion_health[idx] += 2
            if hasattr(state, "e_value"):
                state.e_value = max(0, state.e_value - 1)
            state.evo_or_sevo_used = True
            return
        # 無盡獵人‧阿拉加維 evo：敌我主战者各-3生命
        if card_id == "無盡獵人‧阿拉加維":
            if hasattr(state, "player_hp"):
                state.player_hp -= 3
            if hasattr(state, "opponent_hp"):
                state.opponent_hp -= 3
            # 赋予rush和+2/+2
            if hasattr(state, "own_minion_ids") and card_id in state.own_minion_ids:
                idx = state.own_minion_ids.index(card_id)
                if hasattr(state, "own_minion_follows"):
                    while len(state.own_minion_follows) < len(state.own_minion_ids):
                        state.own_minion_follows.append("normal")
                    state.own_minion_follows[idx] = "rush"
                # +2/+2
                if hasattr(state, "own_minion_attack") and idx < len(state.own_minion_attack):
                    state.own_minion_attack[idx] += 2
                if hasattr(state, "own_minion_health") and idx < len(state.own_minion_health):
                    state.own_minion_health[idx] += 2
            if hasattr(state, "e_value"):
                state.e_value = max(0, state.e_value - 1)
            state.evo_or_sevo_used = True
            return
        # ====== 通用evo ======
        if hasattr(state, "own_minion_ids") and card_id in state.own_minion_ids:
            idx = state.own_minion_ids.index(card_id)
            if not hasattr(state, "own_minion_evo"):
                state.own_minion_evo = []
            # 补齐长度
            while len(state.own_minion_evo) < len(state.own_minion_ids):
                state.own_minion_evo.append("normal")
            while len(state.own_minion_evo) > len(state.own_minion_ids):
                state.own_minion_evo.pop()
            state.own_minion_attack[idx] += 2
            state.own_minion_health[idx] += 2
            state.own_minion_evo[idx] = "evo"
            # 如果evo_rush=True，赋予rush
            if hasattr(state, "own_minion_evo_rush") and idx is not None and idx < len(state.own_minion_evo_rush) and state.own_minion_evo_rush[idx]:
                while len(state.own_minion_follows) < len(state.own_minion_ids):
                    state.own_minion_follows.append("normal")
                state.own_minion_follows[idx] = "rush"
            # evo点消耗
            if hasattr(state, "e_value"):
                state.e_value = max(0, state.e_value - 1)
            # 记录本回合已evo的随从
            if not hasattr(state, "used_evo_ids"):
                state.used_evo_ids = set()
            state.used_evo_ids.add(card_id)
            # 本回合已evo或sevo标记
            state.evo_or_sevo_used = True
    elif action["action_type"] == "sevo":
        card_id = action["card_id"]
        if hasattr(state, "own_minion_ids") and card_id in state.own_minion_ids:
            idx = state.own_minion_ids.index(card_id)
            if not hasattr(state, "own_minion_evo"):
                state.own_minion_evo = []
            # 补齐长度
            while len(state.own_minion_evo) < len(state.own_minion_ids):
                state.own_minion_evo.append("normal")
            while len(state.own_minion_evo) > len(state.own_minion_ids):
                state.own_minion_evo.pop()
            state.own_minion_attack[idx] += 3
            state.own_minion_health[idx] += 3
            state.own_minion_evo[idx] = "sevo"
            # 赋予rush
            if hasattr(state, "own_minion_follows"):
                while len(state.own_minion_follows) < len(state.own_minion_ids):
                    state.own_minion_follows.append("normal")
                state.own_minion_follows[idx] = "rush"
            # sevo点消耗
            if hasattr(state, "se_value"):
                state.se_value = max(0, state.se_value - 1)
            # 记录本回合已sevo的随从
            if not hasattr(state, "used_sevo_ids"):
                state.used_sevo_ids = set()
            state.used_sevo_ids.add(card_id)
            # 本回合已evo或sevo标记
            state.evo_or_sevo_used = True
    elif action["action_type"] == "end_turn":
        # 回合结束时重置used_evo_ids、used_sevo_ids和evo_or_sevo_used
        if hasattr(state, "used_evo_ids"):
            state.used_evo_ids.clear()
        if hasattr(state, "used_sevo_ids"):
            state.used_sevo_ids.clear()
        if hasattr(state, "evo_or_sevo_used"):
            state.evo_or_sevo_used = False
        """
        结束回合，处理PP1恢复机制
        """
        # PP1恢复机制
        used_pp1 = action.get("extra", {}).get("used_pp1", False)
        if used_pp1 and getattr(state, "mana", 0) > 0:
            state.PP1 = 1
    else:
        pass

def enumerate_all_possible_actions(state):
    """
    枚举所有可行动作，返回action字典列表。
    主要流程：
    - 手牌出牌（只枚举手牌中且费用≤当前mana的play_card，死灵术/爆能等特殊消耗自动判断）
    - 特殊卡牌目标枚举（如反转互换、蛇神的嗔怒）
    - rush/dash随从攻击（自动判断守护、主战者、空目标）
    - 进化/超进化（有资源才枚举）
    - PP1机制（枚举前如state.PP1>0，直接视为本回合消耗PP1）
    - 结束回合
    """
    actions = []
    this_module = sys.modules[__name__]
    all_action_vars = [v for k, v in this_module.__dict__.items() if isinstance(v, dict) and v.get("action_type") in ("play_card", "evo", "sevo")]

    # 1. 卡牌使用（分组处理，自动适配死灵术/爆能等）
    playcard_actions = []  # 修复未定义
    playcard_group = defaultdict(list)
    for action in all_action_vars:
        if action["action_type"] == "play_card" and action["card_id"] in getattr(state, 'hand_card_ids', []) and action.get("cost", 999) <= state.mana:
            # 特殊处理反转互换
            if action["card_id"] == "反转互换":
                # 枚举所有我方随从
                for idx in range(len(getattr(state, "own_minion_attack", []))):
                    new_action = action_play_inversion_swap_template.copy()
                    new_action["target_info"] = {"side": "own", "index": idx}
                    playcard_group[action["card_id"]].append(new_action)
                # 枚举所有敌方随从
                for idx in range(len(getattr(state, "opponent_minion_attack", []))):
                    new_action = action_play_inversion_swap_template.copy()
                    new_action["target_info"] = {"side": "opponent", "index": idx}
                    playcard_group[action["card_id"]].append(new_action)
                continue
            # 特殊处理蛇神的嗔怒
            if action["card_id"] == "蛇神的嗔怒":
                # 敌方随从
                for idx in range(len(getattr(state, "opponent_minion_attack", []))):
                    new_action = action_play_serpent_anger_template.copy()
                    new_action["target_info"] = {"side": "opponent", "index": idx}
                    playcard_group[action["card_id"]].append(new_action)
                # 敌方主战者
                new_action = action_play_serpent_anger_template.copy()
                new_action["target_info"] = {"side": "opponent_leader"}
                playcard_group[action["card_id"]].append(new_action)
                continue
            # 特殊处理死神挥镰
            if action["card_id"] == "死神挥镰":
                # 只有双方随从都存在时才枚举
                own_count = len(getattr(state, "own_minion_attack", []))
                opp_count = len(getattr(state, "opponent_minion_attack", []))
                if own_count and opp_count:
                    for i in range(own_count):
                        for j in range(opp_count):
                            new_action = action_play_reaper_scythe.copy()
                            new_action["target_ids"] = [i, j]
                            playcard_group[action["card_id"]].append(new_action)
                continue
            playcard_group[action["card_id"]].append(action)
    for cid, actions in playcard_group.items():
        # 查找是否有死灵术action
        necro_actions = [a for a in actions if "necro_cost" in a.get("extra", {})]
        normal_actions = [a for a in actions if "necro_cost" not in a.get("extra", {})]
        if necro_actions:
            necro_cost = necro_actions[0]["extra"]["necro_cost"]
            if getattr(state, "graveyard_count", 0) >= necro_cost:
                playcard_actions.extend(necro_actions)
            else:
                playcard_actions.extend(normal_actions)
        else:
            playcard_actions.extend(actions)
    # 对同一张卡，优先保留带 burst_cost 的
    unique_playcard = {}
    for action in playcard_actions:
        cid = action["card_id"]
        if "burst_cost" in action.get("extra", {}):
            unique_playcard[cid] = action  # 覆盖普通
        elif cid not in unique_playcard or cid == "反转互换":
            # 反转互换允许多个目标action
            if cid == "反转互换":
                if cid not in unique_playcard:
                    unique_playcard[cid] = []
                if isinstance(unique_playcard[cid], list):
                    unique_playcard[cid].append(action)
            else:
                unique_playcard[cid] = action  # 只在没有burst_cost时保留普通
    # 展开反转互换的所有目标action
    for v in unique_playcard.values():
        if isinstance(v, list):
            actions.extend(v)
        else:
            actions.append(v)
    # 2. 随从攻击
    for idx, minion_id in enumerate(getattr(state, 'own_minion_ids', [])):
        follow_type = state.own_minion_follows[idx] if idx < len(state.own_minion_follows) else None
        taunt_targets = [i for i, t in enumerate(getattr(state, 'opponent_minion_taunt', [])) if t]
        enemy_minion_ids = [f"enemy_{i}" for i in range(getattr(state, 'opponent_minion_count', 0))]
        enemy_leader = "enemy_leader"
        if follow_type == "rush":
            if taunt_targets:
                targets = [enemy_minion_ids[i] for i in taunt_targets]
            else:
                targets = enemy_minion_ids
            for target in targets:
                actions.append({
                    "action_type": "attack",
                    "card_id": minion_id,
                    "target_ids": [target],
                    "attacker_index": idx,
                    "extra": {}
                })
            actions.append({
                "action_type": "attack",
                "card_id": minion_id,
                "target_ids": [],
                "attacker_index": idx,
                "extra": {}
            })
        elif follow_type == "dash":
            if taunt_targets:
                targets = [enemy_minion_ids[i] for i in taunt_targets]
            else:
                targets = enemy_minion_ids + [enemy_leader]
            for target in targets:
                actions.append({
                    "action_type": "attack",
                    "card_id": minion_id,
                    "target_ids": [target],
                    "attacker_index": idx,
                    "extra": {}
                })
            actions.append({
                "action_type": "attack",
                "card_id": minion_id,
                "target_ids": [],
                "attacker_index": idx,
                "extra": {}
            })
    # 3. 进化/超进化
    # 只要本回合已经evo或sevo过，所有进化动作都不再枚举
    if not getattr(state, "evo_or_sevo_used", False):
        for minion_id in getattr(state, 'own_minion_ids', []):
            # evo
            if getattr(state, 'e_value', 0) > 0:
                if not hasattr(state, "used_evo_ids"):
                    state.used_evo_ids = set()
                if minion_id in state.used_evo_ids:
                    continue
                evo_base = None
                for action in all_action_vars:
                    if action.get("action_type") == "evo" and action.get("card_id") == minion_id:
                        evo_base = action
                        break
                idx = state.own_minion_ids.index(minion_id)
                if evo_base:
                    new_evo = evo_base.copy()
                    new_evo["attacker_index"] = idx
                    actions.append(new_evo)
                else:
                    actions.append({
                        "action_type": "evo",
                        "card_id": minion_id,
                        "attacker_index": idx,
                        "extra": {}
                    })
            # sevo
            if getattr(state, 'se_value', 0) > 0:
                if not hasattr(state, "used_sevo_ids"):
                    state.used_sevo_ids = set()
                if minion_id in state.used_sevo_ids:
                    continue
                sevo_base = None
                for action in all_action_vars:
                    if action.get("action_type") == "sevo" and action.get("card_id") == minion_id:
                        sevo_base = action
                        break
                idx = state.own_minion_ids.index(minion_id)
                if sevo_base:
                    new_sevo = sevo_base.copy()
                    new_sevo["attacker_index"] = idx
                    actions.append(new_sevo)
                else:
                    actions.append({
                        "action_type": "sevo",
                        "card_id": minion_id,
                        "attacker_index": idx,
                        "extra": {}
                    })
    # 4. 结束回合
    actions.append({
        "action_type": "end_turn"
    })
    return actions

# ===== 自定义评分函数与AI循环 =====
def custom_evaluate_state(prev_state, new_state, return_detail=False):
    """
    评分函数，基于变量变化和权重。
    e、se为本回合消耗量，系数为负；hand为手牌数变化，少了减分多了加分。
    return_detail: 若为True，返回(总分, 评分项字典)
    """
    # 变量定义
    dmg = 20 - new_state.opponent_hp
    eatk = sum(new_state.opponent_minion_attack) if hasattr(new_state, "opponent_minion_attack") else 0
    edef = sum(new_state.opponent_minion_health) if hasattr(new_state, "opponent_minion_health") else 0
    matk = sum(new_state.own_minion_attack) if hasattr(new_state, "own_minion_attack") else 0
    mdef = sum(new_state.own_minion_health) if hasattr(new_state, "own_minion_health") else 0
    heal = max(0, new_state.player_hp - prev_state.player_hp)  # 我方主战者回复
    hand = (len(new_state.hand_card_ids) - len(prev_state.hand_card_ids)) if hasattr(new_state, "hand_card_ids") else 0
    # e、se为消耗量（用前-后，消耗为正数）
    e = max(0, prev_state.e_value - new_state.e_value) if hasattr(prev_state, "e_value") and hasattr(new_state, "e_value") else 0
    se = max(0, prev_state.se_value - new_state.se_value) if hasattr(prev_state, "se_value") and hasattr(new_state, "se_value") else 0

    detail = {
        'dmg': (dmg, 0.027 * (dmg ** 2)),
        'eatk': (eatk, -2 * eatk),
        'edef': (edef, -1.5 * edef),
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

def enumerate_all_action_paths(state, path=None, max_depth=20, debug_depth=0, visited=None):
    """
    穷举所有动作路径（以end_turn为终点），返回所有路径及其最终状态。
    增加死锁/未推进剪枝、递归深度警告和调试信息。
    """
    from copy import deepcopy
    if path is None:
        path = []
    if visited is None:
        visited = set()
    if max_depth <= 0:
        # print(f"[警告] 超过最大递归深度，剪枝！当前路径长度: {len(path)}，动作序列: {path}")
        return []
    actions = enumerate_all_possible_actions(state)
    if not any(a.get("action_type") == "end_turn" for a in actions):
        actions.append({"action_type": "end_turn", "extra": {}})
    results = []
    state_snapshot = str([
        getattr(state, 'hand_card_ids', []),
        getattr(state, 'own_minion_ids', []),
        getattr(state, 'own_minion_attack', []),
        getattr(state, 'own_minion_health', []),
        getattr(state, 'own_minion_follows', []),
        getattr(state, 'own_minion_evo', []),
        getattr(state, 'opponent_minion_attack', []),
        getattr(state, 'opponent_minion_health', []),
        getattr(state, 'opponent_minion_taunt', []),
        getattr(state, 'player_hp', None),
        getattr(state, 'opponent_hp', None),
        getattr(state, 'mana', None),
        getattr(state, 'e_value', None),
        getattr(state, 'se_value', None),
        getattr(state, 'graveyard_count', None),
        getattr(state, 'PP1', None)
    ])
    visit_key = state_snapshot  # 只用状态，不加深度
    if visit_key in visited:
        # print(f"[全局剪枝] 状态重复，路径终止，深度: {debug_depth}，动作序列: {path}")
        return []
    visited.add(visit_key)
    for action in actions:
        if debug_depth < 3:
            print(f"[递归] 深度: {debug_depth}，动作: {action}")
        if action.get("action_type") == "end_turn":
            sim_state = deepcopy(state)
            execute_action(action, sim_state)
            results.append((path + [action], sim_state))
        else:
            sim_state = deepcopy(state)
            execute_action(action, sim_state)
            sub_results = enumerate_all_action_paths(sim_state, path + [action], max_depth-1, debug_depth=debug_depth+1, visited=visited)
            # 类型防御：只允许list类型
            if not isinstance(sub_results, list):
                # print(f'[警告] 递归返回非list类型: {type(sub_results)}, 已丢弃')
                sub_results = []
            results.extend(sub_results)
    return results if isinstance(results, list) else []

def exhaustive_ai_search(state):
    """
    穷举所有动作路径，输出每条路径及评分，找出最优路径，并记录前三优路径。
    带穷举进度条。
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
    #     # 构造测试state
    #     class DummyState:
    #         def __init__(self):
    #             self.hand_card_ids = ["盛燃的魔劍‧歐特魯斯", "死神挥镰", "蝙蝠"]
    #             self.mana = 5
    #             self.graveyard_count = 5
    #             self.own_minion_ids = ["妖惑魅魔‧莉莉姆", "不屈的剑斗士"]
    #             self.own_minion_attack = [1, 2]
    #             self.own_minion_health = [1, 2]
    #             self.own_minion_follows = ["dash", "dash"]
    #             self.own_minion_evo = ["normal", "normal"]
    #             self.own_minion_count = 2
    #             self.opponent_minion_attack = [3, 2]
    #             self.opponent_minion_health = [2, 4]
    #             self.opponent_minion_taunt = [True, False]
    #             self.opponent_minion_count = 2
    #             self.player_hp = 18
    #             self.opponent_hp = 15
    #             self.e_value = 1
    #             self.se_value = 0
    #             self.PP1 = 0
    #             self.hand_card_count = 3
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
    all_paths = enumerate_all_action_paths(state, visited=None)
    if not isinstance(all_paths, list):
        # print(f"[错误] all_paths 类型异常: {type(all_paths)}，值: {all_paths}")
        return
    scored_paths = []
    total = len(all_paths)
    print(f"\n【穷举路径总数】：{total}")
    import copy
    for idx, item in enumerate(all_paths, 1):
        if not (isinstance(item, tuple) and len(item) == 2):
            # print(f"[警告] 路径数据异常，已跳过: {item}")
            continue
        path, final_state = item
        # 评分
        try:
            init_state_for_score = copy.deepcopy(state)
            result = custom_evaluate_state(init_state_for_score, final_state, return_detail=True)
            if isinstance(result, tuple) and len(result) == 2:
                score, detail = result
            else:
                score, detail = result, {}
        except Exception as e:
            # print(f"[警告] 评分异常，已跳过: {item}, 错误: {e}")
            continue
        scored_paths.append((score, path, final_state, detail))
        # 进度条
        if total > 0:
            percent = idx / total * 100
            bar_len = 30
            filled_len = int(bar_len * idx // total)
            bar = '█' * filled_len + '-' * (bar_len - filled_len)
            print(f"\r[进度] |{bar}| {idx}/{total} ({percent:.1f}%)", end='')
    print()  # 换行
    # 按分数排序
    scored_paths = [x for x in scored_paths if isinstance(x, tuple) and len(x) == 4]
    scored_paths.sort(reverse=True, key=lambda x: float(x[0]))
    for i, item in enumerate(scored_paths):
        if not (isinstance(item, tuple) and len(item) == 4):
            # print(f"[警告] scored_paths数据异常，已跳过: {item}")
            continue
        score, path, final_state, detail = item
        # print(f"\n路径{i+1}，评分：{score:.2f}")
        for step, action in enumerate(path):
            print(f"  {step+1}. {action}")
        # 输出详细评分
        # print("  [详细评分]")
        # for k, (v, s) in detail.items():
        #     print(f"    {k}: {v} -> {s:.2f}")
    if scored_paths:
        print("\n【最优路径】")
        best_score, best_path, best_state, best_detail = scored_paths[0]
        for step, action in enumerate(best_path):
            print(f"  {step+1}. {action}")
        print(f"最终评分：{best_score:.2f}")
        # print("[详细评分]")
        # for k, (v, s) in best_detail.items():
        #     print(f"  {k}: {v} -> {s:.2f}")
        if hasattr(best_state, "print_state"): best_state.print_state()
        # 记录前三优路径
        # print("\n【前三优路径】")
        # for rank, item in enumerate(scored_paths[:3], 1):
        #     if not (isinstance(item, tuple) and len(item) == 4):
        #         print(f"[警告] scored_paths数据异常，已跳过: {item}")
        #         continue
        #     score, path, final_state, detail = item
        #     print(f"\n第{rank}优路径，评分：{score:.2f}")
        #     for step, action in enumerate(path):
        #         print(f"  {step+1}. {action}")
        #     print("  [详细评分]")
        #     for k, (v, s) in detail.items():
        #         print(f"    {k}: {v} -> {s:.2f}")
        #     if hasattr(final_state, "print_state"):
        #         print("  [最终状态]")
        #         final_state.print_state()
    else:
        print("未找到可行路径！")
    end_time = time.time()
    print(f"\n【穷举搜索总用时】{end_time - start_time:.3f} 秒")
    if scored_paths:
        print("\n【最优路径动作序列】")
        best_score, best_path, best_state, best_detail = scored_paths[0]
        for i, action in enumerate(best_path):
            print(f"  {i+1}. {action}")
        print(f"\n最终评分：{best_score:.2f}")
        # print("[详细评分]")
        # for k, (v, s) in best_detail.items():
        #     print(f"  {k}: {v} -> {s:.2f}")
        if hasattr(best_state, "print_state"):
            best_state.print_state()
        # 返回最优路径和初始state，便于现实复现
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
#         def __init__(self):
#             self.hand_card_ids = ["盛燃的魔劍‧歐特魯斯", "反转互换", "蛇神的嗔怒"]
#             self.mana = 5
#             self.graveyard_count = 5
#             self.own_minion_ids = ["妖惑魅魔‧莉莉姆", "不屈的剑斗士"]
#             self.own_minion_attack = [1, 2]
#             self.own_minion_health = [1, 2]
#             self.own_minion_follows = ["dash", "dash"]
#             self.own_minion_evo = ["normal", "normal"]
#             self.own_minion_count = 2
#             self.opponent_minion_attack = [3, 2]
#             self.opponent_minion_health = [2, 5]
#             self.opponent_minion_taunt = [True, False]
#             self.opponent_minion_count = 2
#             self.player_hp = 18
#             self.opponent_hp = 15
#             self.e_value = 1
#             self.se_value = 0
#             self.PP1 = 0
#             self.hand_card_count = 3
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