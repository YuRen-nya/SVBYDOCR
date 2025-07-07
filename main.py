# main.py
# 游戏自动化主程序 - SZBAI控制器
# 功能：游戏状态识别、策略选择、自动操作、数据记录、GUI界面
# 作者：SZBAI开发团队
# 版本：2.0
# 更新日期：2024年

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import pyautogui
import json
import os

# 导入自定义模块
from GameState import GameState, Get_GameState  # 游戏状态识别模块
from Config import CL, ACTION, find_best_strategy  # 策略配置和选择模块
from ATT import perform_full_attack  # 攻击执行模块
from Window_Coordinates_Initial import get_window_rect  # 窗口坐标获取模块
from Templates import load_templates, template_match  # 模板匹配模块

# ===== 全局变量定义 =====
# 数据记录列表 - 存储游戏过程中的所有行动数据，用于强化学习训练
game_actions = []
# 数据记录开关 - 控制是否记录游戏数据，可在GUI中切换
recording_enabled = True

# ===== 强化学习数据记录类 =====
class GameAction:
    """
    游戏行动数据类
    用于记录每次游戏行动的状态、动作和奖励信息
    这些数据将用于训练强化学习模型
    """
    def __init__(self, state, action_id, reward=None):
        """
        初始化游戏行动数据
        
        Args:
            state: 游戏状态对象，包含当前游戏的所有状态信息
            action_id: 执行的策略ID，对应Config.py中定义的策略
            reward: 奖励值（可选），用于强化学习训练
        """
        self.timestamp = time.time()  # 记录时间戳，用于数据分析和调试
        # 记录游戏状态信息 - 这些是强化学习的状态特征
        self.game_state = {
            'player_hp': state.player_hp,  # 玩家生命值
            'opponent_hp': state.opponent_hp,  # 对手生命值
            'mana': state.mana,  # 法力值
            'e_value': state.e_value,  # 能量值
            'se_value': state.se_value,  # 特殊能量值
            'own_minions': list(zip(state.own_minion_attack, state.own_minion_health)),  # 我方随从（攻击力，生命值）
            'opponent_minions': list(zip(state.opponent_minion_attack, state.opponent_minion_health)),  # 敌方随从（攻击力，生命值）
            'hand_cards': state.hand_card_ids.copy()  # 手牌ID列表
        }
        self.action_id = action_id  # 策略ID
        self.reward = reward  # 奖励值
        # 获取策略名称，用于日志输出和数据分析
        self.action_name = CL[action_id][0] if action_id in CL else f"action_{action_id}"
    
    def to_dict(self):
        """
        将对象转换为字典格式，用于JSON序列化
        这个方法使得数据可以保存到文件中
        
        Returns:
            dict: 包含所有数据的字典，可以直接序列化为JSON
        """
        return {
            'timestamp': self.timestamp,
            'game_state': self.game_state,
            'action_id': self.action_id,
            'action_name': self.action_name,
            'reward': self.reward
        }

def log(message):
    """
    日志输出函数
    向GUI文本框或控制台输出日志信息
    支持实时显示和自动滚动
    
    Args:
        message: 要输出的日志消息
    """
    if 'text_box' in globals():
        # 如果GUI已创建，输出到文本框
        text_box.insert(tk.END, message + "\n")
        text_box.see(tk.END)  # 自动滚动到最新内容
    else:
        # 否则输出到控制台
        print(message)

def save_game_data():
    """
    保存游戏数据到JSON文件
    将记录的游戏行动数据保存到data文件夹中
    文件名包含时间戳，便于区分不同的游戏会话
    """
    if not game_actions:
        log("[数据记录] 没有数据需要保存")
        return
    
    # 确保data文件夹存在
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 生成带时间戳的文件名，格式：game_data_YYYYMMDD_HHMMSS.json
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(data_dir, f"game_data_{timestamp}.json")
    
    # 构建数据字典，包含会话信息和行动列表
    data = {
        'session_info': {
            'total_actions': len(game_actions),  # 总行动数
            'start_time': game_actions[0].timestamp if game_actions else time.time(),  # 开始时间
            'end_time': time.time()  # 结束时间
        },
        'actions': [action.to_dict() for action in game_actions]  # 行动列表
    }
    
    # 保存到文件，使用UTF-8编码支持中文
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    log(f"[数据记录] 已保存 {len(game_actions)} 个行动到 {filename}")
    game_actions.clear()  # 清空记录列表，释放内存

