import pygame
import sys

# Pygame initialisieren
pygame.init()

# Fenstergröße definieren
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schachspiel")

# Farben
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Schachbrett zeichnen
def draw_board():
    tile_size = WIDTH // 8
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))

# Hauptloop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    pygame.display.flip()

pygame.quit()
sys.exit()
