import pygame
import sys
import subprocess
import os



# Ustawienia okna
# SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (149, 165, 166)



class Button(pygame.Rect):
    def __init__(self, x, y, width, height, text=None, color=None, id=None):
        super().__init__(x, y, width, height)
        self.text = text if text else None
        self.color = color if color else None
        self.id = id

    def draw(self, surface, text_color=BLACK, font_type='Arial', font_size=24):
        pygame.draw.rect(surface, self.color, self)

        if self.text:
            font = pygame.font.SysFont(font_type, font_size, bold=True)
            text_surface = font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.center)
            surface.blit(text_surface, text_rect)

    def set_color(self, new_color):
        self.color = new_color

    def set_text(self, new_text):
        self.text = new_text

    def clicked(self, pos):
        return self.collidepoint(pos)

    def __eq__(self, other) -> bool:
        if isinstance(other, Button):
            return self.id == other.id
        return False

    def __str__(self):
        return f"{self.id}"




class MainWindow:
    def __init__(self, size) -> None:
        self.screen_size = size
        self.start_button = self.create_start()
        self.top10_button = self.create_top10()

        self.top10_clicked = False
        self.screen = pygame.display.set_mode(self.screen_size)
        self.game_buttons = self.create_game_buttons()

    def create_start(self):
        screen_width, screen_height = self.screen_size
        x = (screen_width - 200) // 2
        y = (screen_height - 50) // 2
        return Button(x, y, 200, 50, 'START', GRAY)

    def create_top10(self):
        x = self.screen_size[0]//30
        y = self.screen_size[1]//30
        return Button(x, y, 200, 50, 'Top 10', GRAY)

    def bg_image(self, path="background.jpg"):
        bg_image = pygame.image.load(path)
        bg_image = pygame.transform.scale(bg_image, self.screen_size)
        self.screen.blit(bg_image, (0, 0))

    def start_game(self):
        if os.path.exists("chess.py"):
            # Uruchom plik jako osobny proces
            subprocess.run(["python", "chess.py"])

    def change_top10_status(self):
        self.top10_clicked = not self.top10_clicked

    def update_game_buttons(self):
        self.game_buttons = self.create_game_buttons()

    def create_game_buttons(self, path='Top10'):
        game_buttons = []
        all_files = [f for f in os.listdir(path) if f.endswith(".json")]
        width, height = self.calculate_game_button_size()
        y = 3*self.top10_button.y
        for filename in all_files:
            y += 2*self.top10_button.y
            button_name = f'{filename.removesuffix(".json")[:24]}'
            x = self.top10_button.centerx - 3*self.top10_button.x
            button = Button(x, y, width, height, button_name, GRAY)
            game_buttons.append(button)
        return game_buttons

    def calculate_game_button_size(self):
        width, hight = 200, 50
        width = (width + 20)//2
        hight = hight//2
        return width, hight

    def open_saved_games(self, pos):
        for button in self.game_buttons:
            if button.clicked(pos):
                game_file = f'Top10/{button.text}'
                subprocess.run(["python", "open_saved_game.py", game_file])

    def draw_myself(self):
        self.bg_image()
        self.top10_button.draw(self.screen, text_color=WHITE)
        self.start_button.draw(self.screen)
        if self.top10_clicked:
            self.update_game_buttons()
            for button in self.game_buttons:
                button.draw(self.screen, font_size=14)

def main():
    pygame.init()
    window = MainWindow((800, 700))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:

                if window.start_button.clicked(event.pos):
                    window.start_game()
                if window.top10_button.clicked(event.pos):
                    window.change_top10_status()

                window.open_saved_games(event.pos)


        window.draw_myself()
        pygame.display.flip()

    pygame.quit()

# if __name__ == "__main__":
#     main()


# Inicjalizacja Pygame
# pygame.init()
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("SHOGI")
# clock = pygame.time.Clock()

# Załaduj obrazek tła
# background_image = pygame.image.load("background.jpg")

# Skalowanie obrazka do rozmiaru okna (opcjonalne)
# background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

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


# running = True
# top_10_clicked = False
# buttons = []

# # # Główna pętla okna
# if __name__ == '__main__':

#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 # Sprawdzenie kliknięcia na przycisk START
#                 pos = (SCREEN_WIDTH - BUTTON_WIDTH) // 2, (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2

#                 if in_button(event.pos, BUTTON_WIDTH, BUTTON_HEIGHT, pos=pos):
#                     if os.path.exists("chess.py"):
#                         # Uruchom plik jako osobny proces
#                         subprocess.run(["python", "chess.py"])

#                 # Sprawdzenie kliknięcia na przycisk TOP 10
#                 pos = 20, 20
#                 if in_button(event.pos, BUTTON_WIDTH, BUTTON_HEIGHT, pos=pos):
#                     top_10_clicked = not top_10_clicked  # Przełącz stan widoczności przycisku "Any"
#                 for button in buttons:
#                     if button['rect'].collidepoint(event.pos):
#                         game_file = f'Top10/{button["name"]}'
#                         subprocess.run(["python", "open_saved_game.py", game_file])

#         # Rysowanie elementów
#         screen.fill(WHITE)
#         screen.blit(background_image, (0, 0))

#         # Rysowanie przycisków
#         button_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
#         button_y = (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2
#         draw_button(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "START")
#         draw_button(20, 20, BUTTON_WIDTH, BUTTON_HEIGHT, 'TOP 10')

#         # Rysowanie dodatkowego przycisku po kliknięciu "TOP 10"
#         if top_10_clicked:
#             buttons = []  # Lista przycisków (pozycja i nazwa)
#             height = 20 + BUTTON_HEIGHT
#             all_files = [f for f in os.listdir('Top10') if f.endswith(".json")]
#             for filename in all_files:
#                 height += 30
#                 button_name = f'{filename.removesuffix(".json")[:24]}'
#                 buttons.append({'rect': pygame.Rect(20, height, (BUTTON_WIDTH +20)// 2, BUTTON_HEIGHT // 2), 'name': button_name})
#                 draw_button(20, height, (BUTTON_WIDTH + 20) // 2, BUTTON_HEIGHT // 2, button_name, 10)


#         pygame.display.flip()
#         clock.tick(60)

#     pygame.quit()
#     sys.exit()