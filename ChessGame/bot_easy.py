# bot.py

import random
from move_logic import get_valid_moves

def get_bot_move(board, color):
    # Finde alle möglichen Züge für den Bot
    all_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith("b" if color == "black" else "w"):
                valid_moves = get_valid_moves(piece, board, row, col)
                for move in valid_moves:
                    all_moves.append(((row, col), move))

    if all_moves:
        return random.choice(all_moves)  # Zufälliger Zug

    return None  # Kein möglicher Zug
