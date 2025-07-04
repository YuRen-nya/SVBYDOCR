# game_logic.py

import pyautogui
from time import sleep
from game_state import GameState
from template_matching import load_templates, match_template
from ocr_utils import ocr_number, ocr_card_name, capture_card_detail, preprocess_card_image, process_card
from yolo_detection import update_state_with_yolo
from ultralytics import YOLO
import cv2
import pytesseract
from card_evaluator import CardScorer
import config  # 导入 config 模块

# 设置 tesseract 的路径（Windows 用户需要这一步）
pytesseract.pytesseract.tesseract_cmd = r'G:\tesseract-OCR\tesseract.exe'

# 全局加载模板
PLAYER_HP_TEMPLATES, PLAYER_HP_LABELS = load_templates('player_hp_img_gray')
OPPONENT_HP_TEMPLATES, OPPONENT_HP_LABELS = load_templates('opponent_hp_img_gray')

# 创建评分器实例
scorer = CardScorer(config.BASE_CARD_SCORES, config.CARD_CONDITION_RULES)

# 获取推荐手牌的坐标
def get_best_card_position(state, hand_card_scores, card_positions):
    best_card = max(hand_card_scores, key=hand_card_scores.get)
    best_score = hand_card_scores[best_card]
    # print(f"Best card: {best_card}, Score: {best_score}")
    
    # 找到最佳手牌的位置索引
    try:
        best_card_index = state.hand_cards.index(best_card)
    except ValueError:
        # print(f"Card {best_card} not found in hand cards.")
        return None
    
    # 返回最佳手牌的坐标
    if best_card_index < len(card_positions):
        return card_positions[best_card_index]
    else:
        # print("No valid position found for the best card.")
        return None

# 模拟鼠标操作
def right_click(position):
    pyautogui.moveTo(position[0], position[1])
    pyautogui.click(button='right')
    sleep(0.5)  # 等待一段时间以确保操作完成

def left_click(position):
    pyautogui.moveTo(position[0], position[1])
    pyautogui.click(button='left')
    sleep(0.5)  # 等待一段时间以确保操作完成

# 识别特殊卡牌并执行特殊动作
def perform_special_action(card_name, action_dict):
    if card_name in action_dict:
        action_info = action_dict[card_name]
        action_type = action_info["action"]
        
        if action_type == "select_target":
            target_position = action_info["target"]
            left_click(target_position)
        elif action_type == "wait_for_effect":
            duration = action_info["duration"]
            sleep(duration) # 暂时无用
        elif action_type == "left_click":
            position = action_info["position"]
            pyautogui.mouseDown(position)
            sleep(0.5)
            pyautogui.mouseUp()
        # 其他动作类型...



