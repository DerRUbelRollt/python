# move_logic.py
rank = ["P", "R", "N", "B", "Q", "K"]
# move_logic.py

def get_pawn_moves(board, row, col, is_white, is_black):
    moves = []
    # Beispiel für weiße Bauern
    if is_white:
        # Prüfen, ob das Feld vor dem Bauern leer ist
        if board[row - 1][col] == "":
            moves.append((row - 1, col))
        # Anfangszug 2 Felder
        if row == 6 and board[row - 2][col] == "":
            moves.append((row - 2, col))
            # Prüfen, ob das Feld schräg links oder rechts vom Bauern eine gegnerische Figur hat
        for r in rank: 
            if col != 7: 
                if board[row -1][col - 1] == f"b{r}" or board[row -1][col + 1] == f"b{r}" :
                    if board[row - 1][col- 1] != "": 
                        moves.append((row - 1, col - 1))
                        # Schlagen nach schräg rechts
                    if board[row - 1][col + 1] != "": 
                        moves.append((row - 1, col + 1))
            else:# Schlagen nach links
                moves.append((row - 1, col - 1))  
        # Beispiel für schwarze Bauern
    if is_black:
        if board[row + 1][col] == "":
            moves.append((row + 1, col))
        # Anfangszug 2 Felder
        if row == 1 and board[row + 2][col] == "":
            moves.append((row + 2, col))
        for r in rank:
            if col != 7:    
                if board[row + 1][col + 1] == f"w{r}" or board[row + 1][col - 1] == f"w{r}":
                    if board[row + 1][col + 1] != "": 
                        moves.append((row + 1, col + 1))
                        # Schlagen nach schräg rechts
                    if board[row + 1][col - 1] != "": 
                        moves.append((row + 1, col - 1))
            else:# Schlagen nach links
                moves.append((row + 1, col - 1))  
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
    is_black = piece[0] == "b"
    kind = piece[1]

    if kind == "P":
        return get_pawn_moves(board, row, col, is_white, is_black)
    elif kind == "R":
        return get_rook_moves(board, row, col, is_white , is_black)
    elif kind == "N":
        return get_knight_moves(board, row, col, is_white , is_black)
    elif kind == "B":
        return get_bishop_moves(board, row, col, is_white , is_black)
    elif kind == "Q":
        return get_queen_moves(board, row, col, is_white , is_black)
    elif kind == "K":
        return get_king_moves(board, row, col, is_white , is_black)
    else:
        return []
