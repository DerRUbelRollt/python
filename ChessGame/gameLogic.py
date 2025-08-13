# Merkt sich, ob eine Figur ausgewählt wurde
selected_square = None
from move_logic import get_legal_moves

rochade_valid_w = 0
rochade_valid_b = 0

def handle_click(pos, board, current_player):
    global selected_square, rochade_valid_w, rochade_valid_b
    tile_size = 100
    col = pos[0] // tile_size 
    row = pos[1] // tile_size
    if selected_square is None:
        piece = board[row][col]
        if piece != "":
            if current_player == "white" and not piece.startswith("w"):
                return False
            if current_player == "black" and not piece.startswith("b"):
                return False
            selected_square = (row, col)
        return False

    else:
        from_row, from_col = selected_square
        to_row, to_col = row, col
        piece = board[from_row][from_col]

        valid_moves = get_legal_moves(piece, board, from_row, from_col, current_player[0])

        if (to_row, to_col) in valid_moves:
            # Rochade-Erkennung nur für König
            if piece[1].upper() == "K":
                # Weiß
                
                if piece.startswith("w") and from_row == 7 and from_col == 4 and rochade_valid_w == 0:
                    # Kurze Rochade
                    rochade_valid_w = 1
                    if to_row == 7 and to_col == 6:
                        # König bewegt sich von e1 nach g1
                        board[7][7], board[7][5] = "", "wR"  # Turm von h1 nach f1
                    # Lange Rochade
                    elif to_row == 7 and to_col == 2:
                        # König bewegt sich von e1 nach c1
                        board[7][0], board[7][3] = "", "wR"  # Turm von a1 nach d1
                # Schwarz
                if piece.startswith("b") and from_row == 0 and from_col == 4 and rochade_valid_b == 0:
                    # Kurze Rochade
                    rochade_valid_b = 1
                    if to_row == 0 and to_col == 6:
                        # König bewegt sich von e8 nach g8
                        board[0][7], board[0][5] = "", "bR"  # Turm von h8 nach f8
                    # Lange Rochade
                    elif to_row == 0 and to_col == 2:
                        # König bewegt sich von e8 nach c8
                        board[0][0], board[0][3] = "", "bR"  # Turm von a8 nach d8
                

            # König ziehen (auch normale Züge)
            board[to_row][to_col] = piece
            board[from_row][from_col] = ""
            selected_square = None
            return True
        else:
            selected_square = None
            return False


def get_selected_square():
    global selected_square
    return selected_square

def get_rochade_valid(color):
    global rochade_valid_w, rochade_valid_b
    return rochade_valid_w if color == "w" else rochade_valid_b
