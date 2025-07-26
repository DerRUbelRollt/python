# move_logic.py

# move_logic.py

def get_pawn_moves(board, row, col, is_white):
    """
    Gibt alle gültigen Zielkoordinaten für einen Bauern zurück.
    :param board: Das aktuelle Spielbrett
    :param row: Zeile der Figur
    :param col: Spalte der Figur
    :param is_white: True für weißen Bauern, False für schwarzen
    :return: Liste mit (ziel_row, ziel_col)
    """
    moves = []

    # Beispiel für weiße Bauern → du ergänzt später für schwarz
    if is_white:
        if board[row - 1][col] == "":
            moves.append((row - 1, col))
        # Anfangszug 2 Felder
        if row == 6 and board[row - 2][col] == "":
            moves.append((row - 2, col))
        # Schlagen nach schräg links/rechts – ergänze das!
    
    return moves


def get_rook_moves(board, row, col, is_white):
    moves = []
    return moves

def get_knight_moves(board, row, col, is_white):
    moves = []
    return moves

def get_bishop_moves(board, row, col, is_white):
    moves = []
    return moves

def get_queen_moves(board, row, col, is_white):
    moves = []
    return moves

def get_king_moves(board, row, col, is_white):
    moves = []
    return moves

def get_valid_moves(piece, board, row, col):
    is_white = piece[0] == "w"
    kind = piece[1]

    if kind == "P":
        return get_pawn_moves(board, row, col, is_white)
    elif kind == "R":
        return get_rook_moves(board, row, col, is_white)
    elif kind == "N":
        return get_knight_moves(board, row, col, is_white)
    elif kind == "B":
        return get_bishop_moves(board, row, col, is_white)
    elif kind == "Q":
        return get_queen_moves(board, row, col, is_white)
    elif kind == "K":
        return get_king_moves(board, row, col, is_white)
    else:
        return []
