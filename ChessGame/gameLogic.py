# Merkt sich, ob eine Figur ausgewählt wurde
selected_square = None
from move_logic import get_legal_moves, apply_move
from network import send_move, receive_move

network_socket = None
rochade_valid_w = 0
rochade_valid_b = 0

def handle_click(pos, board, current_player):
    global selected_square, rochade_valid_w, rochade_valid_b
    tile_size = 100
    col = pos[0] // tile_size 
    row = pos[1] // tile_size

    # Falls noch keine Figur ausgewählt
    if selected_square is None:
        piece = board[row][col]
        if piece != "":
            if current_player == "white" and not piece.startswith("w"):
                return False
            if current_player == "black" and not piece.startswith("b"):
                return False
            selected_square = (row, col)
        return False

    # Falls schon Figur ausgewählt → versuche Zug
    else:
        from_row, from_col = selected_square
        to_row, to_col = row, col
        piece = board[from_row][from_col]
        
        valid_moves = get_legal_moves(piece, board, from_row, from_col, current_player)

        if (to_row, to_col) in valid_moves:
            # Rochade
            if piece[1].upper() == "K":
                if piece.startswith("w") and from_row == 7 and from_col == 4 and rochade_valid_w == 0:
                    rochade_valid_w = 1
                    if to_row == 7 and to_col == 6:
                        board[7][7], board[7][5] = "", "wR"
                    elif to_row == 7 and to_col == 2:
                        board[7][0], board[7][3] = "", "wR"
                if piece.startswith("b") and from_row == 0 and from_col == 4 and rochade_valid_b == 0:
                    rochade_valid_b = 1
                    if to_row == 0 and to_col == 6:
                        board[0][7], board[0][5] = "", "bR"
                    elif to_row == 0 and to_col == 2:
                        board[0][0], board[0][3] = "", "bR"

            # Zug anwenden (lokal)
            move = ((from_row, from_col), (to_row, to_col))
            apply_move(board, move)

            # Falls im Netzwerkmodus → Zug senden
            if network_socket:
                send_move(network_socket, move)

            selected_square = None
            return True
        else:
            selected_square = None
            return False


def get_selected_square():
    return selected_square

def get_rochade_valid(color):
    return rochade_valid_w if color == "w" else rochade_valid_b
