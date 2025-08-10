from copy import deepcopy
from utils_functions import is_king_in_check  # Das brauchst du noch, siehe unten

def get_legal_moves(piece, board, row, col, color):
    valid_moves = get_valid_moves(piece, board, row, col)
    legal_moves = []

    for move in valid_moves:
        test_board = deepcopy(board)

        # Simuliere den Zug
        target_row, target_col = move
        test_board[target_row][target_col] = piece
        test_board[row][col] = ""

        # Prüfe, ob König nach dem Zug im Schach ist
        if not is_king_in_check(test_board, color):
            legal_moves.append(move)

    return legal_moves



def is_path_clear(board, from_row, from_col, to_row, to_col):
    delta_row = to_row - from_row
    delta_col = to_col - from_col

    step_row = (delta_row > 0) - (delta_row < 0)
    step_col = (delta_col > 0) - (delta_col < 0)

    row, col = from_row + step_row, from_col + step_col
    while (row, col) != (to_row, to_col):
        if board[row][col] != "":
            return False
        row += step_row
        col += step_col
    return True


def get_valid_moves(piece, board, row, col):
    if piece == "":
        return []

    color = piece[0]  # "w" oder "b"
    name = piece[1].upper()
    moves = []

    direction = -1 if color == "w" else 1  # nach oben für weiß, unten für schwarz

    if name == "P":  # Bauer
        # Ein Schritt vor
        if 0 <= row + direction < 8 and board[row + direction][col] == "":
            moves.append((row + direction, col))
            
            # Zwei Schritte vom Startfeld
            if (color == "w" and row == 6) or (color == "b" and row == 1):
                if board[row + 2*direction][col] == "":
                    moves.append((row + 2*direction, col))
        if (color == "w" and row == 0): 
            board[row][col] = "wQ"
        if (color == "b" and row == 7):
            board[row][col] = "bQ"
        # Schlagen
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                target = board[new_row][new_col]
                if target != "" and target[0] != color:
                    moves.append((new_row, new_col))

    elif name == "N":  # Springer
        steps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                 (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in steps:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target == "" or target[0] != color:
                    moves.append((r, c))

    elif name == "B":  # Läufer
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr*i, col + dc*i
                if 0 <= r < 8 and 0 <= c < 8:
                    if is_path_clear(board, row, col, r, c):
                        target = board[r][c]
                        if target == "":
                            moves.append((r, c))
                        elif target[0] != color:
                            moves.append((r, c))
                            break
                        else:
                            break
                    else:
                        break

    elif name == "R":  # Turm
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr*i, col + dc*i
                if 0 <= r < 8 and 0 <= c < 8:
                    if is_path_clear(board, row, col, r, c):
                        target = board[r][c]
                        if target == "":
                            moves.append((r, c))
                        elif target[0] != color:
                            moves.append((r, c))
                            break
                        else:
                            break
                    else:
                        break

    elif name == "Q":  # Dame
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                      (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr*i, col + dc*i
                if 0 <= r < 8 and 0 <= c < 8:
                    if is_path_clear(board, row, col, r, c):
                        target = board[r][c]
                        if target == "":
                            moves.append((r, c))
                        elif target[0] != color:
                            moves.append((r, c))
                            break
                        else:
                            break
                    else:
                        break

    elif name == "K":  # König
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if target == "" or target[0] != color:
                        moves.append((r, c))

    return moves
