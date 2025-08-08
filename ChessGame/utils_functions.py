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
    if color == "w":
        enemy_color = "b"
        king_piece = "wK"
    else:
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

