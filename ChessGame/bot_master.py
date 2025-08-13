# bot_master.py
from stockfish import Stockfish
import os

# Engine starten
stockfish = Stockfish(
    path=os.path.join("engines", "stockfish.exe"),  # Pfad anpassen
    depth=20  # Tiefe für Master-Level
)
stockfish.set_skill_level(20)  # 0-20 (Master = 20)

def board_to_fen(board, current_player):
    """Wandelt dein Board-Array in FEN-String um."""
    rows = []
    for row in board:
        empty_count = 0
        fen_row = ""
        for piece in row:
            if piece == "":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                color = piece[0]
                ptype = piece[1]
                letter = ptype.lower()
                if color == "w":
                    letter = letter.upper()
                fen_row += letter
        if empty_count > 0:
            fen_row += str(empty_count)
        rows.append(fen_row)
    fen_board = "/".join(rows)

    # FEN Grundstruktur: board active_color castling en_passant halfmove fullmove
    return f"{fen_board} {'w' if current_player == 'white' else 'b'} - - 0 1"

def get_bot_e_move(board, color):
    fen = board_to_fen(board, color)
    stockfish.set_fen_position(fen)
    move = stockfish.get_best_move()
    if move:
        # Umwandeln von 'e2e4' in ((row_from, col_from), (row_to, col_to))
        col_map = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
        start = (8 - int(move[1]), col_map[move[0]])
        end = (8 - int(move[3]), col_map[move[2]])
        return (start, end)
    return None
