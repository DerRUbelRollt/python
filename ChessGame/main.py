import pygame
import sys
from board import board as start_board, load_images
from gameLogic import handle_click, get_selected_square
from bot_easy import get_bot_move
from move_logic import get_legal_moves
from utils_functions import is_king_in_check



# Pygame initialisieren
pygame.font.init()
clock = pygame.time.Clock()

current_player = "white"
is_bot_game = False
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

# Hauptloop starten
def main_menu():
    global mainMenu, current_player, is_bot_game

    screen = pygame.display.set_mode((800, 800))
    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 50)

    start_button = pygame.Rect(250, 300, 300, 60)
    bot_button = pygame.Rect(250, 400, 300, 60)
    quit_button = pygame.Rect(250, 500, 300, 60)

    while mainMenu:
        screen.fill((20, 20, 20))
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if start_button.collidepoint(mouse_pos):
                    current_player = "white"
                    is_bot_game = False
                    mainMenu = False

                elif bot_button.collidepoint(mouse_pos):
                    current_player = "white"
                    is_bot_game = True
                    mainMenu = False

                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        def draw_button(rect, text, hover_color, normal_color):
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect)
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2,
                                    rect.y + (rect.height - text_surf.get_height()) // 2))

        title_surf = font_big.render("Schachspiel", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 120))

        draw_button(start_button, "Spiel starten", (100, 100, 255), (70, 70, 200))
        draw_button(bot_button, "Einfach", (100, 255, 100), (70, 200, 70))
        draw_button(quit_button, "Beenden", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()



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
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "" and piece.startswith(color[0]):
                legal_moves = get_legal_moves(piece, board, row, col, color)
                if legal_moves:
                    return True
    return False

def show_game_over_screen(winner_color):
    font_big = pygame.font.SysFont(None, 80)
    font_button = pygame.font.SysFont(None, 50)

    button_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT - 150, 300, 60)
    
    color_text = (0, 0, 0) if winner_color == "white" else (255, 255, 255)
    overlay_color = (255, 255, 255, 200) if winner_color == "white" else (0, 0, 0, 180)
    winner_text = f"{winner_color.upper()} gewinnt!"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(overlay_color)
        screen.blit(overlay, (0, 0))

        text_surf = font_big.render(winner_text, True, color_text)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surf, text_rect)

        mouse_pos = pygame.mouse.get_pos()
        button_color = (100, 100, 255) if button_rect.collidepoint(mouse_pos) else (70, 70, 200)
        pygame.draw.rect(screen, button_color, button_rect)
        button_text = font_button.render("Zurück zum Menü", True, (255, 255, 255))
        screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2,
                                  button_rect.y + (button_rect.height - button_text.get_height()) // 2))

        pygame.display.flip()
        clock.tick(30)



# Hauptloop
#To start the game python main.py
game = True
running = False
mainMenu = True
while game:
    main_menu()  # blockiert, bis mainMenu == true

    running = True
    while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if handle_click(mouse_pos, board, current_player):
                    # Nur wenn ein gültiger Zug gemacht wurde → Spieler wechseln
                        if current_player == "white": 
                            current_player = "black"
                                # Wenn Bot-Spiel und schwarzer Spieler dran ist
                            if is_bot_game and current_player == "black":
                                pygame.time.delay(200)  # Kleine Pause für Bot-Zug
                                move = get_bot_move(board, "black")
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
                        show_game_over_screen("white")
                    else:
                        show_game_over_screen("black")
                    board = [row[:] for row in start_board]  # Board zurücksetzen (neue Kopie)
                    mainMenu = True
                    running = False
                else:
                    # Neuer Check für Schachmatt / Patt
                    if is_king_in_check(board, current_player):
                        if not has_legal_moves(board, current_player):
                            print(f"Schachmatt! {'SCHWARZ' if current_player == 'white' else 'WEIß'} gewinnt!")
                            if current_player == 'black':
                                show_game_over_screen("white")
                            else:
                                show_game_over_screen("black")
                            board = [row[:] for row in start_board]
                            mainMenu = True
                            running = False
                    else:
                        if not has_legal_moves(board, current_player):
                            print("Patt! Unentschieden!")
                            board = [row[:] for row in start_board]
                            mainMenu = True
                            running = False
draw_board()
draw_pieces()
pygame.quit()
sys.exit()