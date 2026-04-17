import pygame
import os
import sys

image_size = 100     # Größe der Figur
tile_size = 100      # Größe eines Schachbrettfeldes
offset = 0           # Offset für die Positionierung der Figuren (falls benötigt)

# Pfad für gebündelte EXE anpassen
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

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

board_black = [
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
    ["wP"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["bP"] * 8,
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
]

# Bilder laden und auf image_size skalieren
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK",
              "bP", "bR", "bN", "bB", "bQ", "bK"]
    images = {}
    for piece in pieces:
        path = os.path.join(base_path, "images", f"{piece}.png")
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

# Board für die Anzeige drehen (180 Grad Rotation)
def flip_board(board):
    """
    Dreht das Board um 180 Grad für die schwarze Perspektive.
    Das erste Element wird zum letzten, invertierte Reihen und Spalten.
    """
    flipped = [[board[7-row][7-col] for col in range(8)] for row in range(8)]
    return flipped

# Koordinaten zwischen normaler und gedrehter Perspektive konvertieren
def flip_coordinates(row, col):
    """
    Konvertiert Koordinaten zwischen normaler (weiß) und gedrehter (schwarz) Perspektive.
    Von (row, col) wird zu (7-row, 7-col).
    """
    return (7 - row, 7 - col)

# Das richtige Board je nach Spielerperspektive zurückgeben
def get_display_board(board, player_color):
    """
    Gibt das Board aus der Perspektive des Spielers zurück.
    Wenn player_color == "black", wird das Board gedreht.
    Wenn player_color == "white" oder None, wird das normale Board zurückgegeben.
    """
    if player_color == "black":
        return flip_board(board)
    return board
