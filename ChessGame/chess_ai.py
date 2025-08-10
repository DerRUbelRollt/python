# chess_ai.py
import math

# Bewertung der Figuren
PIECE_VALUES = {
    "P": 1,  # Bauer
    "N": 3,  # Springer
    "B": 3,  # Läufer
    "R": 5,  # Turm
    "Q": 9,  # Dame
    "K": 0   # König (wird separat behandelt)
}

def evaluate_board(board):
    """Einfache Bewertungsfunktion: + für Weiß, - für Schwarz"""
    score = 0
    for row in board:
        for piece in row:
            if piece != "":
                value = PIECE_VALUES.get(piece[1], 0)
                if piece.startswith("w"):
                    score += value
                else:
                    score -= value
    return score

def minimax(board, depth, alpha, beta, maximizing_player, color, get_legal_moves_fn):
    if depth == 0:
        return evaluate_board(board), None

    all_moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith("w" if maximizing_player else "b"):
                moves = get_legal_moves_fn(piece, board, row, col, color)
                for move in moves:
                    all_moves.append(((row, col), move))

    if not all_moves:
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in all_moves:
            new_board = [r[:] for r in board]  # Kopie
            (sr, sc), (er, ec) = move
            new_board[er][ec] = new_board[sr][sc]
            new_board[sr][sc] = ""
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, color, get_legal_moves_fn)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in all_moves:
            new_board = [r[:] for r in board]
            (sr, sc), (er, ec) = move
            new_board[er][ec] = new_board[sr][sc]
            new_board[sr][sc] = ""
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, color, get_legal_moves_fn)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def get_best_move(board, color, get_legal_moves_fn, depth=2):
    _, best_move = minimax(board, depth, -math.inf, math.inf, color == "white", color, get_legal_moves_fn)
    return best_move
