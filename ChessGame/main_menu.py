import pygame
import sys
import subprocess
import threading
from Network.network_thread import start_server, connect_to_server, send_move, listen_for_moves, incoming_moves
from Network.lan_discovery import broadcast_host, listen_for_hosts

network_socket = None

def multiplayer_menu(screen, background):
    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 50)

    host_button = pygame.Rect(250, 300, 300, 60)
    find_button = pygame.Rect(250, 400, 300, 60)
    back_button = pygame.Rect(250, 500, 300, 60)

    while True:
        screen.blit(background, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if host_button.collidepoint(mouse_pos):
                    result = host_game_screen(screen, background)
                    if result:
                        return result
                elif find_button.collidepoint(mouse_pos):
                    result = find_game_screen(screen, background)
                    if result:
                        return result
                elif back_button.collidepoint(mouse_pos):
                    return None

        def draw_button(rect, text, hover_color, normal_color):
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect)
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        title_surf = font_big.render("Multiplayer", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 120))
        
        draw_button(host_button, "Host Game", (100, 100, 255), (70, 70, 200))
        draw_button(find_button, "Find Game", (100, 100, 255), (70, 70, 200))
        draw_button(back_button, "Back", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()

def host_game_screen(screen, background):
    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 50)

    back_button = pygame.Rect(250, 600, 300, 60)

    # Shared variable for connection
    conn = [None]

    def server_thread():
        try:
            conn[0] = start_server()
        except Exception as e:
            print(f"Server error: {e}")

    # Start server thread
    threading.Thread(target=server_thread, daemon=True).start()

    # Start broadcast thread
    threading.Thread(target=broadcast_host, args=(5005,), daemon=True).start()

    while True:
        screen.blit(background, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(mouse_pos):
                    return None

        # Check if connected
        if conn[0] is not None:
            return {"mode": "host", "socket": conn[0], "color": "white"}

        def draw_button(rect, text, hover_color, normal_color):
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect)
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        title_surf = font_big.render("Hosting Game", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 120))

        waiting_surf = font.render("Warte auf Spieler...", True, (255, 255, 255))
        screen.blit(waiting_surf, (screen.get_width() // 2 - waiting_surf.get_width() // 2, 300))

        draw_button(back_button, "Back", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()

def find_game_screen(screen, background):
    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 50)

    back_button = pygame.Rect(250, 600, 300, 60)
    found_hosts = []
    selected_index = 0

    # Start listening thread
    threading.Thread(target=listen_for_hosts, args=(found_hosts,), daemon=True).start()

    while True:
        screen.blit(background, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and found_hosts:
                    selected_index = (selected_index - 1) % len(found_hosts)
                elif event.key == pygame.K_DOWN and found_hosts:
                    selected_index = (selected_index + 1) % len(found_hosts)
                elif event.key == pygame.K_RETURN and found_hosts:
                    host_ip, port = found_hosts[selected_index]
                    try:
                        sock = connect_to_server(host_ip, int(port))
                        return {"mode": "client", "socket": sock, "color": "black"}
                    except Exception as e:
                        print(f"Connection error: {e}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(mouse_pos):
                    return None
                # Check if clicked on a host
                for i, (ip, port) in enumerate(found_hosts):
                    rect = pygame.Rect(200, 250 + i * 50, 400, 40)
                    if rect.collidepoint(mouse_pos):
                        selected_index = i
                        try:
                            sock = connect_to_server(ip, int(port))
                            return {"mode": "client", "socket": sock, "color": "black"}
                        except Exception as e:
                            print(f"Connection error: {e}")

        def draw_button(rect, text, hover_color, normal_color):
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect)
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        title_surf = font_big.render("Find Game", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 120))

        # Draw found hosts
        for i, (ip, port) in enumerate(found_hosts):
            color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            host_surf = font.render(f"{ip}:{port}", True, color)
            screen.blit(host_surf, (200, 250 + i * 50))

        draw_button(back_button, "Back", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()


def main_menu(screen, background):
    
    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 50)

    multiplayer_button = pygame.Rect(250, 200, 300, 60)
    start_button = pygame.Rect(250, 300, 300, 60)
    bot_button_b = pygame.Rect(250, 400, 300, 60)
    quit_button = pygame.Rect(250, 500, 300, 60)

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
                    return False, "white"
                elif bot_button_b.collidepoint(mouse_pos):
                    return True, "white"
                elif multiplayer_button.collidepoint(mouse_pos):
                    result = multiplayer_menu(screen, background)
                    if result:
                        return False, result
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
        
        draw_button(multiplayer_button, "Multiplayer", (100, 100, 255), (70, 70, 200))
        draw_button(start_button, "Lokal 2 Player", (100, 100, 255), (70, 70, 200))
        draw_button(bot_button_b, "KI  BEGINNER", (100, 255, 100), (70, 200, 70))
        draw_button(quit_button, "Beenden", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()
