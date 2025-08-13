import pygame
import sys
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
is_bot_e_game = False
is_bot_b_game = False
WIDTH, HEIGHT = 800, 800
tile_size = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schachspiel")


WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
Dark_Gray = (50,50,50)  # Neue Farbe für Auswahl

# Das Spielfeld als Kopie der Startposition initialisieren
board = [row[:] for row in start_board]
piece_images = load_images()

# Schachbrett zeichnen
def draw_board(selected_square=None):
    valid_moves = []

    # Wenn ein Feld ausgewählt ist, hole die gültigen Züge
    if selected_square:
        row, col = selected_square
        piece = board[row][col]
        if piece:  # Nur wenn eine Figur vorhanden ist
            valid_moves = get_legal_moves(piece, board, row, col, current_player)

    for row in range(8):
        for col in range(8):
            # Standardfarben für Felder
            if (row + col) % 2 == 0:
                color = WHITE
            else:
                color = GRAY

            # Aktuell ausgewähltes Feld dunkler einfärben
            if selected_square == (row, col):
                color = Dark_Gray

            pygame.draw.rect(screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))

            # Gültige Züge hervorheben (hellgrün transparent)
            if (row, col) in valid_moves:
                highlight_color = (10, 190, 180, 80)  # Hellgrün, leicht transparent
                highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                highlight_surface.fill(highlight_color)
                screen.blit(highlight_surface, (col * tile_size, row * tile_size))


# Figuren zeichnen
def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "":
                screen.blit(piece_images[piece], (col * tile_size, row * tile_size))
                
def has_legal_moves(board, color):
    # Prüfe für jede Figur von `color`, ob es legalen Zug gibt
    if isinstance(color, dict):  # falls doch ein Dictionary übergeben wurde
        color = color['color']
    
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "" and piece.startswith(color[0]):
                legal_moves = get_legal_moves(piece, board, row, col, color)
                if legal_moves:
                    return True
    return False


# Hauptloop
#To start the game python main.py
game = True
running = False
mainMenu = True
while game:
    draw_board(get_selected_square())
    draw_pieces()
    pygame.display.flip()
    last_game_surface = screen.copy()
    is_bot_b_game, is_bot_e_game, current_player = main_menu(screen, last_game_surface)

    if isinstance(current_player, dict):
        if current_player["mode"] == "host":
            network_socket = current_player["socket"]
            # Hier Host-Logik starten
        elif current_player["mode"] == "client":
            network_socket = current_player["socket"]
            # Hier Client-Logik starten
    running = True
    while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if handle_click(mouse_pos, board, current_player):
                        draw_board(get_selected_square())
                        draw_pieces()
                        pygame.display.flip()
                    # Nur wenn ein gültiger Zug gemacht wurde → Spieler wechseln
                        if current_player == "white": 
                            current_player = "black"
                                # Wenn Bot-Spiel und schwarzer Spieler dran ist
                            if is_bot_b_game and current_player == "black":
                                pygame.time.delay(800)  # Kleine Pause für Bot-Zug
                                move = get_bot_b_move(board, "black")
                                if move:
                                    (from_row, from_col), (to_row, to_col) = move
                                    board[to_row][to_col] = board[from_row][from_col]
                                    board[from_row][from_col] = ""
                                    current_player = "white"
                            if is_bot_e_game and current_player == "black":
                                pygame.time.delay(800)  # Kleine Pause für Bot-Zug
                                move = get_bot_e_move(board, "black")
                                if move:
                                    (from_row, from_col), (to_row, to_col) = move
                                    board[to_row][to_col] = board[from_row][from_col]
                                    board[from_row][from_col] = ""
                                    current_player = "white"
                        else:
                            current_player = "white"

                draw_board(get_selected_square())
                draw_pieces()
                pygame.display.flip()
                # Prüfen, ob beide Könige noch da sind
                kings = [piece for row in board for piece in row if piece in ("wK", "bK")]
                if "wK" not in kings or "bK" not in kings:
                    if kings == ['wK']:
                        last_game_surface = screen.copy()
                        show_game_over_screen("white", last_game_surface, screen)
                    else:
                        last_game_surface = screen.copy()
                        show_game_over_screen("black", last_game_surface, screen)
                    board = [row[:] for row in start_board]  # Board zurücksetzen (neue Kopie)
                    mainMenu = True
                    running = False
                else:
                    # Neuer Check für Schachmatt / Patt
                    if is_king_in_check(board, current_player):
                        print(f"check current player => {current_player}")
                        if not has_legal_moves(board, current_player):
                            pygame.time.delay(800)  # Kleine Pause für Bot-Zug
                            print(f"Schachmatt! {'SCHWARZ' if current_player == 'white' else 'WEIß'} gewinnt!")
                            if current_player == 'black':
                                last_game_surface = screen.copy()
                                show_game_over_screen("white", last_game_surface, screen)
                            else:
                                last_game_surface = screen.copy()
                                show_game_over_screen("black", last_game_surface, screen)
                            board = [row[:] for row in start_board]
                            mainMenu = True
                            running = False
                    else:
                        print(f"current_player => {current_player}")
                        if not has_legal_moves(board, current_player):
                            print(f"2current_player => {current_player}")
                            if is_king_in_check(board, current_player):
                                print(f"Schachmatt! {'SCHWARZ' if current_player == 'white' else 'WEIß'} gewinnt!")
                                if current_player == 'black':
                                    last_game_surface = screen.copy()
                                    show_game_over_screen("white", last_game_surface, screen)
                                else:
                                    last_game_surface = screen.copy()
                                    show_game_over_screen("black", last_game_surface, screen)
                                board = [row[:] for row in start_board]
                                mainMenu = True
                                running = False
                            else:
                                print("Patt!")
                                last_game_surface = screen.copy()
                                show_game_over_screen("Unentschieden", last_game_surface, screen)
                                board = [row[:] for row in start_board]
                                mainMenu = True
                                running = False
                        if insufficient_material(board):
                            last_game_surface = screen.copy()
                            show_game_over_screen("Unentschieden", last_game_surface, screen)
                            print("Remis – unzureichendes Material!")
                            board = [row[:] for row in start_board]
                            mainMenu = True
                            running = False

draw_board()
draw_pieces()
pygame.quit()
sys.exit()