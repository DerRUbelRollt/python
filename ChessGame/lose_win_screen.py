import pygame
import sys
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def show_game_over_screen(winner_color, background,screen ):
    font_big = pygame.font.SysFont(None, 80)
    font_button = pygame.font.SysFont(None, 50)

    button_rect = pygame.Rect(screen.get_width()//2 - 150, screen.get_height() - 150, 300, 60)

    color_text = (0, 0, 0) if winner_color == "white" else (255, 255, 255)
    winner_text = "Unentschieden" if winner_color == "Unentschieden" else f"{winner_color.upper()} gewinnt!"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

        # Spielfeld im Hintergrund
        screen.blit(background, (0, 0))

        # Halbtransparente Abdunkelung
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 60) if winner_color == "white" else (0, 0, 0, 60))
        screen.blit(overlay, (0, 0))

        # Gewinner-Text
        text_surf = font_big.render(winner_text, True, color_text)
        text_rect = text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text_surf, text_rect)

        # Button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (100, 100, 255) if button_rect.collidepoint(mouse_pos) else (70, 70, 200)
        pygame.draw.rect(screen, button_color, button_rect)
        button_text = font_button.render("Zurück zum Menü", True, (255, 255, 255))
        screen.blit(button_text, (
            button_rect.x + (button_rect.width - button_text.get_width()) // 2,
            button_rect.y + (button_rect.height - button_text.get_height()) // 2
        ))

        pygame.display.flip()
