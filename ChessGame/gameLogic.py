# Merkt sich, ob eine Figur ausgewählt wurde
selected_square = None
from move_logic import get_valid_moves

def handle_click(pos, board, current_player):
    global selected_square
    tile_size = 100
    col = pos[0] // tile_size 
    row = pos[1] // tile_size

    if selected_square is None:
        piece = board[row][col]
        if piece != "":
            # Farbprüfung: passt Figur zur Spielerfarbe?
            if current_player == "white" and not piece.startswith("w"):
                return False
            if current_player == "black" and not piece.startswith("b"):
                return False
            selected_square = (row, col)
        return False  # nur Auswahl, kein Zug
    else:
        from_row, from_col = selected_square
        to_row, to_col = row, col
        piece = board[from_row][from_col]

        valid_moves = get_valid_moves(piece, board, from_row, from_col)

        if (to_row, to_col) in valid_moves:
            board[to_row][to_col] = piece
            board[from_row][from_col] = ""
            selected_square = None
            return True  # erfolgreicher Zug
        else:
            # Auswahl zurücksetzen, falls ungültiger Zug
            selected_square = None
            return False

def get_selected_square():
    global selected_square
    return selected_square
