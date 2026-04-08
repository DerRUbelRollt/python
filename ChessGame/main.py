import pygame
import sys
import threading
from Network.network_thread import start_server, connect_to_server, send_move, listen_for_moves, incoming_moves
from board import board as start_board, load_images
from gameLogic import handle_click, get_selected_square
from bots import get_bot_b_move, get_bot_a_move
from move_logic import get_legal_moves, apply_move, check_promotion, promote_pawn
from utils_functions import is_king_in_check, insufficient_material
from main_menu import main_menu
from lose_win_screen import show_game_over_screen

# Pygame initialisieren
pygame.font.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 1200, 800
board_offset_x = 200
board_size = 800
tile_size = board_size // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schachspiel")

WHITE = (240, 217, 181)  # Hellbraun für helle Felder
GRAY = (181, 136, 99)   # Dunkelbraun für dunkle Felder
Dark_Gray = (50, 50, 50)  # Auswahlfarbe

# Das Spielfeld als Kopie der Startposition initialisieren
board = [row[:] for row in start_board]
piece_images = load_images()

# Geschlagene Figuren
captured_white = []
captured_black = []



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
            pygame.draw.rect(screen, color, (board_offset_x + c * tile_size, r * tile_size, tile_size, tile_size))

            if (r, c) in valid_moves:
                highlight_color = (10, 190, 180, 80)
                highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                highlight_surface.fill(highlight_color)
                screen.blit(highlight_surface, (board_offset_x + c * tile_size, r * tile_size))

def draw_pieces():
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != "":
                screen.blit(piece_images[piece], (board_offset_x + c * tile_size, r * tile_size))

def draw_captured_pieces():
    # Fülle die Seitenbereiche mit hellbraun
    side_color = WHITE  # Hellbraun
    pygame.draw.rect(screen, side_color, (0, 0, board_offset_x, HEIGHT))  # Linke Seite
    pygame.draw.rect(screen, side_color, (board_offset_x + board_size, 0, WIDTH - (board_offset_x + board_size), HEIGHT))  # Rechte Seite

    small_size = 50
    left_x = 50
    right_x = WIDTH - 50 - small_size
    y_start = 50

    for i, piece in enumerate(captured_white):
        if piece in piece_images:
            img = pygame.transform.scale(piece_images[piece], (small_size, small_size))
            screen.blit(img, (left_x, y_start + i * (small_size + 10)))

    for i, piece in enumerate(captured_black):
        if piece in piece_images:
            img = pygame.transform.scale(piece_images[piece], (small_size, small_size))
            screen.blit(img, (right_x, y_start + i * (small_size + 10)))

