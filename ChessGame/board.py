import pygame
import os

image_size = 100     # Größe der Figur


# 8x8 Startposition des Schachbretts ("" = leer)
board = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["wP"] * 8,
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
]

# Bilder laden und auf image_size skalieren
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK",
              "bP", "bR", "bN", "bB", "bQ", "bK"]
    images = {}
    for piece in pieces:
        path = os.path.join("images", f"{piece}.png")
        image = pygame.image.load(path)
        images[piece] = pygame.transform.scale(image, (image_size, image_size))
    return images

# Figuren auf das Board zeichnen
def draw_pieces(screen, board, images):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "":
                x = col * tile_size + offset
                y = row * tile_size + offset
                screen.blit(images[piece], (x, y))
