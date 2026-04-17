import pygame
import sys
import threading
from Network.network_thread import start_server, connect_to_server, send_move, listen_for_moves, incoming_moves
from Network.lan_discovery import broadcast_host, listen_for_hosts

network_socket = None

def multiplayer_menu(screen, background):
    font_big = pygame.font.SysFont(None, 100)  # Größerer Titel wie im Hauptmenü
    font = pygame.font.SysFont(None, 50)

    # Buttons zentrieren und größer machen wie im Hauptmenü
    button_width = 400
    button_height = 70
    center_x = screen.get_width() // 2 - button_width // 2
    host_button = pygame.Rect(center_x, 300, button_width, button_height)
    find_button = pygame.Rect(center_x, 400, button_width, button_height)
    back_button = pygame.Rect(center_x, 500, button_width, button_height)

    while True:
        screen.blit(background, (0, 0))
        # Schönerer Overlay mit leichtem Blau wie im Hauptmenü
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 50, 150))  # Dunkleres Blau
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

        def draw_button(rect, text, hover_color, normal_color, shadow_color=(0, 0, 0)):
            # Schatten
            shadow_rect = rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=10)
            
            # Button
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            # Rand
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10)
            
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        # Titel mit Schatten
        title_surf = font_big.render("Multiplayer", True, (255, 255, 255))
        title_shadow = font_big.render("Multiplayer", True, (0, 0, 0))
        title_x = screen.get_width() // 2 - title_surf.get_width() // 2
        title_y = 120
        screen.blit(title_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_surf, (title_x, title_y))
        
        draw_button(host_button, "Host Game", (100, 150, 255), (70, 100, 200))
        draw_button(find_button, "Find Game", (100, 150, 255), (70, 100, 200))
        draw_button(back_button, "Back", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()

def host_game_screen(screen, background):
    font_big = pygame.font.SysFont(None, 100)  # Größerer Titel wie im Hauptmenü
    font = pygame.font.SysFont(None, 50)

    # Button zentrieren und größer machen wie im Hauptmenü
    button_width = 400
    button_height = 70
    center_x = screen.get_width() // 2 - button_width // 2
    back_button = pygame.Rect(center_x, 600, button_width, button_height)

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
        # Schönerer Overlay mit leichtem Blau wie im Hauptmenü
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 50, 150))  # Dunkleres Blau
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

        def draw_button(rect, text, hover_color, normal_color, shadow_color=(0, 0, 0)):
            # Schatten
            shadow_rect = rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=10)
            
            # Button
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            # Rand
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10)
            
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        # Titel mit Schatten
        title_surf = font_big.render("Hosting Game", True, (255, 255, 255))
        title_shadow = font_big.render("Hosting Game", True, (0, 0, 0))
        title_x = screen.get_width() // 2 - title_surf.get_width() // 2
        title_y = 120
        screen.blit(title_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_surf, (title_x, title_y))

        waiting_surf = font.render("Warte auf Spieler...", True, (255, 255, 255))
        screen.blit(waiting_surf, (screen.get_width() // 2 - waiting_surf.get_width() // 2, 300))

        draw_button(back_button, "Back", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()

def find_game_screen(screen, background):
    font_big = pygame.font.SysFont(None, 100)  # Größerer Titel wie im Hauptmenü
    font = pygame.font.SysFont(None, 50)

    # Button zentrieren und größer machen wie im Hauptmenü
    button_width = 400
    button_height = 70
    center_x = screen.get_width() // 2 - button_width // 2
    back_button = pygame.Rect(center_x, 600, button_width, button_height)
    found_hosts = []
    selected_index = 0

    # Start listening thread
    threading.Thread(target=listen_for_hosts, args=(found_hosts,), daemon=True).start()

    while True:
        screen.blit(background, (0, 0))
        # Schönerer Overlay mit leichtem Blau wie im Hauptmenü
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 50, 150))  # Dunkleres Blau
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
                        return {"mode": "client", "socket": sock, "color": "black", "server_ip": host_ip}
                    except Exception as e:
                        print(f"Connection error: {e}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(mouse_pos):
                    return None
                # Check if clicked on a host
                for i, (ip, port) in enumerate(found_hosts):
                    rect = pygame.Rect(center_x, 250 + i * 60, button_width, 50)
                    if rect.collidepoint(mouse_pos):
                        selected_index = i
                        try:
                            sock = connect_to_server(ip, int(port))
                            return {"mode": "client", "socket": sock, "color": "black", "server_ip": ip}
                        except Exception as e:
                            print(f"Connection error: {e}")

        def draw_button(rect, text, hover_color, normal_color, shadow_color=(0, 0, 0)):
            # Schatten
            shadow_rect = rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=10)
            
            # Button
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            # Rand
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10)
            
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        # Titel mit Schatten
        title_surf = font_big.render("Find Game", True, (255, 255, 255))
        title_shadow = font_big.render("Find Game", True, (0, 0, 0))
        title_x = screen.get_width() // 2 - title_surf.get_width() // 2
        title_y = 120
        screen.blit(title_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_surf, (title_x, title_y))

        # Draw found hosts
        for i, (ip, port) in enumerate(found_hosts):
            # Host als Button darstellen
            host_rect = pygame.Rect(center_x, 250 + i * 60, button_width, 50)
            is_selected = i == selected_index
            color = (255, 255, 0) if is_selected else (255, 255, 255)
            
            # Schatten für Host-Buttons
            shadow_rect = host_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=5)
            
            # Host-Button
            pygame.draw.rect(screen, (70, 100, 200) if is_selected else (50, 80, 180), host_rect, border_radius=5)
            pygame.draw.rect(screen, color, host_rect, 2, border_radius=5)
            
            host_surf = font.render(f"{ip}:{port}", True, color)
            screen.blit(host_surf, (
                host_rect.x + (host_rect.width - host_surf.get_width()) // 2,
                host_rect.y + (host_rect.height - host_surf.get_height()) // 2
            ))

        draw_button(back_button, "Back", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()


def main_menu(screen, background):
    
    font_big = pygame.font.SysFont(None, 100)  # Größerer Titel
    font = pygame.font.SysFont(None, 50)

    # Buttons zentrieren und größer machen
    button_width = 400
    button_height = 70
    center_x = screen.get_width() // 2 - button_width // 2
    multiplayer_button = pygame.Rect(center_x, 250, button_width, button_height)
    start_button = pygame.Rect(center_x, 350, button_width, button_height)
    bot_button_b = pygame.Rect(center_x, 450, button_width, button_height)
    bot_button_a = pygame.Rect(center_x, 550, button_width, button_height)
    quit_button = pygame.Rect(center_x, 650, button_width, button_height)

    while True:
        screen.blit(background, (0, 0))
        # Schönerer Overlay mit leichtem Blau
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 50, 150))  # Dunkleres Blau
        screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_pos):
                    return False, None, "white"
                elif bot_button_b.collidepoint(mouse_pos):
                    return True, "beginner", "white"
                elif bot_button_a.collidepoint(mouse_pos):
                    return True, "advanced", "white"
                elif multiplayer_button.collidepoint(mouse_pos):
                    result = multiplayer_menu(screen, background)
                    if result:
                        return False, None, result
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        def draw_button(rect, text, hover_color, normal_color, shadow_color=(0, 0, 0)):
            # Schatten
            shadow_rect = rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=10)
            
            # Button
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            # Rand
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10)
            
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.x + (rect.width - text_surf.get_width()) // 2,
                rect.y + (rect.height - text_surf.get_height()) // 2
            ))

        # Titel mit Schatten
        title_surf = font_big.render("Schachspiel", True, (255, 255, 255))
        title_shadow = font_big.render("Schachspiel", True, (0, 0, 0))
        title_x = screen.get_width() // 2 - title_surf.get_width() // 2
        title_y = 100
        screen.blit(title_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_surf, (title_x, title_y))
        
        draw_button(multiplayer_button, "Multiplayer", (100, 150, 255), (70, 100, 200))
        draw_button(start_button, "Lokal 2 Player", (100, 255, 150), (70, 200, 100))
        draw_button(bot_button_b, "KI Beginner", (255, 200, 100), (200, 150, 70))
        draw_button(bot_button_a, "KI Advanced", (255, 150, 100), (200, 100, 70))
        draw_button(quit_button, "Beenden", (255, 100, 100), (200, 70, 70))

        pygame.display.flip()
