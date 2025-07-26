# Merkt sich, ob eine Figur ausgewählt wurde
selected_square = None
from move_logic import get_valid_moves

def handle_click(pos, board):
    global selected_square
    tile_size = 100
    col = pos[0] // tile_size
    row = pos[1] // tile_size

    if selected_square is None:
        if board[row][col] != "":
            selected_square = (row, col)
    else:
        from_row, from_col = selected_square
        to_row, to_col = row, col

        piece = board[from_row][from_col]
        valid_moves = get_valid_moves(piece, board, from_row, from_col)

        if (to_row, to_col) in valid_moves:
            board[to_row][to_col] = piece
            board[from_row][from_col] = ""

        selected_square = None
