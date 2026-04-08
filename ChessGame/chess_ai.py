# chess_ai.py - KI für Schach mit Minimax-Algorithmus
import math

# Transposition Table für Caching (speichert Scores für Positionen)
transposition_table = {}

# Bewertung der Figuren (Materialwert)
PIECE_VALUES = {
    "P": 100,  # Bauer
    "N": 320,  # Springer
    "B": 330,  # Läufer
    "R": 500,  # Turm
    "Q": 900,  # Dame
    "K": 20000  # König (hoher Wert, um Schachmatt zu priorisieren)
}

# Positions-Tabellen für bessere Bewertung (für Weiß, für Schwarz gespiegelt)
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

KING_TABLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

PIECE_TABLES = {
    "P": PAWN_TABLE,
    "N": KNIGHT_TABLE,
    "B": BISHOP_TABLE,
    "R": ROOK_TABLE,
    "Q": QUEEN_TABLE,
    "K": KING_TABLE
}

def evaluate_board(board):
    """Verbesserte Bewertungsfunktion: Material + Positionswerte"""
    score = 0
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "":
                value = PIECE_VALUES.get(piece[1], 0)
                # Positionswert hinzufügen
                if piece[1] in PIECE_TABLES:
                    table = PIECE_TABLES[piece[1]]
                    if piece.startswith("w"):
                        pos_value = table[row][col]  # Weiß: normale Reihenfolge
                    else:
                        pos_value = table[7 - row][col]  # Schwarz: gespiegelt
                    value += pos_value
                if piece.startswith("w"):
                    score += value
                else:
                    score -= value
    return score

def is_castling_move(piece, start, end):
    # König zieht 2 Felder horizontal
    if piece[1].upper() == "K" and start[0] == end[0] and abs(start[1] - end[1]) == 2:
        return True
    return False



def minimax(board, depth, alpha, beta, maximizing_player, color, get_legal_moves_fn):
    """
    Minimax-Algorithmus mit Alpha-Beta-Pruning zur Suche des besten Zugs.
    
    - depth: Suchtiefe (wie viele Züge voraus)
    - alpha/beta: Pruning-Werte zur Optimierung
    - maximizing_player: True für maximierenden Spieler (Weiß), False für minimierenden (Schwarz)
    - color: Farbe des aktuellen Spielers
    """
    if depth == 0:
        # Blattknoten: Bewerte die Position
        return evaluate_board(board), None

    # Sammle alle möglichen Züge des aktuellen Spielers
    all_moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith("w" if maximizing_player else "b"):
                moves = get_legal_moves_fn(piece, board, row, col, color)
                for move in moves:
                    all_moves.append(((row, col), move))

    if not all_moves:
        # Keine Züge möglich: Bewerte die Position (z.B. Schachmatt)
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        # Maximierender Spieler (Weiß): Suche höchsten Score
        max_eval = -math.inf
        for move in all_moves:
            # Simuliere den Zug auf einer Kopie des Boards
            new_board = [r[:] for r in board]
            (sr, sc), (er, ec) = move
            new_board[er][ec] = new_board[sr][sc]
            new_board[sr][sc] = ""

            # Rochade: Turm mitziehen
            if is_castling_move(new_board[er][ec], (sr, sc), (er, ec)):
                row = er
                if ec == 6:  # Kurze Rochade
                    new_board[row][5] = new_board[row][7]
                    new_board[row][7] = ""
                elif ec == 2:  # Lange Rochade
                    new_board[row][3] = new_board[row][0]
                    new_board[row][0] = ""

            # Rekursiver Aufruf für den Gegner
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, color, get_legal_moves_fn)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            # Alpha-Beta-Pruning
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta-Cutoff
        return max_eval, best_move
    else:
        # Minimierender Spieler (Schwarz): Suche niedrigsten Score
        min_eval = math.inf
        for move in all_moves:
            new_board = [r[:] for r in board]
            (sr, sc), (er, ec) = move
            new_board[er][ec] = new_board[sr][sc]
            new_board[sr][sc] = ""
            
            # Rochade: Turm mitziehen
            if is_castling_move(new_board[er][ec], (sr, sc), (er, ec)):
                row = er
                if ec == 6:
                    new_board[row][5] = new_board[row][7]
                    new_board[row][7] = ""
                elif ec == 2:
                    new_board[row][3] = new_board[row][0]
                    new_board[row][0] = ""

            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, color, get_legal_moves_fn)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            # Alpha-Beta-Pruning
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-Cutoff
        return min_eval, best_move

