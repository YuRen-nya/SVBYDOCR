# rl_trainer.py
# 强化学习训练脚本
# 功能：训练价值函数和策略函数模型，用于强化学习决策

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import glob
import os

def load_training_data():
    """
    加载训练数据
    从带奖励的游戏数据文件中提取状态、行动和奖励信息
    
    Returns:
        tuple: (状态特征数组, 行动ID数组, 奖励数组) 或 None
    """
    data_files = glob.glob('data/game_data_*_with_rewards.json')
    
    if not data_files:
        print("未找到带奖励的数据文件，请先运行 rl_data_processor.py")
        return None
    
    all_states = []
    all_actions = []
    all_rewards = []
    
    for filename in data_files:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for action in data['actions']:
            state = action['game_state']
            
            # 特征工程：将状态转换为数值特征
            features = [
                state['player_hp'],                    # 玩家生命值
                state['opponent_hp'],                  # 对手生命值
                state['e_value'],                      # 能量值
                state['se_value'],                     # 特殊能量值
                len(state['hand_cards']),              # 手牌数量
                len(state['own_minions']),             # 我方随从数量
                len(state['opponent_minions']),        # 敌方随从数量
                sum(atk for atk, _ in state['own_minions']),      # 我方随从总攻击力
                sum(hp for _, hp in state['own_minions']),        # 我方随从总生命值
                sum(atk for atk, _ in state['opponent_minions']), # 敌方随从总攻击力
                sum(hp for _, hp in state['opponent_minions'])    # 敌方随从总生命值
            ]
            
            all_states.append(features)
            all_actions.append(action['action_id'])
            all_rewards.append(action['reward'])
    
    return np.array(all_states), np.array(all_actions), np.array(all_rewards)

def train_value_function(X, y):
    """
    训练价值函数模型
    使用随机森林回归器预测状态价值
    
    Args:
        X: 状态特征数组
        y: 奖励数组
    
    Returns:
        RandomForestRegressor: 训练好的价值函数模型
    """
    print("训练价值函数模型...")
    
    # 分割训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 训练随机森林模型
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # 评估模型
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"价值函数模型性能:")
    print(f"  MSE: {mse:.4f}")
    print(f"  R²: {r2:.4f}")
    
    return model

def train_policy_function(X, actions, rewards):
    """
    训练策略函数模型
    基于奖励选择最佳行动，训练策略预测模型
    
    Args:
        X: 状态特征数组
        actions: 行动ID数组
        rewards: 奖励数组
    
    Returns:
        RandomForestRegressor: 训练好的策略函数模型
    """
    print("训练策略函数模型...")
    
    # 为每个状态选择最佳行动（基于奖励）
    best_actions = []
    best_rewards = []
    
    # 按状态分组，选择奖励最高的行动
    state_action_rewards = {}
    for i, (state, action, reward) in enumerate(zip(X, actions, rewards)):
        state_key = tuple(state)
        if state_key not in state_action_rewards:
            state_action_rewards[state_key] = []
        state_action_rewards[state_key].append((action, reward))
    
    for state_key, action_rewards in state_action_rewards.items():
        # 选择奖励最高的行动
        best_action, best_reward = max(action_rewards, key=lambda x: x[1])
        best_actions.append(best_action)
        best_rewards.append(best_reward)
    
    best_actions = np.array(best_actions)
    best_rewards = np.array(best_rewards)
    
    # 训练策略模型
    X_train, X_test, y_train, y_test = train_test_split(X, best_actions, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # 评估模型
    y_pred = model.predict(X_test)
    accuracy = np.mean(np.round(y_pred) == y_test)
    
    print(f"策略函数模型性能:")
    print(f"  准确率: {accuracy:.4f}")
    
    return model

def save_models(value_model, policy_model):
    """
    保存训练好的模型
    将模型保存到data文件夹中，便于后续使用
    
    Args:
        value_model: 价值函数模型
        policy_model: 策略函数模型
    """
    # 确保data文件夹存在
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    value_model_path = os.path.join(data_dir, 'value_function_model.pkl')
    policy_model_path = os.path.join(data_dir, 'policy_function_model.pkl')
    
    joblib.dump(value_model, value_model_path)
    joblib.dump(policy_model, policy_model_path)
    print("模型已保存:")
    print(f"  - {value_model_path}")
    print(f"  - {policy_model_path}")

def create_feature_names():
    """
    创建特征名称列表
    用于特征重要性分析和模型解释
    
    Returns:
        list: 特征名称列表
    """
    return [
        'player_hp',                    # 玩家生命值
        'opponent_hp',                  # 对手生命值
        'e_value',                      # 能量值
        'se_value',                     # 特殊能量值
        'hand_cards_count',             # 手牌数量
        'own_minions_count',            # 我方随从数量
        'opponent_minions_count',       # 敌方随从数量
        'own_minions_total_atk',        # 我方随从总攻击力
        'own_minions_total_hp',         # 我方随从总生命值
        'opponent_minions_total_atk',   # 敌方随从总攻击力
        'opponent_minions_total_hp'     # 敌方随从总生命值
    ]

def analyze_feature_importance(model, feature_names):
    """
    分析特征重要性
    显示模型中各个特征的重要程度
    
    Args:
        model: 训练好的模型
        feature_names: 特征名称列表
    """
    importance = model.feature_importances_
    feature_importance = list(zip(feature_names, importance))
    feature_importance.sort(key=lambda x: x[1], reverse=True)
    
    print("\n特征重要性排序:")
    for feature, imp in feature_importance:
        print(f"  {feature}: {imp:.4f}")

def main():
    """
    主函数
    执行完整的强化学习模型训练流程
    """
    print("开始强化学习模型训练...")
    
    # 加载数据
    data = load_training_data()
    if data is None:
        return
    
    X, actions, rewards = data
    print(f"加载了 {len(X)} 个训练样本")
    
    # 特征名称
    feature_names = create_feature_names()
    
    # 训练价值函数
    value_model = train_value_function(X, rewards)
    analyze_feature_importance(value_model, feature_names)
    
    # 训练策略函数
    policy_model = train_policy_function(X, actions, rewards)
    analyze_feature_importance(policy_model, feature_names)
    
    # 保存模型
    save_models(value_model, policy_model)
    
    print("\n训练完成！")
    print("现在可以使用训练好的模型进行预测和决策。")

if __name__ == "__main__":
    main() 