# card_evaluator.py

class CardScorer:
    def __init__(self, base_card_scores, card_condition_rules):
        self.base_card_scores = base_card_scores
        self.card_condition_rules = card_condition_rules
        self._validate_conditions()

    def _validate_conditions(self):
        """
        验证所有条件字典是否包含必要的键。
        """
        for card_name, conditions in self.card_condition_rules.items():
            for condition in conditions:
                if 'type' not in condition:
                    raise ValueError(f"Condition for card '{card_name}' is missing 'type' key.")
                if 'operator' not in condition:
                    raise ValueError(f"Condition for card '{card_name}' is missing 'operator' key.")
                if 'param_index' not in condition and condition['type'] != 'mana':
                    print(f"Warning: Condition for card '{card_name}' is missing 'param_index' key. Setting default to 0.")
                    condition['param_index'] = 0
                if 'threshold' not in condition:
                    print(f"Warning: Condition for card '{card_name}' is missing 'threshold' key. Setting default to 0.")
                    condition['threshold'] = 0
                if 'adjustment' not in condition:
                    print(f"Warning: Condition for card '{card_name}' is missing 'adjustment' key. Setting default to 0.")
                    condition['adjustment'] = 0

    def score_card(self, card_name, state, condition_params):
        """
        计算卡牌的评分。

        :param card_name: 卡牌名称。
        :param state: 当前游戏状态对象。
        :param condition_params: 元组，包含用于条件判断的参数。
        :return: 卡牌评分。
        """
        base_score = self.base_card_scores.get(card_name, 0)
        total_score = base_score
        
        if card_name in self.card_condition_rules:
            for rule in self.card_condition_rules[card_name]:
                
                if rule['type'] == 'mana':
                    # 获取条件参数中的值，索引由 rule['param_index'] 指定
                    value = condition_params[rule['param_index']]
                    # 根据不同的操作符调整分数
                    if rule['operator'] == '=' and value == rule['threshold']:
                        total_score += rule['adjustment']
                        
                    elif rule['operator'] == '<' and value < rule['threshold']:
                        total_score += rule['adjustment']
                        
                    elif rule['operator'] == '>' and value > rule['threshold']:
                        total_score += rule['adjustment']

                    elif rule['operator'] == '>=' and value >= rule['threshold']:
                        total_score += rule['adjustment']
                        
                    elif rule['operator'] == '<=' and value <= rule['threshold']:
                        total_score += rule['adjustment']
                        
                
                elif rule['type'] == 'opponent_hp':
                    # 获取条件参数中的值，索引由 rule['param_index'] 指定
                    value = condition_params[rule['param_index']]
                    
                    
                    # 根据不同的操作符调整分数
                    if rule['operator'] == '<' and value < rule['threshold']:
                        total_score += rule['adjustment']
                        
                    elif rule['operator'] == '>' and value > rule['threshold']:
                        total_score += rule['adjustment']
                        
                    elif rule['operator'] == '>=' and value >= rule['threshold']:
                        total_score += rule['adjustment']
                        
                    elif rule['operator'] == '<=' and value <= rule['threshold']:
                        total_score += rule['adjustment']
                        
                
                elif rule['type'] == 'enemy_minion_attack_and_health':
                    # 调整分数根据敌方随从的攻击力和生命值
                    adjustment = self._adjust_enemy_minion_attack_and_health(rule, state.enemy_minion_health_values, state.enemy_minion_attack_values)
                    total_score += adjustment
                    
                
                elif rule['type'] == 'enemy_minion_health':
                    # 调整分数根据敌方随从的生命值
                    adjustment = self._adjust_enemy_minion_health(rule, state.enemy_minion_health_values)
                    total_score += adjustment
                    
                
                elif rule['type'] == 'dash_attack_total':
                    # 调整分数根据我方 dash 状态随从总攻击力
                    adjustment = self._adjust_dash_attack_total(rule, state.minion_attack_values, state.my_followers, condition_params)
                    total_score += adjustment
                
        return total_score

    def _adjust_enemy_minion_attack_and_health(self, condition, enemy_minion_health_values, enemy_minion_attack_values):
        """
        根据敌方随从攻击力和生命值条件调整分数。

        :param condition: 条件字典。
        :param enemy_minion_health_values: 敌方随从的生命值列表。
        :param enemy_minion_attack_values: 敌方随从的攻击力列表。
        :return: 调整值。
        """
        adjustment = 0
        threshold = condition.get('threshold', 0)  # 默认阈值为 0
        adjustment_value = condition.get('adjustment', 0)  # 默认调整值为 0

        for health, attack in zip(enemy_minion_health_values, enemy_minion_attack_values):
            try:
                health = int(health)
                attack = int(attack)
                if health > threshold and attack > threshold:
                    adjustment += adjustment_value
            except ValueError:
                print(f"Invalid value encountered: health={health}, attack={attack}. Skipping this minion.")
        return adjustment

    def _adjust_enemy_minion_health(self, condition, enemy_minion_health_values):
        """
        根据敌方随从生命值条件调整分数。

        :param condition: 条件字典。
        :param enemy_minion_health_values: 敌方随从的生命值列表。
        :return: 调整值。
        """
        adjustment = 0
        threshold = condition.get('threshold', 0)  # 默认阈值为 0
        adjustment_value = condition.get('adjustment', 0)  # 默认调整值为 0

        for health in enemy_minion_health_values:
            try:
                health = int(health)
                if health == threshold:
                    adjustment += adjustment_value
            except ValueError:
                print(f"Invalid value encountered: health={health}. Skipping this minion.")
        return adjustment

    def _adjust_dash_attack_total(self, condition, minion_attack_values, my_followers, condition_params):
        """
        根据我方 dash 状态随从总攻击力条件调整分数。

        :param condition: 条件字典。
        :param minion_attack_values: 我方随从的攻击力列表。
        :param my_followers: 我方随从的状态列表。
        :param condition_params: 元组，包含用于条件判断的参数。
        :return: 调整值。
        """
        dash_attack_total = sum(
            int(minion_attack_values[i])
            for i, status in enumerate(my_followers)
            if status == 'dash'
        )
        opponent_hp = condition_params[condition['param_index']]  # param_index2 should be opponent HP
        threshold = condition.get('threshold', 0)  # 默认阈值为 0
        adjustment_value = condition.get('adjustment', 0)  # 默认调整值为 0

        if opponent_hp - dash_attack_total <= threshold:
            return adjustment_value
        return 0