# ===== 窗口坐标和模板初始化 =====
# 获取游戏窗口坐标，用于精确定位游戏元素
coords = get_window_rect()
if coords is None:
    log("[错误] 无法获取窗口坐标，使用默认值")
    [x_o, y_o, x_ob, y_ob] = [0, 0, 1920, 1080]  # 默认全屏坐标
else:
    [x_o, y_o, x_ob, y_ob] = coords

# 加载各种模板图像，用于界面元素识别
end1, end1l = load_templates('Templates/end_img1', threshold=150)  # 结束按钮模板
begin1, begin1l = load_templates('Templates/begin_img1', threshold=150)  # 开始游戏按钮模板
change1, change1l = load_templates('Templates/change_img1', threshold=150)  # 换牌按钮模板
manat, manal = load_templates('Templates/mana_img1', threshold=150)  # 法力值模板

# ===== 全局状态变量 =====
auto_run_enabled = False  # 自动运行开关，控制是否启用自动检测
paused = False  # 暂停状态，控制是否暂停自动运行
game_in_progress = False  # 游戏进行中状态，用于区分不同阶段
change_detected = False  # 换牌界面检测状态，避免重复点击

# ===== 线程锁 =====
# 使用线程锁保护共享变量，避免多线程访问冲突
auto_run_lock = threading.Lock()  # 自动运行状态锁
pause_lock = threading.Lock()  # 暂停状态锁
game_state_lock = threading.Lock()  # 游戏状态锁

# GUI按钮变量
btn_pause = None

def run_one_turn():
    """
    运行一次完整回合流程
    包括：获取状态、策略选择、出牌、攻击阶段
    
    流程：
    1. 获取最新游戏状态
    2. 循环选择并执行策略，直到无可用策略
    3. 执行攻击阶段
    4. 结束回合
    
    这是游戏自动化的核心函数，负责执行完整的游戏逻辑
    """
    global game_in_progress  # 全局变量声明必须在函数开始处
    
    # 检查暂停状态，如果暂停则跳过执行
    with pause_lock:
        if paused:
            log("[INFO] 当前处于暂停状态，跳过执行")
            return

    # 创建游戏状态对象，设置窗口坐标
    state = GameState()
    state.co = [x_o, y_o, x_ob, y_ob]

    # Step 1: 获取最新游戏状态
    Get_GameState(state)

    # Step 2: 循环选择并执行策略，直到无可用策略
    strategy_count = 0
    while True:
        # 检查暂停状态
        with pause_lock:
            if paused:
                log("[INFO] 执行中断：当前处于暂停状态")
                return

        # 寻找最佳策略，使用Config.py中定义的策略选择逻辑
        best_strategy_id = find_best_strategy(state, CL)
        if best_strategy_id is None:
            break  # 没有可用策略，退出循环

        log(f"选定策略ID: {best_strategy_id}")
        
        # 记录行动数据（如果启用），用于强化学习训练
        if recording_enabled:
            game_actions.append(GameAction(state, best_strategy_id))
        
        try:
            # 执行策略，调用Config.py中定义的ACTION函数
            ACTION[best_strategy_id](state)
            strategy_count += 1

            # 更新游戏状态（重新读取），确保状态同步
            Get_GameState(state)

        except Exception as e:
            log(f"[错误] 执行策略 {best_strategy_id} 时发生异常: {e}")
            break

    # 输出策略执行结果
    if strategy_count == 0:
        log("无可用策略，跳过出牌阶段")
    else:
        log(f"共执行了 {strategy_count} 个策略")

    # Step 3: 攻击阶段
    with pause_lock:
        if paused:
            log("[INFO] 当前处于暂停状态，跳过攻击阶段")
            return

    if state.own_minion_count > 0:
        log("开始攻击阶段")
        perform_full_attack(state)  # 执行完整攻击流程
        state.print_state()  # 打印当前状态
    else:
        log("我方无随从，跳过攻击阶段")

    # Step 4: 回合结束 - 点击结束按钮
    # 使用mouseDown/mouseUp模拟真实点击，提高稳定性
    pyautogui.mouseDown(1450 + x_o, 450 + y_o)
    time.sleep(0.5)
    pyautogui.mouseUp()


