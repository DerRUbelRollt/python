import pygame
import sys
from board import board as start_board, load_images
from gameLogic import handle_click, get_selected_square
from bot_easy import get_bot_move



# Pygame initialisieren
pygame.init()
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
    for row in range(8):
        for col in range(8):
            if selected_square == (row, col):
                color = Dark_Gray
            else:
                color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))

# Figuren zeichnen
def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "":
                screen.blit(piece_images[piece], (col * tile_size, row * tile_size))

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
                        print(f"Spiel beendet! WEIß gewinnt")
                    else:
                        print(f"Spiel beendet! SCHWARZ  gewinnt")
                    draw_pieces()
                    board = [row[:] for row in start_board]  # Board zurücksetzen (neue Kopie)
                    mainMenu = True
                    running = False
draw_board()
draw_pieces()
pygame.quit()
sys.exit()