def draw_board_border(current_turn):
    # Dicker farbiger Rand um das Brett, der anzeigt wer am Zug ist
    if current_turn == "white":
        border_color = (0, 255, 0)  # Grün für Weiß
    else:
        border_color = (255, 0, 0)  # Rot für Schwarz
    
    border_width = 8  # Dicker Rand für bessere Sichtbarkeit
    # Zeichne den Rand um das Brett, leicht versetzt um den Rand zu erweitern
    pygame.draw.rect(screen, border_color, (board_offset_x - border_width//2, -border_width//2, board_size + border_width, board_size + border_width), border_width)

def show_promotion_dialog(screen, color):
    """
    Zeigt ein kleines Dialog-Fenster mit den 4 Promotion-Optionen als Bilder in 2x2 Grid.
    Gibt die gewählte Figur zurück: "Q", "R", "N" oder "B"
    Layout:
    Dame  | Turm
    ------+------
    Läufer| Springer
    """
    font_title = pygame.font.SysFont(None, 40)
    
    # Kleineres Dialog-Fenster
    dialog_width = 300
    dialog_height = 320
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2
    
    # 2x2 Grid mit Buttons
    button_size = 100
    button_spacing = 10
    grid_start_x = dialog_x + 25
    grid_start_y = dialog_y + 70
    
    # Promotion-Optionen im 2x2 Format: (Figur-Code, x, y)
    promotion_pieces = [
        (color + "Q", grid_start_x, grid_start_y),                                      # Dame (oben links)
        (color + "R", grid_start_x + button_size + button_spacing, grid_start_y),       # Turm (oben rechts)
        (color + "B", grid_start_x, grid_start_y + button_size + button_spacing),       # Läufer (unten links)
        (color + "N", grid_start_x + button_size + button_spacing, grid_start_y + button_size + button_spacing)  # Springer (unten rechts)
    ]
    
    selecting = True
    choice = None
    
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for piece_code, x, y in promotion_pieces:
                    button_rect = pygame.Rect(x, y, button_size, button_size)
                    if button_rect.collidepoint(mouse_pos):
                        choice = piece_code[1]  # Extrahiere Figur-Typ (Q, R, B, N)
                        selecting = False
        
        # Zeichne Dialog-Hintergrund
        pygame.draw.rect(screen, (200, 200, 200), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, (0, 0, 0), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        # Titel
        title_surf = font_title.render("Umwandeln:", True, (0, 0, 0))
        screen.blit(title_surf, (dialog_x + (dialog_width - title_surf.get_width()) // 2, dialog_y + 15))
        
        # Figur-Buttons mit Bildern in 2x2 Grid
        mouse_pos = pygame.mouse.get_pos()
        for piece_code, x, y in promotion_pieces:
            button_rect = pygame.Rect(x, y, button_size, button_size)
            is_hovered = button_rect.collidepoint(mouse_pos)
            button_color = (150, 200, 150) if is_hovered else (100, 180, 100)
            
            # Button-Hintergrund
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, (0, 0, 0), button_rect, 3 if is_hovered else 2)
            
            # Figur-Bild
            if piece_code in piece_images:
                piece_img = pygame.transform.scale(piece_images[piece_code], (button_size - 20, button_size - 20))
                screen.blit(piece_img, (x + 10, y + 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    return choice

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
    captured_white = []
    captured_black = []
    # Zeige Menü und erhalte Modus
    last_game_surface = screen.copy()
    is_bot_game, bot_type, menu_result = main_menu(screen, last_game_surface)

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
            my_color = player_color

            # 🧠 1. Gegner-Züge IMMER zuerst verarbeiten (nicht blockierend!)
            while not incoming_moves.empty():
                move = incoming_moves.get()

                print("[NETWORK] Gegnerzug:", move)

                # Track captured
                (fr, fc), (tr, tc) = move
                captured = board[tr][tc] if board[tr][tc] != "" else None

                apply_move(board, move)

                # Prüfe Promotion
                needs_promotion, pawn_color = check_promotion(board, tr, tc)
                if needs_promotion:
                    promotion_choice = show_promotion_dialog(screen, pawn_color)
                    promote_pawn(board, tr, tc, promotion_choice)

                if captured:
                    if turn == "white":
                        captured_black.append(captured)
                    else:
                        captured_white.append(captured)

                turn = "black" if turn == "white" else "white"

            # 🧠 2. Nur wenn ich dran bin → Eingabe erlauben
            if turn == my_color:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        move = handle_click(mouse_pos, board, turn)

                        if move:
                            print("[NETWORK] Sende Zug:", move)

                            # Track captured
                            (fr, fc), (tr, tc) = move
                            captured = board[tr][tc] if board[tr][tc] != "" else None

                            # Lokalen Zug anwenden
                            apply_move(board, move)

                            # Prüfe Promotion (für Spieler)
                            needs_promotion, pawn_color = check_promotion(board, tr, tc)
                            if needs_promotion:
                                promotion_choice = show_promotion_dialog(screen, pawn_color)
                                promote_pawn(board, tr, tc, promotion_choice)

                            if captured:
                                if turn == "white":
                                    captured_white.append(captured)
                                else:
                                    captured_black.append(captured)

                            # Senden
                            send_move(network_socket, move)

                            # Zug wechseln
                            turn = "black" if turn == "white" else "white"

        # --- Lokale/ Bot-Logik (kein Netzwerk) ---
        else:
            # Verarbeiten von Klicks nur wenn dran (turn toggles)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    move = handle_click(mouse_pos, board, turn)
                    if move:
                        # Track captured
                        (fr, fc), (tr, tc) = move
                        captured = board[tr][tc] if board[tr][tc] != "" else None

                        apply_move(board, move)

                        # Prüfe Promotion
                        needs_promotion, pawn_color = check_promotion(board, tr, tc)
                        if needs_promotion:
                            promotion_choice = show_promotion_dialog(screen, pawn_color)
                            promote_pawn(board, tr, tc, promotion_choice)

                        if captured:
                            if turn == "white":
                                captured_white.append(captured)
                            else:
                                captured_black.append(captured)

                        draw_board(get_selected_square(), current_turn=turn)
                        draw_pieces()
                        pygame.display.flip()
                        pygame.time.delay(700)
                        
                        # Zug wechseln
                        turn = "black" if turn == "white" else "white"

                        # Bot-Logic: wenn Bot-Spiel aktiv und Bot ist dran (schwarz)
                        if turn == "black" and is_bot_game:
                            
                            if bot_type == "advanced":
                                move = get_bot_a_move(board, "black")
                            else:
                                move = get_bot_b_move(board, "black")
                            
                            if move:
                                (fr, fc), (tr, tc) = move
                                captured = board[tr][tc] if board[tr][tc] != "" else None

                                board[tr][tc] = board[fr][fc]
                                board[fr][fc] = ""

                                # Prüfe Promotion
                                needs_promotion, pawn_color = check_promotion(board, tr, tc)
                                if needs_promotion:
                                    promotion_choice = show_promotion_dialog(screen, pawn_color)
                                    promote_pawn(board, tr, tc, promotion_choice)
                                
                                if captured:
                                    captured_black.append(captured)

                                turn = "white"
                
        # Drawing
        draw_board(get_selected_square(), current_turn=turn)
        draw_board_border(turn)
        draw_pieces()
        draw_captured_pieces()
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
