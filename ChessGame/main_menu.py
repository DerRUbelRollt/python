import pygame
import sys

def main_menu(screen, background):
    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 50)

    start_button = pygame.Rect(250, 300, 300, 60)
    bot_button_b = pygame.Rect(250, 400, 300, 60)
    bot_button_e = pygame.Rect(250, 500, 300, 60)
    quit_button = pygame.Rect(250, 600, 300, 60)

    while True:
        # Hintergrund: letztes Spielfeld
        screen.blit(background, (0, 0))

        # Halbtransparente Abdunkelung
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_pos):
                    return False, False, "white"
                elif bot_button_b.collidepoint(mouse_pos):
                    return True, False, "white"
                elif bot_button_e.collidepoint(mouse_pos):
                    return False, True, "white"
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        def draw_button(rect, text, hover_color, normal_color):
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect)
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        title_surf = font_big.render("Schachspiel", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 120))

        draw_button(start_button, "Lokal 2 Player", (100, 100, 255), (70, 70, 200))
        draw_button(bot_button_b, "KI  BEGINNER", (100, 255, 100), (70, 200, 70))
        draw_button(bot_button_e, "KI  EXPERT", (100, 255, 100), (70, 200, 70))
        draw_button(quit_button, "Beenden", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()
