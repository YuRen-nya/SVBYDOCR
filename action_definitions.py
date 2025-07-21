# action_definitions.py
"""
标准Action字典结构模板
每个字段均有详细注释，注明可取值范围。

结构说明：
- 一张卡牌 = 一个 actions 列表
- 每个 ability/触发点 = 一个 action 字典
  （即：如果一张卡有多个能力，如入场曲、进化时等，每个能力单独写一个 action 字典）
- 如果某个能力有多个目标/多步动作，也可以拆分为多个 action 字典（视具体需求）
"""
# # Action结构示例
# ACTION_TEMPLATE = {
#     "action_type": "play_card",  # 动作类型，可取值：
#                                    #   'play_card'（出牌）
#                                    #   'attack'（攻击）
#                                    #   'evo'（进化）
#                                    #   'sevo'（超进化）
#                                    #   'activate_ability'（主动技能）
#                                    #   'end_turn'（结束回合）

#     # 出牌相关字段
#     "card_id": None,              # 卡牌ID，仅'play_card'时需要，字符串，如'fireball_001'
#     "cost": None,                 # 法力消耗，仅'play_card'时需要，int
#     "attack": None,               # 基础攻击力，仅随从卡需要，int
#     "health": None,               # 基础生命值，仅随从卡需要，int
#     "mode": None,                 # 出牌/技能模式，可取值：'normal'、'buffed'等，字符串或None

#     # 攻击/进化/技能相关字段
#     "card_id": None,             # 执行动作的随从或卡牌ID，'attack'/'evo'/'sevo'/'activate_ability'时需要，字符串
#     "target_ids": None,           # 目标ID列表，list[str]，可为[]或None，表示无目标/空目标

#     # 主动技能相关字段
#     "ability_id": None,           # 主动技能唯一标识，仅'activate_ability'时需要，字符串

#     # 其他扩展参数
#     "extra": {},                  # 扩展参数，dict，可用于自动化操作、特殊消耗等
# }

# ===== 蝙蝠 =====
action_play_bat = {
    "action_type": "play_card",
    "card_id": "蝙蝠",
    "cost": 1,
    "attack": 1,
    "health": 1,
    "mode": "normal",
    "target_ids": [],
    "extra": {}
}

# ===== 怨靈 =====
action_play_grudge = {
    "action_type": "play_card",
    "card_id": "怨靈",
    "cost": 1,
    "attack": 1,
    "health": 1,
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "keyword": ["dash"],
        "end_of_own_turn": {"effect": "vanish_self"}
    }
}

# ===== 妖惑魅魔‧莉莉姆 =====
action_play_lilim = {
    "action_type": "play_card",
    "card_id": "妖惑魅魔‧莉莉姆",
    "cost": 1,
    "attack": 1,  # 假设攻击力为1，请根据实际修改
    "health": 1,  # 假设生命值为1，请根据实际修改
    "mode": "normal",
    "target_ids": [],
    "extra": {}
}

action_deathrattle_lilim = {
    "action_type": "activate_ability",
    "card_id": "妖惑魅魔‧莉莉姆",
    "ability_id": "deathrattle_add_bat",
    "target_ids": [],
    "extra": {
        "effect": "add_card_to_hand",
        "card_id": "蝙蝠",
        "count": 1
    }
}

# ===== 怨恨的栽培者 =====
action_play_grudgeplanter = {
    "action_type": "play_card",
    "card_id": "怨恨的栽培者",
    "cost": 1,  # 请根据实际费用修改
    "attack": 1,  # 假设攻击力为1，请根据实际修改
    "health": 1,  # 假设生命值为1，请根据实际修改
    "mode": "normal",
    "target_ids": [],
    "extra": {}
}

action_deathrattle_grudgeplanter = {
    "action_type": "activate_ability",
    "card_id": "怨恨的栽培者",
    "ability_id": "deathrattle_add_grudge",
    "target_ids": [],
    "extra": {
        "effect": "add_card_to_hand",
        "card_id": "怨灵",
        "count": 1
    }
}

# ===== 死神挥镰 =====
action_play_reaper_scythe = {
    "action_type": "play_card",
    "card_id": "死神挥镰",
    "cost": 1,           # 请根据实际费用填写
    "attack": None,      # 法术卡无攻击力
    "health": None,      # 法术卡无生命值
    "mode": "spell",   # 标明是法术
    "target_ids": ["my_minion_id", "enemy_minion_id"],  # 先我方，后敌方
    "extra": {
        "effect": "destroy_both",
        "target_order": ["self", "enemy"]  # 可选，说明目标顺序
    }
}

# ===== 不屈的剑斗士 =====
action_play_undefeated_gladiator = {
    "action_type": "play_card",
    "card_id": "不屈的剑斗士",
    "cost": 2,
    "attack": 2,
    "health": 2,
    "mode": "normal",
    "target_ids": [],
    "extra": {}
}

action_burst_undefeated_gladiator = {
    "action_type": "play_card",
    "card_id": "不屈的剑斗士",
    "cost": 4,
    "attack": 5,  # 2+3
    "health": 5,  # 2+3
    "mode": "normal",  # 标明是爆能强化4
    "target_ids": [],
    "extra": {
        "effect": "buff_self",
        "buff_attack": 3,
        "buff_health": 3,
        "burst_cost": 4
    }
}

