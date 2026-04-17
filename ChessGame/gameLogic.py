# Merkt sich, ob eine Figur ausgewählt wurde
selected_square = None
from move_logic import get_legal_moves, apply_move
from board import flip_coordinates

tile_size = 100
board_offset_x = 200

def handle_click(pos, board, current_player, player_perspective="white"):
    """
    Verarbeitet Klicks auf das Board.
    player_perspective kann "white" oder "black" sein und bestimmt, 
    ob die Koordinaten umgekehrt werden.
    """
    global selected_square
    col = (pos[0] - board_offset_x) // tile_size 
    row = pos[1] // tile_size

    if col < 0 or col > 7 or row < 0 or row > 7:
        return None  # Klick außerhalb des Boards

    # Wenn von schwarzer Perspektive gespielt wird, Koordinaten konvertieren
    if player_perspective == "black":
        row, col = flip_coordinates(row, col)

    # Falls noch keine Figur ausgewählt
    if selected_square is None:
        piece = board[row][col]
        if piece != "":
            if current_player == "white" and not piece.startswith("w"):
                return None
            if current_player == "black" and not piece.startswith("b"):
                return None
            selected_square = (row, col)
        return None

    # Falls schon Figur ausgewählt → versuche Zug
    else:
        from_row, from_col = selected_square
        to_row, to_col = row, col
        piece = board[from_row][from_col]
        
        valid_moves = get_legal_moves(piece, board, from_row, from_col, current_player)

        if (to_row, to_col) in valid_moves:
            move = ((from_row, from_col), (to_row, to_col))
            selected_square = None
            return move
        else:
            selected_square = None
            return None


def get_selected_square():
    return selected_square
