# bots.py - Bot-Funktionen
from chess_ai import get_best_move_optimized
from move_logic import get_legal_moves

def get_bot_b_move(board, color):
    """
    Beginner Bot: Verwendet Minimax mit Tiefe 4 für noch bessere Spielstärke.
    Sucht den besten Zug basierend auf Material- und Positionsbewertung.
    Hinweis: Tiefe 4 kann das Spiel verlangsamen – bei Bedarf zurück auf 3 setzen.
    """
    return get_best_move_optimized(board, color, get_legal_moves, depth=3)

def get_bot_a_move(board, color):
    """
    Advanced Bot: Optimierte KI mit Tiefe 4, Transposition Table und Null Move Pruning.
    Schneller als normaler Tiefe-4-Bot, aber stärker als Beginner.
    """
    return get_best_move_optimized(board, color, get_legal_moves, depth=5)


