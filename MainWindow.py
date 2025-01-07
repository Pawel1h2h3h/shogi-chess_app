import pygame
import sys
import subprocess
import os


# Ustawienia okna
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (149, 165, 166)

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SHOGI")
clock = pygame.time.Clock()

# Załaduj obrazek tła
background_image = pygame.image.load("background.jpg")

# Skalowanie obrazka do rozmiaru okna (opcjonalne)
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Funkcja do sprawdzenia, czy kliknięcie jest w przycisku
def in_button(mouse_pos, width, height, pos):
    """
    Returns:
        bool: True gdy przycisk został kliknięty, False gdy warunek nie został spełnony.
    """
    mouse_x, mouse_y = mouse_pos
    button_x, button_y = pos
    return button_x <= mouse_x <= button_x + width and button_y <= mouse_y <= button_y + height

# Rysowanie przycisku
def draw_button(x, y, width, height, text, font_size=24):
    """
    Rysuje przycisk
    """
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    font = pygame.font.SysFont("Arial", font_size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


running = True
top_10_clicked = False
buttons = []

# Główna pętla okna
if __name__ == '__main__':

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Sprawdzenie kliknięcia na przycisk START
                pos = (SCREEN_WIDTH - BUTTON_WIDTH) // 2, (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2

                if in_button(event.pos, BUTTON_WIDTH, BUTTON_HEIGHT, pos=pos):
                    if os.path.exists("chess.py"):
                        # Uruchom plik jako osobny proces
                        subprocess.run(["python", "chess.py"])

                # Sprawdzenie kliknięcia na przycisk TOP 10
                pos = 20, 20
                if in_button(event.pos, BUTTON_WIDTH, BUTTON_HEIGHT, pos=pos):
                    top_10_clicked = not top_10_clicked  # Przełącz stan widoczności przycisku "Any"
                for button in buttons:
                    if button['rect'].collidepoint(event.pos):
                        game_file = f'Top10/{button["name"]}'
                        subprocess.run(["python", "open_saved_game.py", game_file])

        # Rysowanie elementów
        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))

        # Rysowanie przycisków
        button_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
        button_y = (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2
        draw_button(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "START")
        draw_button(20, 20, BUTTON_WIDTH, BUTTON_HEIGHT, 'TOP 10')

        # Rysowanie dodatkowego przycisku po kliknięciu "TOP 10"
        if top_10_clicked:
            buttons = []  # Lista przycisków (pozycja i nazwa)
            height = 20 + BUTTON_HEIGHT
            all_files = [f for f in os.listdir('Top10') if f.endswith(".json")]
            for filename in all_files:
                height += 30
                button_name = f'{filename.removesuffix(".json")[:24]}'
                buttons.append({'rect': pygame.Rect(20, height, (BUTTON_WIDTH +20)// 2, BUTTON_HEIGHT // 2), 'name': button_name})
                draw_button(20, height, (BUTTON_WIDTH + 20) // 2, BUTTON_HEIGHT // 2, button_name, 10)


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()