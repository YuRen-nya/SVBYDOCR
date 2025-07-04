# EVO_check.py

from game_logic import right_click  # 导入 right_click 函数

def evolve_and_dash_check(state):
    ids = state.minion_names
    minions = state.my_followers
    
    # 按顺序优先检测名称为特定值的随从
    target_names = ["Cerberus, Hellfire Unleashed", "Aragavy, Eternal Hunter", "Ceres, Blue Rose Maiden", "Orthrus, Hellhound Blader", "Devious Lesser Mummy"]
    
    for target_name in target_names:
        if target_name in ids:
            idx = ids.index(target_name)
            position = state.minion_positions[idx]
            right_click([0.5*(position[0]+position[2]),0.5*(position[1]+position[3])])
            break
    else:
        # 如果没有找到目标名称的随从，则检测状态为"DASH"的随从
        dash_found = False
        for idx, status in enumerate(minions):
            if status == 'dash':
                position = state.minion_positions[idx]
                right_click([0.5*(position[0]+position[2]),0.5*(position[1]+position[3])])
                break
        
        # 如果没有找到状态为"DASH"的随从，则右键第一个随从
        if not dash_found and minions:
            position = state.minion_positions[0]
            right_click([0.5 * (position[0] + position[2]), 0.5 * (position[1] + position[3])])