def start_turn():
    """
    按钮回调函数：启动一个新线程运行回合流程
    避免GUI界面卡顿，保持界面响应性
    """
    threading.Thread(target=run_one_turn, daemon=True).start()


def toggle_auto_run():
    """
    切换自动运行开关状态
    控制是否启用自动检测和运行
    这个功能可以自动检测游戏状态并执行相应操作
    """
    global auto_run_enabled
    with auto_run_lock:
        auto_run_enabled = not auto_run_enabled
    status = "开启" if auto_run_enabled else "关闭"
    log(f"[AUTO] 自动运行已{status}")
    update_auto_run_button_text()


def update_auto_run_button_text():
    """
    更新自动运行按钮文字
    根据当前状态显示相应的按钮文本
    提供直观的状态反馈
    """
    btn_text_auto.set("关闭自动运行" if auto_run_enabled else "开启自动运行")


def toggle_pause():
    """
    切换暂停状态
    控制是否暂停自动运行
    可以在任何时候暂停和恢复自动运行
    """
    global paused
    with pause_lock:
        paused = not paused
    status = "暂停" if paused else "继续"
    log(f"[CONTROL] 状态已切换为：{status}")
    update_pause_button_text()


def update_pause_button_text():
    """
    更新暂停按钮文字
    根据当前状态显示相应的按钮文本
    使用emoji图标提供更好的视觉效果
    """
    btn_text_pause.set("▶️ 继续" if paused else "⏸️ 暂停")


def toggle_recording():
    """
    切换数据记录开关
    控制是否记录游戏数据用于强化学习
    可以在游戏过程中动态开启或关闭数据记录
    """
    global recording_enabled
    recording_enabled = not recording_enabled
    status = "开启" if recording_enabled else "关闭"
    log(f"[数据记录] 记录功能已{status}")

def reset_game_state():
    """
    手动重置游戏状态
    用于处理游戏状态异常的情况
    当自动检测出现问题时，可以手动重置状态
    """
    global game_in_progress, change_detected  # 全局变量声明必须在函数开始处
    
    with game_state_lock:
        game_in_progress = False
        change_detected = False
    log("[CONTROL] 游戏状态已手动重置")


