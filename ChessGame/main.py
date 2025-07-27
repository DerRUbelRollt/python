import pygame
import sys
from board import board as start_board, load_images
from gameLogic import handle_click


# Pygame initialisieren
pygame.init()

WIDTH, HEIGHT = 800, 800
tile_size = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schachspiel")

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)


# Das Spielfeld als Kopie der Startposition initialisieren
board = [row[:] for row in start_board]
piece_images = load_images()

# Hauptloop starten
def main_menu():
    global mainMenu
    while mainMenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Button "Spiel starten"
                if start_button.collidepoint(mouse_pos):
                    mainMenu = False
                    running = True
                # Button "Beenden"
                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        screen.fill(WHITE)
        font = pygame.font.Font(None, 74)
        text = font.render("Schachspiel", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        # Buttons zeichnen
        button_font = pygame.font.Font(None, 50)
        start_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 60)
        pygame.draw.rect(screen, GRAY, start_button)
        pygame.draw.rect(screen, GRAY, quit_button)
        start_text = button_font.render("Spiel starten", True, (0, 0, 0))
        quit_text = button_font.render("Beenden", True, (0, 0, 0))
        screen.blit(start_text, (start_button.x + 30, start_button.y + 10))
        screen.blit(quit_text, (quit_button.x + 80, quit_button.y + 10))

        pygame.display.flip()

# Schachbrett zeichnen
def draw_board():
    for row in range(8):
        for col in range(8):
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
game = True
running = False
mainMenu = True
while game:
    while mainMenu:
        main_menu()
        if mainMenu == False:
            running = True
        while running:
            for event in pygame.event.get():
        
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    handle_click(mouse_pos, board)

                draw_board()
                draw_pieces()
                pygame.display.flip()
                # Prüfen, ob beide Könige noch da sind
                kings = [piece for row in board for piece in row if piece in ("wK", "bK")]
                if "wK" not in kings or "bK" not in kings:
                    print("Spiel beendet! Ein König fehlt.")
                    draw_pieces()
                    board = [row[:] for row in start_board]  # Board zurücksetzen (neue Kopie)
                    mainMenu = True
                    running = False
                
        
    

draw_board()
draw_pieces()
pygame.quit()
sys.exit()