def minimax_optimized(board, depth, alpha, beta, maximizing_player, color, get_legal_moves_fn, use_null_move=True):
    """
    Optimierte Minimax-Version mit Transposition Table und Null Move Pruning.
    - Transposition Table: Speichert bereits berechnete Positionen.
    - Null Move Pruning: Überspringt Züge, um schneller zu prunen.
    """
    # Erstelle einen Hash für die Position (einfach: tuple des Boards)
    board_tuple = tuple(tuple(row) for row in board)
    key = (board_tuple, depth, maximizing_player)
    if key in transposition_table:
        return transposition_table[key]

    if depth == 0:
        score = evaluate_board(board)
        transposition_table[key] = (score, None)
        return score, None

    # Null Move Pruning: Wenn nicht im Check, überspringe einen Zug
    if use_null_move and depth > 2 and not maximizing_player:  # Nur für minimierenden Spieler
        # Prüfe, ob König in Check ist (vereinfacht)
        king_in_check = any("K" in row for row in board)  # Einfache Prüfung
        if not king_in_check:
            # Null Move: Wechsle Spieler ohne Zug
            null_score, _ = minimax_optimized(board, depth - 3, -beta, -beta + 1, True, color, get_legal_moves_fn, False)
            null_score = -null_score
            if null_score >= beta:
                transposition_table[key] = (beta, None)
                return beta, None

    all_moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith("w" if maximizing_player else "b"):
                moves = get_legal_moves_fn(piece, board, row, col, color)
                for move in moves:
                    all_moves.append(((row, col), move))

    if not all_moves:
        score = evaluate_board(board)
        transposition_table[key] = (score, None)
        return score, None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in all_moves:
            new_board = [r[:] for r in board]
            (sr, sc), (er, ec) = move
            new_board[er][ec] = new_board[sr][sc]
            new_board[sr][sc] = ""

            if is_castling_move(new_board[er][ec], (sr, sc), (er, ec)):
                row = er
                if ec == 6:
                    new_board[row][5] = new_board[row][7]
                    new_board[row][7] = ""
                elif ec == 2:
                    new_board[row][3] = new_board[row][0]
                    new_board[row][0] = ""

            eval_score, _ = minimax_optimized(new_board, depth - 1, alpha, beta, False, color, get_legal_moves_fn)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        transposition_table[key] = (max_eval, best_move)
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in all_moves:
            new_board = [r[:] for r in board]
            (sr, sc), (er, ec) = move
            new_board[er][ec] = new_board[sr][sc]
            new_board[sr][sc] = ""
            
            if is_castling_move(new_board[er][ec], (sr, sc), (er, ec)):
                row = er
                if ec == 6:
                    new_board[row][5] = new_board[row][7]
                    new_board[row][7] = ""
                elif ec == 2:
                    new_board[row][3] = new_board[row][0]
                    new_board[row][0] = ""

            eval_score, _ = minimax_optimized(new_board, depth - 1, alpha, beta, True, color, get_legal_moves_fn)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        transposition_table[key] = (min_eval, best_move)
        return min_eval, best_move

def get_best_move_optimized(board, color, get_legal_moves_fn, depth=4):
    """
    Optimierte Version: Tiefe 4 mit Caching und Pruning für schnellere Berechnung.
    """
    global transposition_table
    transposition_table = {}  # Reset für jeden Zug
    _, best_move = minimax_optimized(board, depth, -math.inf, math.inf, color == "white", color, get_legal_moves_fn)
    return best_move
