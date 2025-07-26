import pygame
import sys
from board import board, load_images  # <-- hier importierst du
from gameLogic import handle_click

# Pygame initialisieren
pygame.init()

WIDTH, HEIGHT = 800, 800
tile_size = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schachspiel")

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Bilder laden
piece_images = load_images()

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
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            
            mouse_pos = pygame.mouse.get_pos()
            handle_click(mouse_pos, board)    

    draw_board()
    draw_pieces()
    pygame.display.flip()

pygame.quit()
sys.exit()
