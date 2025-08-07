
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

def get_rook_moves(board, row, col, is_white, is_black):
    moves = []
    # Richtungen Oben / unten/ links/ rechts
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    # Die Range in der sich der sich alle Türem bewegen dürfen
    for dr, dc in directions:
        for step in range(1, 8):
            new_row = row + dr * step
            new_col = col + dc * step
            if new_row < 0 or new_row > 7 or new_col < 0 or new_col > 7:
                break
            target = board[new_row][new_col]
            if target == "":
                moves.append((new_row, new_col))
            else:
                if is_white and target.startswith("b") or is_black and target.startswith("w"):
                    moves.append((new_row, new_col))
                    break # danach NICHT weitergehen
                break
             
         
    return moves    

def get_knight_moves(board, row, col, is_white, is_black):
    moves = []
    directions_L_R = [(0,-1), (0,1)]
    directions_O_D = [(-1,0), (1,0)]
    for dr, dc in directions_L_R:
        col_up_down = col + dc * 1
        row_left_right = row + dr * 1
        row_up = row - 2
        row_down = row + 2
        col_left = col - 2
        col_right = col + 2
        if col_up_down > 7:
            col_up_down = 7
        if row_left_right > 7:
            row_left_right = 7
        if row_up < 0:
            row_up = row 
        if row_down > 7:
            row_down = row
        if col_left < 0 :
            col_left = col
        if col_right > 7:
            col_right = col
        if (is_white and not board[row_up][col_up_down].startswith("w")) or (is_black and not board[row_up][col_up_down].startswith("b")):
            moves.append((row_up, col_up_down))

        if (is_white and not board[row_down][col_up_down].startswith("w")) or (is_black and not board[row_down][col_up_down].startswith("b")):
            moves.append((row_down, col_up_down))
            
        if (is_white and not board[row_left_right][col_left].startswith("w")) or (is_black and not board[row_left_right][col_left].startswith("b")):
            moves.append((row_left_right, col_left))

        if (is_white and not board[row_left_right][col_right].startswith("w")) or (is_black and not board[row_left_right][col_right].startswith("b")):
            moves.append((row_left_right, col_right))
        
    return moves

def get_bishop_moves(board, row, col, is_white, is_black):
    moves = []
        # Richtungen Diagonal oben links/ oben rechts/ unten rechts/ unten links
    directions = [(-1,-1), (-1,1), (1,1), (1,-1)]
    for dr, dc in directions:
        for step in range(1,8):
            new_row = row + dr * step
            new_col = col + dc * step
            if new_row < 0 or new_row > 7 or new_col < 0 or new_col > 7:
                break
            target = board[new_row][new_col]
            if target == "":
                moves.append((new_row, new_col))
            else:
                if is_white and target.startswith("b") or is_black and target.startswith("w"):
                    moves.append((new_row, new_col))
                    break # danach NICHT weitergehen
                break
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