def auto_run_loop():
    """
    自动检测循环
    持续检测游戏状态并自动执行相应操作
    这是自动运行的核心循环，在后台线程中运行
    
    检测流程：
    1. 检测开始游戏按钮 - 当游戏未开始时
    2. 检测换牌界面 - 游戏开始后的第一个阶段
    3. 检测结束按钮并执行回合 - 主要游戏阶段
    4. 持续检测开始游戏按钮 - 判断游戏是否结束
    """
    global game_in_progress, change_detected  # 全局变量声明必须在函数开始处
    
    last_run_time = 0
    cooldown = 10  # 回合执行冷却时间，防止重复触发（单位：秒）
    last_start_time = 0
    start_cooldown = 5  # 开始游戏按钮的冷却时间
    last_change_time = 0
    change_cooldown = 3  # 换牌按钮的冷却时间

    while True:
        current_time = time.time()

        # 获取自动运行状态
        with auto_run_lock:
            enabled = auto_run_enabled

        if enabled and not is_paused():
            # 获取游戏状态
            with game_state_lock:
                in_game = game_in_progress
                change_done = change_detected

            if not in_game:
                # 游戏未进行时，检测开始游戏按钮
                start_region = (980 + x_o, 400 + y_o, 100, 30)
                start_matched = template_match(start_region, begin1, begin1l, threshold_match=0.8)

                if start_matched and (current_time - last_start_time) > start_cooldown:
                    log("[AUTO] 检测到开始游戏按钮，点击开始游戏...")
                    pyautogui.click(1400 + x_o, 600 + y_o)
                    last_start_time = current_time  # 更新最后点击时间
                    
                    # 等待游戏开始
                    time.sleep(3)
                    
                    # 设置游戏进行中状态，重置换牌检测状态
                    with game_state_lock:
                        game_in_progress = True
                        change_detected = False
                    log("[GAME] 游戏已开始，等待换牌界面...")
            else:
                # 游戏进行中时，先检测换牌界面
                if not change_done:
                    change_region = (450 + x_o, 450 + y_o, 500, 50)
                    change_matched = template_match(change_region, change1, change1l, threshold_match=0.8)

                    if change_matched and (current_time - last_change_time) > change_cooldown:
                        log("[AUTO] 检测到换牌界面，点击换牌按钮...")
                        pyautogui.click(1400 + x_o, 500 + y_o)
                        last_change_time = current_time  # 更新最后点击时间
                        
                        # 等待换牌完成
                        time.sleep(2)
                        
                        # 设置换牌完成状态
                        with game_state_lock:
                            change_detected = True
                        log("[GAME] 换牌完成，进入主要游戏流程")
                else:
                    # 换牌完成后，检测结束按钮
                    end_region = (1400 + x_o, 425 + y_o, 100, 50)
                    end_matched = template_match(end_region, end1, end1l, threshold_match=0.7)

                    if end_matched and (current_time - last_run_time) > cooldown:
                        log("[AUTO] 检测到结束按钮，开始执行回合流程...")
                        run_one_turn()
                        last_run_time = current_time  # 更新最后执行时间
                    
                    # 持续检测游戏是否结束（通过检测开始游戏按钮）
                    start_region = (980 + x_o, 400 + y_o, 100, 30)
                    start_matched = template_match(start_region, begin1, begin1l, threshold_match=0.8)
                    
                    if start_matched:
                        log("[GAME] 检测到游戏结束：出现开始游戏按钮")
                        # 重置游戏状态
                        with game_state_lock:
                            game_in_progress = False
                            change_detected = False
                        log("[GAME] 游戏状态已重置，等待下一局游戏...")

        time.sleep(1)  # 每秒检查一次，平衡响应性和性能


def is_paused():
    """
    获取当前是否暂停（带锁保护）
    线程安全的暂停状态检查
    
    Returns:
        bool: True表示暂停，False表示运行中
    """
    with pause_lock:
        return paused




# ===== GUI界面创建 =====
# 创建主窗口，设置标题和大小
root = tk.Tk()
root.title("SZBAI控制器 v2.0")
root.geometry("600x400")

# 添加手动执行按钮 - 可以手动触发一次完整回合
btn_manual = tk.Button(root, text="手动执行一次完整回合", width=25, height=2, command=start_turn)
btn_manual.pack(pady=5)

# 添加自动运行按钮 - 控制自动检测和运行
btn_text_auto = tk.StringVar()
btn_text_auto.set("开启自动运行")
tk.Button(root, textvariable=btn_text_auto, width=25, height=2, command=toggle_auto_run).pack(pady=5)

# 添加暂停按钮 - 可以随时暂停和恢复自动运行
btn_text_pause = tk.StringVar()
btn_text_pause.set("⏸️ 暂停")
tk.Button(root, textvariable=btn_text_pause, width=25, height=2, command=toggle_pause).pack(pady=5)

# 添加数据记录按钮 - 控制强化学习数据收集
tk.Button(root, text="切换数据记录", width=25, height=2, command=toggle_recording).pack(pady=5)
tk.Button(root, text="保存游戏数据", width=25, height=2, command=save_game_data).pack(pady=5)

# 添加游戏状态控制按钮 - 手动重置游戏状态
tk.Button(root, text="重置游戏状态", width=25, height=2, command=reset_game_state).pack(pady=5)

# 日志显示框 - 实时显示程序运行状态和日志信息
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
text_box.pack(padx=10, pady=5, expand=True, fill='both')

# 启动自动检测线程 - 在后台持续运行，不影响GUI响应
threading.Thread(target=auto_run_loop, daemon=True).start()

# 启动GUI主循环 - 程序入口点
root.mainloop()