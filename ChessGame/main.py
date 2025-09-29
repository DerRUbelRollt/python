import pygame
import sys
import threading
from network_thread import start_server, connect_to_server, send_move, listen_for_moves, incoming_moves

from network import receive_move, send_move
from board import board as start_board, load_images
from gameLogic import handle_click, get_selected_square
from bots import get_bot_b_move
from move_logic import get_legal_moves
from utils_functions import is_king_in_check, insufficient_material
from main_menu import main_menu
from bot_master import get_bot_e_move
from lose_win_screen import show_game_over_screen

# Pygame initialisieren
pygame.font.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 800, 800
tile_size = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schachspiel")

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
Dark_Gray = (50, 50, 50)  # Auswahlfarbe

# Das Spielfeld als Kopie der Startposition initialisieren
board = [row[:] for row in start_board]
piece_images = load_images()



def main_game(is_host, server_ip=None):
    global current_player
    
    # Netzwerkverbindung aufbauen
    if is_host:
        conn = start_server()
    else:
        conn = connect_to_server(server_ip)

    # Thread für Eingehende Moves starten
    threading.Thread(target=listen_for_moves, args=(conn,), daemon=True).start()

    # ---- Dein pygame-Loop ----
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and current_player == "white":
                mouse_pos = pygame.mouse.get_pos()
                move = ("white", mouse_pos)
                send_move(conn, move)   # an Gegner senden
                current_player = "black"

        # Prüfen ob vom Gegner was kam
        while not incoming_moves.empty():
            move = incoming_moves.get()
            print("Verarbeite gegnerischen Move:", move)
            # hier board aktualisieren
            current_player = "white"

        # Bildschirm neu zeichnen (Board etc.)
        pygame.display.flip()

    conn.close()

def draw_board(selected_square=None, current_turn="white"):
    valid_moves = []

    if selected_square:
        row, col = selected_square
        piece = board[row][col]
        if piece:  # Nur wenn eine Figur vorhanden ist
            valid_moves = get_legal_moves(piece, board, row, col, current_turn)

    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else GRAY
            if selected_square == (r, c):
                color = Dark_Gray
            pygame.draw.rect(screen, color, (c * tile_size, r * tile_size, tile_size, tile_size))

            if (r, c) in valid_moves:
                highlight_color = (10, 190, 180, 80)
                highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                highlight_surface.fill(highlight_color)
                screen.blit(highlight_surface, (c * tile_size, r * tile_size))

def draw_pieces():
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != "":
                screen.blit(piece_images[piece], (c * tile_size, r * tile_size))

def has_legal_moves(board_state, color):
    if isinstance(color, dict):
        color = color.get('color')
    for r in range(8):
        for c in range(8):
            piece = board_state[r][c]
            if piece != "" and piece.startswith(color[0]):
                legal_moves = get_legal_moves(piece, board_state, r, c, color)
                if legal_moves:
                    return True
    return False

# ----- Hauptprogramm -----
game = True

