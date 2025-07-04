# game_state.py

class GameState:
    def __init__(self):
        self.mana = 0              # 当前法力值
        self.card_num = 0          # 手牌数量
        self.player_hp = 0         # 玩家生命值
        self.opponent_hp = 0       # 对手生命值
        self.hand_cards = []       # 手牌名称列表
        self.minion_count = 0      # 随从数量（我方）
        self.enemy_minion_count = 0 # 随从数量（敌方）
        self.minion_names = []     # 战场随从名称列表（我方）
        self.enemy_minion_names = [] # 战场随从名称列表（敌方）
        self.minion_positions = [] # 战场随从位置列表（我方）
        self.enemy_minion_positions = [] # 战场随从位置列表（敌方）
        self.minion_attack_values = []  # 攻击力列表（我方）
        self.minion_health_values = []  # 生命值列表（我方）
        self.enemy_minion_attack_values = []  # 攻击力列表（敌方）
        self.enemy_minion_health_values = []  # 生命值列表（敌方）
        self.my_followers = []     # 新增：己方随从状态
        self.enemy_followers = []  # 新增：敌方随从状态
        self.hand_card_scores = {} # 新增：手牌评分列表

    def print_state(self):
        """
        打印游戏状态的所有信息。
        """
        print("=== 游戏状态 ===")
        print(f"Mana: {self.mana}")
        print(f"Card Number: {self.card_num}")
        print(f"Player HP: {self.player_hp}")
        print(f"Opponent HP: {self.opponent_hp}")
        print("\n--- 手牌 ---")
        if self.hand_cards:
            for idx, card in enumerate(self.hand_cards):
                score = self.hand_card_scores.get(card, "未评分")
                print(f"{idx + 1}. {card} - 评分: {score}")
        else:
            print("没有手牌")
        print("\n--- 我方随从 ---")
        if self.minion_count > 0:
            for i in range(self.minion_count):
                print(f"随从 {i + 1}: 名称={self.minion_names[i]}, "
                      f"位置={self.minion_positions[i]}, "
                      f"攻击力={self.minion_attack_values[i]}, "
                      f"生命值={self.minion_health_values[i]}, "
                      f"状态={self.my_followers[i] if i < len(self.my_followers) else '未知'}")
        else:
            print("没有我方随从")
        print("\n--- 敌方随从 ---")
        if self.enemy_minion_count > 0:
            for i in range(self.enemy_minion_count):
                print(f"随从 {i + 1}: 名称={self.enemy_minion_names[i]}, "
                      f"位置={self.enemy_minion_positions[i]}, "
                      f"攻击力={self.enemy_minion_attack_values[i]}, "
                      f"生命值={self.enemy_minion_health_values[i]}, "
                      f"状态={self.enemy_followers[i] if i < len(self.enemy_followers) else '未知'}")
        else:
            print("没有敌方随从")

    def set_hand_card_scores(self, scores):
        """
        设置手牌评分。

        :param scores: 字典，包含每张手牌的评分。
        """
        self.hand_card_scores = scores
    
    def update_minion_attributes(self):
        """
        将 None 的攻击力和生命值替换为 0。
        """
        self.minion_attack_values = [attack if attack is not None else 0 for attack in self.minion_attack_values]
        self.minion_health_values = [health if health is not None else 0 for health in self.minion_health_values]
        self.enemy_minion_attack_values = [attack if attack is not None else 0 for attack in self.enemy_minion_attack_values]
        self.enemy_minion_health_values = [health if health is not None else 0 for health in self.enemy_minion_health_values]    