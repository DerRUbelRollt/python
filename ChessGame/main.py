import pygame
import sys
import threading
import time
from Network.network_thread import start_server, connect_to_server, send_move, listen_for_moves, incoming_moves, is_connection_alive
from board import board as start_board, load_images, get_display_board, flip_coordinates
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

# Disconnect-Status für Multiplayer
disconnect_time = None
reconnect_countdown = 60  # 60 Sekunden Wartezeit
is_disconnected = False
waiting_for_reconnect = False

def try_reconnect_to_server(server_ip, port=5005, max_attempts=5):
    """Versucht, sich wieder mit dem Server zu verbinden"""
    for attempt in range(max_attempts):
        try:
            print(f"[RECONNECT] Versuch {attempt + 1}/{max_attempts}...")
            sock = connect_to_server(server_ip, port)
            print("[RECONNECT] Erfolgreich wieder verbunden!")
            return sock
        except Exception as e:
            print(f"[RECONNECT] Versuch {attempt + 1} fehlgeschlagen: {e}")
            time.sleep(1)
    print("[RECONNECT] Alle Versuche fehlgeschlagen.")
    return None



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

def draw_board(selected_square=None, current_turn="white", display_board=None, player_perspective="white"):
    """
    Zeichnet das Schachbrett.
    display_board: Das Board das angezeigt werden soll (kann eine gedrehte Variante sein)
    Falls None, wird das globale board verwendet.
    player_perspective: "white" oder "black" für die Anzeige/Highlight-Logik.
    """
    if display_board is None:
        display_board = board
        
    valid_moves = []
    display_selected = None

    if selected_square:
        if player_perspective == "black":
            display_selected = flip_coordinates(*selected_square)
        else:
            display_selected = selected_square

        row, col = display_selected
        piece = display_board[row][col]
        if piece:  # Nur wenn eine Figur vorhanden ist
            valid_moves = get_legal_moves(piece, board, selected_square[0], selected_square[1], current_turn)
            if player_perspective == "black":
                valid_moves = [flip_coordinates(r, c) for r, c in valid_moves]

    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else GRAY
            if display_selected == (r, c):
                color = Dark_Gray
            pygame.draw.rect(screen, color, (board_offset_x + c * tile_size, r * tile_size, tile_size, tile_size))

            if (r, c) in valid_moves:
                highlight_color = (10, 190, 180, 80)
                highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                highlight_surface.fill(highlight_color)
                screen.blit(highlight_surface, (board_offset_x + c * tile_size, r * tile_size))

