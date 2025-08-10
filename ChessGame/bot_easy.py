# bot.py
from chess_ai import get_best_move
from move_logic import get_legal_moves

def get_bot_move(board, color):
    return get_best_move(board, color, get_legal_moves, depth=2)
