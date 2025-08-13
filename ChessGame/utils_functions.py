import random

def get_all_attacked_squares(board, by_color):
    from move_logic import get_valid_moves
    attacked = set()

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "" and piece.startswith(by_color[0]):
                moves = get_valid_moves(piece, board, row, col)
                attacked.update(moves)

    return attacked


def is_king_in_check(board, color):
    if  color == "white":
        enemy_color = "b"
        king_piece = "wK"
    elif color == "black":
        enemy_color = "w"
        king_piece = "bK"
        
    king_pos = None

    # Finde den König
    for row in range(8):
        for col in range(8):
            if board[row][col] == king_piece:
                king_pos = (row, col)
                break
        if king_pos:
            break

    if not king_pos:
        return True  # kein König gefunden = Schach/Fehler

    attacked_squares = get_all_attacked_squares(board, enemy_color)
    return king_pos in attacked_squares

def insufficient_material(board):
    pieces = []
    for row in board:
        for piece in row:
            if piece != "":
                pieces.append(piece)

    # Zähle nur die Figurentypen ohne Farbe
    piece_types = [p[1] for p in pieces]  # z.B. "K", "Q", "B", ...

    # Fall 1: Nur beide Könige
    if sorted(piece_types) == ["K", "K"]:
        return True

    # Fall 2: König + Läufer gegen König
    if sorted(piece_types) in [["B", "K", "K"], ["K", "K", "B"]]:
        return True

    # Fall 3: König + Springer gegen König
    if sorted(piece_types) in [["K", "K", "N"], ["N", "K", "K"]]:
        return True

    # Fall 4: König + Läufer gegen König + Läufer (optional ohne Farberkennung)
    if sorted(piece_types) == ["B", "B", "K", "K"]:
        return True

    return False