def draw_pieces(display_board=None):
    """
    Zeichnet die Figuren auf das Board.
    display_board: Das Board das angezeigt werden soll (kann eine gedrehte Variante sein)
    Falls None, wird das globale board verwendet.
    """
    if display_board is None:
        display_board = board
        
    for r in range(8):
        for c in range(8):
            piece = display_board[r][c]
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

    # Stelle sicher, dass links immer schwarze Figuren und rechts immer weiße Figuren stehen.
    black_captured = [p for p in captured_white + captured_black if p.startswith('b')]
    white_captured = [p for p in captured_white + captured_black if p.startswith('w')]

    for i, piece in enumerate(black_captured):
        if piece in piece_images:
            img = pygame.transform.scale(piece_images[piece], (small_size, small_size))
            screen.blit(img, (left_x, y_start + i * (small_size + 10)))

    for i, piece in enumerate(white_captured):
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
    
    # Reset Disconnect-Status
    disconnect_time = None
    is_disconnected = False
    waiting_for_reconnect = False
    
    # Zeige Menü und erhalte Modus
    last_game_surface = screen.copy()
    is_bot_game, bot_type, menu_result = main_menu(screen, last_game_surface)

    # Initialwerte
    network_socket = None
    player_color = None   # Farbe des lokalen Spielers: "white"/"black" oder None
    turn = "white"        # wer ist gerade dran (weiß beginnt)
    server_ip = None      # IP-Adresse für Reconnect

    # menu_result kann sein: "white" (lokal), oder dict {"mode":..., "socket":..., "color":...}
    if isinstance(menu_result, dict):
        # Multiplayer
        mode = menu_result.get("mode")
        network_socket = menu_result.get("socket")
        player_color = menu_result.get("color")  # z.B. "white" für Host, "black" für Client
        server_ip = menu_result.get("server_ip")  # Speichere IP für Reconnect
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Prüfe Zurück-Button
                back_button_rect = pygame.Rect(10, 10, 80, 40)
                if back_button_rect.collidepoint(mouse_pos):
                    # Zurück zum Menü - Netzwerkverbindung schließen falls vorhanden
                    if network_socket and not waiting_for_reconnect:
                        if mode == "host":
                            # Host verlässt Spiel - starte Wartezeit für Client
                            waiting_for_reconnect = True
                            disconnect_time = time.time()
                            print("[DISCONNECT] Host hat das Spiel verlassen. Warte auf Reconnect...")
                        else:
                            # Client verlässt Spiel - schließe Verbindung sofort
                            network_socket.close()
                    elif waiting_for_reconnect:
                        # Während Wartezeit: Verbindung schließen und zurück zum Menü
                        if network_socket:
                            network_socket.close()
                        running = False
                        continue
                    else:
                        running = False
                        continue

        # --- Multiplayer-Logik ---
        if mode in ("host", "client") and not waiting_for_reconnect:
            my_color = player_color
            display_board = get_display_board(board, player_color)

            # Prüfe auf Disconnect
            if not is_connection_alive(network_socket):
                if not is_disconnected:
                    is_disconnected = True
                    disconnect_time = time.time()
                    print("[DISCONNECT] Verbindung unterbrochen!")

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

            # 🧠 2. Reconnect-Logik falls disconnected
            if is_disconnected and mode == "client" and server_ip:
                print("[RECONNECT] Versuche Reconnect...")
                new_socket = try_reconnect_to_server(server_ip)
                if new_socket:
                    network_socket = new_socket
                    is_disconnected = False
                    disconnect_time = None
                    # Starte neuen Listen-Thread
                    threading.Thread(target=listen_for_moves, args=(network_socket,), daemon=True).start()
                    print("[RECONNECT] Erfolgreich wieder verbunden!")
                else:
                    print("[RECONNECT] Reconnect fehlgeschlagen.")

            # 🧠 3. Wartezeit-Logik für Host
            if waiting_for_reconnect and mode == "host":
                elapsed = time.time() - disconnect_time
                remaining = max(0, reconnect_countdown - elapsed)
                
                if remaining <= 0:
                    # Wartezeit abgelaufen - Verbindung schließen
                    print("[DISCONNECT] Wartezeit abgelaufen. Verbindung wird geschlossen.")
                    if network_socket:
                        network_socket.close()
                    running = False
                    continue

            # 🧠 4. Nur wenn ich dran bin → Eingabe erlauben (und nicht disconnected)
            if turn == my_color and not is_disconnected and not waiting_for_reconnect:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        move = handle_click(mouse_pos, board, turn, player_perspective=player_color)

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
        if mode in ("host", "client"):
            display_board = get_display_board(board, player_color)
            draw_board(get_selected_square(), current_turn=turn, display_board=display_board, player_perspective=player_color)
        else:
            draw_board(get_selected_square(), current_turn=turn)
        
        draw_board_border(turn)
        
        if mode in ("host", "client"):
            display_board = get_display_board(board, player_color)
            draw_pieces(display_board)
        else:
            draw_pieces()
            
        draw_captured_pieces()
                # Zeichne Disconnect-Overlay falls nötig
        if waiting_for_reconnect and mode == "host":
            # Grauer Schleier
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((100, 100, 100, 150))  # Leichter grauer Schleier
            screen.blit(overlay, (0, 0))
            
            # Countdown-Text
            elapsed = time.time() - disconnect_time
            remaining = max(0, reconnect_countdown - elapsed)
            font_large = pygame.font.SysFont(None, 80)
            font_small = pygame.font.SysFont(None, 40)
            
            countdown_text = font_large.render(f"{int(remaining)}", True, (255, 255, 255))
            info_text = font_small.render("Warte auf Reconnect...", True, (255, 255, 255))
            
            # Zentriere Texte
            screen.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 20))
        
        elif is_disconnected and mode == "client":
            # Disconnect-Info für Client
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((150, 50, 50, 100))  # Rötlicher Schleier für Disconnect
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.SysFont(None, 50)
            disconnect_text = font.render("Verbindung unterbrochen - Reconnect...", True, (255, 255, 255))
            screen.blit(disconnect_text, (WIDTH//2 - disconnect_text.get_width()//2, HEIGHT//2))
                # Zeichne Zurück-Button oben links
        back_button_rect = pygame.Rect(10, 10, 80, 40)
        mouse_pos = pygame.mouse.get_pos()
        button_color = (100, 150, 255) if back_button_rect.collidepoint(mouse_pos) else (70, 100, 200)
        pygame.draw.rect(screen, button_color, back_button_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), back_button_rect, 2, border_radius=5)
        
        font = pygame.font.SysFont(None, 30)
        back_text = font.render(" Back", True, (255, 255, 255))
        screen.blit(back_text, (back_button_rect.x + 5, back_button_rect.y + 8))
        
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