# ===== 反转互换 =====
action_play_inversion_swap_template = {
    "action_type": "play_card",
    "card_id": "反转互换",
    "cost": 2,           # 请根据实际费用修改
    "attack": None,      # 法术卡无攻击力
    "health": None,      # 法术卡无生命值
    "mode": "spell",
    # "target_info": {"side": "own"/"opponent", "index": 0}, # 枚举时生成
    "extra": {
        "effect": "buff_target",
        "buff_attack": 2,
        "buff_health": -2
    }
}

# ===== 凶恶的小木乃伊 =====
action_play_fierce_mummy = {
        "action_type": "play_card",
    "card_id": "凶恶的小木乃伊",
    "cost": 2,         # 请根据实际费用修改
    "attack": 2,       # 请根据实际攻击力修改
    "health": 2,       # 请根据实际生命值修改
    "mode": "normal",
    "target_ids": [],
        "extra": {}
}

action_necro_fierce_mummy = {
    "action_type": "play_card",
    "card_id": "凶恶的小木乃伊",
    "cost": 2,         # 死灵术消耗不影响费用
    "attack": 2,
    "health": 2,
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "effect": "gain_keyword",
        "keyword": "疾驰",
        "necro_cost": 4
    }
}

# ===== 夢魔‧維莉 =====
action_play_dream_demon_vili = {
    "action_type": "play_card",
    "card_id": "夢魔‧維莉",
    "cost": 2,
    "attack": 3,
    "health": 3,
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "fanfare": {
            "effect": "damage_leader",
            "target": "player",
            "value": 3
        }
    }
}

action_evo_dream_demon_vili = {
    "action_type": "evo",
    "card_id": "夢魔‧維莉",
    "target_ids": ["player"],
    "extra": {
        "effect": "heal_leader",
        "value": 5
    }
}

# ===== 盛燃的魔劍‧歐特魯斯 =====
action_play_outrous = {
    "action_type": "play_card",
    "card_id": "盛燃的魔劍‧歐特魯斯",
    "cost": 2,  
    "attack": 2,  
    "health": 2,  
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "fanfare": {
            "effect": "add_graveyard",
            "target": "self",
            "value": 2
        },
        "keyword": ["守护"]
    }
}

action_evo_outrous = {
    "action_type": "evo",
    "card_id": "盛燃的魔劍‧歐特魯斯",
    "target_ids": ["random_enemy_minion", "random_enemy_minion"],
    "extra": {
        "effect": "random_damage",
        "value": 2,
        "repeat": 2,
        "necro_cost": 4
    }
}

# ===== 蛇神的嗔怒 =====
action_play_serpent_anger_template = {
    "action_type": "play_card",
    "card_id": "蛇神的嗔怒",
    "cost": 2,           # 请根据实际费用修改
    "attack": None,      # 法术卡无攻击力
    "health": None,      # 法术卡无生命值
    "mode": "spell",
    # "target_info": {"side": "opponent", "index": 0} 或 {"side": "opponent_leader"}
    "extra": {
        "effect": [
            {"type": "damage", "target": "target", "value": 3},
            {"type": "damage", "target": "self_leader", "value": 2}
        ]
    }
}

# ===== 役使蝙蝠 =====
action_play_bat_servant = {
    "action_type": "play_card",
    "card_id": "役使蝙蝠",
    "cost": 2,           # 请根据实际费用修改
    "attack": None,      # 法术卡无攻击力
    "health": None,      # 法术卡无生命值
    "mode": "spell",
    "target_ids": [],
    "extra": {
        "effect": "summon",
        "summon_card_id": "蝙蝠",
        "count": 2
    }
}

# ===== 暗夜鬼人 =====
action_play_night_ogre = {
    "action_type": "play_card",
    "card_id": "暗夜鬼人",
    "cost": 3,
    "attack": 4,
    "health": 3,
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "fanfare": {
            "effect": "damage_leader",
            "target": "player",
            "value": 1
        }
    }
}

# ===== 法外的賞金獵人‧巴爾特 =====
action_play_bart_bountyhunter = {
    "action_type": "play_card",
    "card_id": "法外的賞金獵人‧巴爾特",
    "cost": 3,
    "attack": 5,
    "health": 1,
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "fanfare": {
            "effect": "end_of_turn_trigger",
            "actions": [
                {"type": "damage", "target": "all_leader", "value": 1}
            ]
        }
    }
}

# ===== 暮夜魔將‧艾瑟菈 =====
action_play_night_general_ethera = {
    "action_type": "play_card",
    "card_id": "暮夜魔將‧艾瑟菈",
    "cost": 4,
    "attack": 1,  # 基础攻击力
    "health": 3,  # 基础生命值
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "fanfare": [
            {
                "effect": "buff_self_dynamic",
                "buff_attack": "other_follower_count",
                "buff_health": 0
            },
            {
                "effect": "damage_leader",
                "target": "player",
                "value": 2
            }
        ],
        "keyword": ["疾驰"]
    }
}

# ===== 無盡獵人‧阿拉加維 =====
action_play_endless_hunter_aragavy = {
    "action_type": "play_card",
    "card_id": "無盡獵人‧阿拉加維",
    "cost": 5,
    "attack": 4,
    "health": 3,
    "mode": "normal",
    "target_ids": [],
    "extra": {
        "fanfare": {
            "effect": "distribute_damage",
            "target": "all_enemy_minion",
            "value": 7
        }
    }
}

action_evo_endless_hunter_aragavy = {
    "action_type": "evo",
    "card_id": "無盡獵人‧阿拉加維",
    "target_ids": ["all_leader"],
    "extra": {
        "effect": "damage_leader",
        "value": 3
    }
}
