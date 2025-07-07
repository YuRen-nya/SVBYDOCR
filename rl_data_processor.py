# rl_data_processor.py
# 强化学习数据处理脚本
# 功能：处理游戏数据、计算奖励、分析策略效果和生成可视化图表

import json
import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

def load_game_data(filename):
    """
    加载游戏数据文件
    
    Args:
        filename: JSON数据文件路径
    
    Returns:
        dict: 游戏数据字典
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_state_value(state):
    """
    计算状态价值函数
    综合考虑HP差值、随从价值、手牌价值和特殊状态价值
    
    Args:
        state: 游戏状态字典
    
    Returns:
        float: 状态价值分数
    """
    # 基础价值：HP差值（我方HP - 敌方HP）使用平方的2倍
    hp_diff = state['player_hp'] - state['opponent_hp']
    hp_value = 2 * (hp_diff ** 2) if hp_diff > 0 else -2 * (hp_diff ** 2)
    
    # 随从价值：我方随从总攻击力 - 敌方随从总攻击力
    own_minion_value = sum(atk for atk, _ in state['own_minions'])
    enemy_minion_value = sum(atk for atk, _ in state['opponent_minions'])
    minion_value = own_minion_value - enemy_minion_value
    
    # 手牌价值：手牌数量 * 2（手牌越多选择越多）
    hand_value = len(state['hand_cards']) * 2
    
    # 特殊状态价值：E值和SE值
    special_value = state['e_value'] * 3 + state['se_value'] * 5
    
    # 综合价值（移除法力值）
    total_value = hp_value + minion_value * 5 + hand_value + special_value
    
    return total_value

def calculate_action_reward(action, next_action=None):
    """
    计算行动奖励
    基于状态价值变化计算奖励值
    
    Args:
        action: 当前行动数据
        next_action: 下一个行动数据（可选）
    
    Returns:
        float: 奖励值
    """
    current_state = action['game_state']
    current_value = calculate_state_value(current_state)
    
    if next_action is None:
        # 如果没有下一个行动，使用当前状态作为基准
        reward = current_value
    else:
        # 计算价值变化作为奖励
        next_state = next_action['game_state']
        next_value = calculate_state_value(next_state)
        reward = next_value - current_value
    
    return reward

def add_rewards_to_data(data):
    """
    为数据添加奖励值
    遍历所有行动，计算每个行动的奖励
    
    Args:
        data: 游戏数据字典
    
    Returns:
        dict: 添加了奖励的数据
    """
    actions = data['actions']
    
    for i, action in enumerate(actions):
        if i < len(actions) - 1:
            # 有下一个行动
            next_action = actions[i + 1]
            reward = calculate_action_reward(action, next_action)
        else:
            # 最后一个行动，使用当前状态价值
            reward = calculate_action_reward(action)
        
        action['reward'] = reward
    
    return data

def analyze_game_data(data):
    """
    分析游戏数据
    统计行动频率、状态信息和奖励分布
    
    Args:
        data: 游戏数据字典
    
    Returns:
        dict: 分析结果字典
    """
    actions = data['actions']
    
    # 统计信息
    total_actions = len(actions)
    action_counts = defaultdict(int)
    state_stats = {
        'avg_player_hp': [],
        'avg_opponent_hp': [],
        'avg_e_value': [],
        'avg_se_value': [],
        'avg_reward': []
    }
    
    for action in actions:
        # 统计行动频率
        action_name = action['action_name']
        if isinstance(action_name, list):
            action_name = '+'.join(action_name)
        action_counts[action_name] += 1
        
        # 统计状态信息
        state = action['game_state']
        state_stats['avg_player_hp'].append(state['player_hp'])
        state_stats['avg_opponent_hp'].append(state['opponent_hp'])
        state_stats['avg_e_value'].append(state['e_value'])
        state_stats['avg_se_value'].append(state['se_value'])
        
        # 统计奖励
        if 'reward' in action:
            state_stats['avg_reward'].append(action['reward'])
    
    # 计算平均值
    for key in state_stats:
        if state_stats[key]:  # 确保列表不为空
            state_stats[key] = np.mean(state_stats[key])
        else:
            state_stats[key] = 0.0
    
    return {
        'total_actions': total_actions,
        'action_counts': dict(action_counts),
        'state_stats': state_stats
    }

def create_action_sequence(data):
    """
    创建行动序列数据
    将游戏数据转换为pandas DataFrame格式，便于分析
    
    Args:
        data: 游戏数据字典
    
    Returns:
        pd.DataFrame: 行动序列数据框
    """
    actions = data['actions']
    sequences = []
    
    for i, action in enumerate(actions):
        sequences.append({
            'step': i + 1,
            'action_id': action['action_id'],
            'action_name': action['action_name'],
            'player_hp': action['game_state']['player_hp'],
            'opponent_hp': action['game_state']['opponent_hp'],
            'mana': action['game_state']['mana'],
            'e_value': action['game_state']['e_value'],
            'se_value': action['game_state']['se_value'],
            'hand_cards_count': len(action['game_state']['hand_cards']),
            'own_minions_count': len(action['game_state']['own_minions']),
            'opponent_minions_count': len(action['game_state']['opponent_minions'])
        })
    
    return pd.DataFrame(sequences)

def plot_action_distribution(action_counts):
    """
    绘制行动分布图
    显示各种行动的使用频率
    
    Args:
        action_counts: 行动计数字典
    """
    plt.figure(figsize=(12, 6))
    actions = list(action_counts.keys())
    counts = list(action_counts.values())
    
    plt.bar(range(len(actions)), counts)
    plt.xlabel('Actions')
    plt.ylabel('Usage Count')
    plt.title('Action Usage Frequency Distribution')
    plt.xticks(range(len(actions)), actions, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('action_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_state_evolution(df):
    """
    绘制状态演化图
    显示游戏过程中各种状态的变化趋势
    
    Args:
        df: 行动序列数据框
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # HP变化
    axes[0, 0].plot(df['step'], df['player_hp'], label='Player HP', color='blue')
    axes[0, 0].plot(df['step'], df['opponent_hp'], label='Opponent HP', color='red')
    axes[0, 0].set_xlabel('Step')
    axes[0, 0].set_ylabel('Health Points')
    axes[0, 0].set_title('Health Points Evolution')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # 奖励变化
    if 'reward' in df.columns:
        axes[0, 1].plot(df['step'], df['reward'], color='green')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Reward')
        axes[0, 1].set_title('Reward Evolution')
        axes[0, 1].grid(True)
    else:
        # 如果没有奖励列，显示手牌数量
        axes[0, 1].plot(df['step'], df['hand_cards_count'], color='purple')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Hand Cards')
        axes[0, 1].set_title('Hand Cards Count')
        axes[0, 1].grid(True)
    
    # E/SE值变化
    axes[1, 0].plot(df['step'], df['e_value'], label='E Value', color='orange')
    axes[1, 0].plot(df['step'], df['se_value'], label='SE Value', color='purple')
    axes[1, 0].set_xlabel('Step')
    axes[1, 0].set_ylabel('E/SE Value')
    axes[1, 0].set_title('E/SE Value Evolution')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # 随从数量变化
    axes[1, 1].plot(df['step'], df['own_minions_count'], label='Own Minions', color='blue')
    axes[1, 1].plot(df['step'], df['opponent_minions_count'], label='Enemy Minions', color='red')
    axes[1, 1].set_xlabel('Step')
    axes[1, 1].set_ylabel('Minion Count')
    axes[1, 1].set_title('Minion Count Evolution')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('state_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    主函数
    处理所有游戏数据文件，生成分析报告和可视化图表
    """
    import glob
    
    # 查找所有游戏数据文件（在data文件夹中）
    data_files = glob.glob('data/game_data_*.json')
    
    if not data_files:
        print("未找到游戏数据文件，请先运行main.py收集数据")
        return
    
    print(f"找到 {len(data_files)} 个数据文件")
    
    for filename in data_files:
        print(f"\n分析文件: {filename}")
        
        # 加载数据
        data = load_game_data(filename)
        
        # 添加奖励计算
        data = add_rewards_to_data(data)
        
        # 分析数据
        analysis = analyze_game_data(data)
        
        print(f"总行动数: {analysis['total_actions']}")
        print(f"平均玩家HP: {analysis['state_stats']['avg_player_hp']:.2f}")
        print(f"平均对手HP: {analysis['state_stats']['avg_opponent_hp']:.2f}")
        print(f"平均奖励值: {analysis['state_stats']['avg_reward']:.2f}")
        
        print("\n行动使用频率:")
        for action, count in sorted(analysis['action_counts'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {action}: {count}次")
        
        # 创建行动序列
        df = create_action_sequence(data)
        
        # 保存到CSV（也在data文件夹中）
        csv_filename = filename.replace('.json', '_sequence.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"行动序列已保存到: {csv_filename}")
        
        # 保存带奖励的数据（也在data文件夹中）
        reward_filename = filename.replace('.json', '_with_rewards.json')
        with open(reward_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"带奖励的数据已保存到: {reward_filename}")
        
        # 绘制图表
        plot_action_distribution(analysis['action_counts'])
        plot_state_evolution(df)

if __name__ == "__main__":
    main() 