
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
            print(f"Pawn move added: from ({row}, {col}) to ({row - 1}, {col})")
        # Anfangszug 2 Felder
        if row == 6 and board[row - 2][col] == "":
            moves.append((row - 2, col))
            print(f"Pawn move added: from ({row}, {col}) to ({row - 2}, {col})")
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

def get_rook_moves(board, row, col, is_white, is_black):
    moves = []
    # Die Range in der sich der sich alle Türem bewegen dürfen
    for step in range(1, 8):
        new_row_up = row - step
        new_col_left = col - step
        new_row_down = row + step
        new_col_right = col + step
        if new_row_up < 0 :
            new_row_up = 0         # außerhalb des Bretts
        if new_col_left < 0 :
            new_col_left = 0       # außerhalb des Bretts
        if new_row_down > 7 :
            new_row_down = 7       # außerhalb des Bretts
        if new_col_right > 7 :
            new_col_right = 7      # außerhalb des Bretts
        # Von unten zu oben wenn keine Figuren im weg sind
        if row > new_row_up and board[new_row_up][col] == "":
            moves.append((new_row_up, col))
        # Von rechts nach links wenn keine Figuren im weg sind
        if col > new_col_left and board[row][new_col_left] == "" :
            moves.append((row, new_col_left))
        # Von oben zu unten wenn keine Figuren im weg sind
        if row < new_row_down and board[new_row_down][col] == "" :
            moves.append((new_row_down, col))
        # Von links nach rechts wenn keine Figuren im weg sind
        if col < new_col_right and board[row][new_col_right] == "" :
            moves.append((row, new_col_right))

         
    return moves    

def get_knight_moves(board, row, col, is_white, is_black):
    moves = []
    return moves

def get_bishop_moves(board, row, col, is_white, is_black):
    moves = []
    return moves

def get_queen_moves(board, row, col, is_white, is_black):
    moves = []
    return moves

def get_king_moves(board, row, col, is_white, is_black):
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