while game:
    # Reset board zu Spielstart
    board = [row[:] for row in start_board]
    # Zeige Menü und erhalte Modus
    last_game_surface = screen.copy()
    is_bot_b_game, is_bot_e_game, menu_result = main_menu(screen, last_game_surface)

    # Initialwerte
    network_socket = None
    player_color = None   # Farbe des lokalen Spielers: "white"/"black" oder None
    turn = "white"        # wer ist gerade dran (weiß beginnt)

    # menu_result kann sein: "white" (lokal), oder dict {"mode":..., "socket":..., "color":...}
    if isinstance(menu_result, dict):
        # Multiplayer
        mode = menu_result.get("mode")
        network_socket = menu_result.get("socket")
        player_color = menu_result.get("color")  # z.B. "white" für Host, "black" für Client
        # Im Multiplayer beginnt immer Weiß (Host) — turn bleibt "white"
        threading.Thread(target=listen_for_moves, args=(network_socket,), daemon=True).start()
    else:
        # Lokalmodus oder Botmodus: menu_result == "white" (spielerfarbe irrelevant, turn="white")
        mode = "local"    
        my_color = None
        network_socket = None

    running = True
    # Spielschleife
    while running:
        # Event-Handling (immer sammeln)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # --- Multiplayer-Logik ---
        if mode in ("host", "client"):
            my_color = player_color  # Farbe, die dieser Client spielt
            # Wenn ich dran bin -> Eingaben erlauben
            if turn == my_color:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        move = handle_click(mouse_pos, board, turn)
                        if move:
                            # move erwartet ((from_row, from_col), (to_row, to_col))
                            (fr, fc), (tr, tc) = move
                            # Lokale Anwendung des Zugs
                            board[tr][tc] = board[fr][fc]
                            board[fr][fc] = ""
                            # Senden des Moves an Gegner
                            send_move(network_socket, move)
                            # Zugwechsel
                            turn = "black" if turn == "white" else "white"
            else:
                # Nicht mein Zug -> auf Move vom Gegner warten (blockiert hier)
                move = receive_move(network_socket)
                if move is None:
                    # Verbindung verloren / keine Daten
                    print("[NETWORK] Verbindung wurde getrennt oder Fehler beim Empfangen.")
                    running = False
                    break
                (fr, fc), (tr, tc) = move
                board[tr][tc] = board[fr][fc]
                board[fr][fc] = ""
                turn = "black" if turn == "white" else "white"

        # --- Lokale/ Bot-Logik (kein Netzwerk) ---
        else:
            # Verarbeiten von Klicks nur wenn dran (turn toggles)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    move_made = handle_click(mouse_pos, board, turn)
                    if move_made:
                        draw_board(get_selected_square(), current_turn=turn)
                        draw_pieces()
                        pygame.display.flip()
                        pygame.time.delay(700)
                        
                        # Falls move_made ist True, handle_click hat intern das Board geändert
                        # (Wenn deine handle_click nur markiert, dann du musst selbst anwenden)
                        # Wir hier setzen turn um und evtl. Botzüge ausführen
                        turn = "black" if turn == "white" else "white"

                        # Bot-Logic: wenn Bot-Spiel aktiv und Bot ist dran (schwarz)
                        if turn == "black" and is_bot_b_game:
                            
                            move = get_bot_b_move(board, "black")
                            if move:
                                (fr, fc), (tr, tc) = move
                                board[tr][tc] = board[fr][fc]
                                board[fr][fc] = ""
                                turn = "white"
                        if turn == "black" and is_bot_e_game:
                            move = get_bot_e_move(board, "black")
                            if move:
                                (fr, fc), (tr, tc) = move
                                board[tr][tc] = board[fr][fc]
                                board[fr][fc] = ""
                                turn = "white"
                
        # Drawing
        draw_board(get_selected_square(), current_turn=turn)
        draw_pieces()
        pygame.display.flip()
        clock.tick(60)

        # --- Spielende-Prüfungen ---
        kings = [p for row in board for p in row if p in ("wK", "bK")]
        if "wK" not in kings or "bK" not in kings:
            if kings == ['wK']:
                last_game_surface = screen.copy()
                show_game_over_screen("white", last_game_surface, screen)
            else:
                last_game_surface = screen.copy()
                show_game_over_screen("black", last_game_surface, screen)
            board = [row[:] for row in start_board]
            running = False
            break

        # Checkmate / Patt / Remis
        if is_king_in_check(board, turn):
            if not has_legal_moves(board, turn):
                winner = "white" if turn == "black" else "black"
                last_game_surface = screen.copy()
                show_game_over_screen(winner, last_game_surface, screen)
                board = [row[:] for row in start_board]
                running = False
                break
        else:
            if not has_legal_moves(board, turn):
                last_game_surface = screen.copy()
                show_game_over_screen("Unentschieden", last_game_surface, screen)
                board = [row[:] for row in start_board]
                running = False
                break

        if insufficient_material(board):
            last_game_surface = screen.copy()
            show_game_over_screen("Unentschieden", last_game_surface, screen)
            board = [row[:] for row in start_board]
            running = False
            break

# Ende Hauptschleife
pygame.quit()
sys.exit()
