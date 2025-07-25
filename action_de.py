"""
标准字典
"卡牌名":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 0202,
            "play_target_1":{
                "target_area1": False,我方主战者
                "target_area2": False,我方随从区域
                "target_area3": False,敌方主战者
                "target_area4": False,敌方随从区域
            },
                如果你不写 play_target_1，该卡就不会被枚举为可出牌动作。
                不会报错，但会导致该卡“永远不能出牌”。
                如果你希望“无目标出牌”也能被枚举，必须写 play_target_1，并设置所有 target_areaX 为 False，同时 play_less_target_use_able 设为 True。
            "play_target_2":{
                "target_area1": False,我方主战者
                "target_area2": False,我方随从区域
                "target_area3": False,敌方主战者
                "target_area4": False,敌方随从区域
            },如果有，按照该命名格式添加
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",  # 目标模式
                # 可选值：
                # "ordered_unique"   有序不可重复（如[甲,乙]和[乙,甲]不同，且不能重复）
                # "ordered_repeat"   有序可重复（如[甲,甲]合法）
                # "unordered_unique" 无序不可重复（如[甲,乙]和[乙,甲]视为同一组，且不能重复）
                # "unordered_repeat" 无序可重复（如[甲,甲]合法，[甲,乙]和[乙,甲]视为同一组）
        },
        "Play_Card_mode": {}额外的出牌方式，例如爆能，死灵术等
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["**"]},如果有
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e卡牌名",
            "evo_target":{
                "target_area1": False,我方主战者
                "target_area2": False,我方随从区域
                "target_area3": False,敌方主战者
                "target_area4": False,敌方随从区域
            },如果有
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e卡牌名",
            "sevo_target":{
                "target_area1": False,我方主战者
                "target_area2": False,我方随从区域
                "target_area3": False,敌方主战者
                "target_area4": False,敌方随从区域
            },如果有
        },
        "End_Turn_Card": {}
        }
"""
from re import T


actions_d = {
    "蝙蝠":{
        "Play_Card": {
            "play_cost": 1,
            "play_value": 101,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["吸血"]},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e蝙蝠",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"se蝙蝠",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e蝙蝠":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["吸血"]},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "怨靈":{
        "Play_Card": {
            "play_cost": 1,
            "play_value": 101,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["dash"]},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e怨靈",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e怨靈",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {"exile_self":True},
    },
    "e怨靈":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["dash"]},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {"exile_self":True},
    },

    "妖惑魅魔‧莉莉姆":{
        "Play_Card": {
            "play_cost": 1,
            "play_value": 101,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {"handcard_add":"蝙蝠"},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e妖惑魅魔‧莉莉姆",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e妖惑魅魔‧莉莉姆",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e妖惑魅魔‧莉莉姆":{
        "Play_Card": {},
        "Die_Card": {
            "handcard_add":"蝙蝠"
        },
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "怨恨的栽培者":{
        "Play_Card": {
            "play_cost": 1,
            "play_value": 101,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
        },
        "Die_Card": {"handcard_add":"怨靈"},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e怨恨的栽培者",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e怨恨的栽培者",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e怨恨的栽培者":{
        "Play_Card": {},
        "Die_Card": {"handcard_add":"怨靈"},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "死神挥镰":{
        "Play_Card": {
            "play_cost": 1,
            "play_value": 0,
            "play_target_1":{
                "target_area1": False,
                "target_area2": True,
                "target_area3": False,
                "target_area4": False,
            },
            "play_target_2":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": True,
            },
            "play_less_target_use_able": False,
            "target_mode": "ordered_unique"
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {},
        "Sevo_Card": {},
        "End_Turn_Card": {},
    },

    "不屈的剑斗士":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 202,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Play_Card_1_burst": {
            "play_cost": 4,
            "play_value": 505,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e不屈的剑斗士",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e不屈的剑斗士",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e不屈的剑斗士":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "反转互换":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 0,
            "play_target_1":{
                "target_area1": False,
                "target_area2": True,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": False,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {},
        "Sevo_Card": {},
        "End_Turn_Card": {},
    },

    "凶恶的小木乃伊":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 202,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Play_Card_1_necro": {
            "play_cost": 2,
            "play_value": 202,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },# 死灵术召唤给dash，在实现的时候根据前缀play和后缀necro与卡名来判断
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e凶恶的小木乃伊",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e凶恶的小木乃伊",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e凶恶的小木乃伊":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "夢魔‧維莉":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 303,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e夢魔‧維莉",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e夢魔‧維莉",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e夢魔‧維莉":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "盛燃的魔劍‧歐特魯斯":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 202,
            "play_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["守护"]},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e盛燃的魔劍‧歐特魯斯",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e盛燃的魔劍‧歐特魯斯",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e盛燃的魔劍‧歐特魯斯":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["守护"]},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "蛇神的嗔怒":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 0,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": True,
                "target_area4": True,
            },
            "play_less_target_use_able": False,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {},
        "Sevo_Card": {},
        "End_Turn_Card": {},
    },

    "役使蝙蝠":{
        "Play_Card": {
            "play_cost": 2,
            "play_value": 0,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {},
        "Sevo_Card": {},
        "End_Turn_Card": {},
    },
    
    "暗夜鬼人":{
        "Play_Card": {
            "play_cost": 3,
            "play_value": 403,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e暗夜鬼人",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e暗夜鬼人",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
            "End_Turn_Card": {},
    },
    "e暗夜鬼人":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "法外的賞金獵人‧巴爾特":{
        "Play_Card": {
            "play_cost": 3,
            "play_value": 301,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e法外的賞金獵人‧巴爾特",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e法外的賞金獵人‧巴爾特",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e法外的賞金獵人‧巴爾特":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "暮夜魔將‧艾瑟菈":{
        "Play_Card": {
            "play_cost": 4,
            "play_value": 103,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["dash"]},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e暮夜魔將‧艾瑟菈",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e暮夜魔將‧艾瑟菈",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e暮夜魔將‧艾瑟菈":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {"keywords": ["dash"]},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "無盡獵人‧阿拉加維":{
        "Play_Card": {
            "play_cost": 5,
            "play_value": 403,
            "play_target_1":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "play_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": True,
            "evo_to":"e無盡獵人‧阿拉加維",
            "evo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "evo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "Sevo_Card": {
            "sevo_able": True,
            "sevo_to":"e無盡獵人‧阿拉加維",
            "sevo_target":{
                "target_area1": False,
                "target_area2": False,
                "target_area3": False,
                "target_area4": False,
            },
            "sevo_less_target_use_able": True,
            "target_mode": "ordered_unique",
        },
        "End_Turn_Card": {},
    },
    "e無盡獵人‧阿拉加維":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {
            "evo_able": False
        },
        "Sevo_Card": {
            "sevo_able": False
        },
        "End_Turn_Card": {},
    },

    "未知随从":{
        "Play_Card": {},
        "Die_Card": {},
        "Activate_Card": {},
        "Const_Card": {},
        "Evo_Card": {},
        "Sevo_Card": {},
        "End_Turn_Card": {},
    }
}