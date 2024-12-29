import pygame
import sys
import subprocess
import os

# Ustawienia okna
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
TAB_WIDTH, TAB_HEIGHT = 150, 50

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLUE = (100, 150, 255)

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Interface Example")
clock = pygame.time.Clock()

# Rysowanie przycisku
def draw_button(x, y, width, height, text):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    font = pygame.font.SysFont("Arial", 24)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

# Rysowanie zakładek
def draw_tab(x, y, width, height, text, selected=False):
    color = BLUE if selected else DARK_GRAY
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.SysFont("Arial", 20)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

# Główna pętla gry
tunning = True
selected_tab = "Tab 1"  # Domyślnie zaznaczona zakładka
while tunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            tunning = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Sprawdzenie kliknięcia na zakładki
            if 10 <= mouse_x <= 10 + TAB_WIDTH:
                if 10 <= mouse_y <= 10 + TAB_HEIGHT:
                    selected_tab = "Tab 1"
                elif 70 <= mouse_y <= 70 + TAB_HEIGHT:
                    selected_tab = "Tab 2"

            # Sprawdzenie kliknięcia na przycisk
            button_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
            button_y = (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2
            if button_x <= mouse_x <= button_x + BUTTON_WIDTH and button_y <= mouse_y <= button_y + BUTTON_HEIGHT:
                if os.path.exists("chess.py"):
                # Uruchom plik jako osobny proces
                    subprocess.run(["python", "chess.py"])

    # Rysowanie elementów
    screen.fill(WHITE)

    # Rysowanie zakładek
    draw_tab(10, 10, TAB_WIDTH, TAB_HEIGHT, "Tab 1", selected=(selected_tab == "Tab 1"))
    draw_tab(10, 70, TAB_WIDTH, TAB_HEIGHT, "Tab 2", selected=(selected_tab == "Tab 2"))

    # Rysowanie przycisku
    button_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
    button_y = (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2
    draw_button(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()