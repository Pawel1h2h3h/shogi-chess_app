import pygame
from chess import GameWindow, MainWindow, game_loop, analise_loop


GAME_EVENTS = [pygame.K_n, pygame.K_y, pygame.MOUSEBUTTONDOWN, pygame.K_ESCAPE]

ANALISE_EVENTS = [pygame.MOUSEBUTTONDOWN]


class App:
    def __init__(self, current_window='main', icon_path='pictures/icon.jpg') -> None:
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((12 * 80, 9 * 80))
        self.icon = pygame.image.load(icon_path)
        pygame.display.set_icon(self.icon)

        # Inicjalizacja okna
        self.main_window = MainWindow(self.screen)
        self.game = False
        self.analise = False

        self.current_window = current_window

    def operate_main_window(self, event):
        if self.current_window == "main":
            pygame.display.set_caption('SHOGI')
            # Obsługa zdarzeń dla MainWindow
            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.main_window.start_button.clicked(event.pos):
                    self.current_window = "game"
                elif self.main_window.top10_button.clicked(event.pos):
                    self.main_window.change_top10_status()

                if self.main_window.top10_clicked:
                    self.analise = self.main_window.open_saved_games(event.pos)
                    if self.analise:
                        self.current_window = 'analise'
                        date = self.analise.game.date
                        pygame.display.set_caption(f'Game {date}')

    def operate_game_window(self, event):
        if self.current_window == "game":
            if not self.game:
                self.game = GameWindow(self.screen)
            if event.type in GAME_EVENTS:
                self.current_window, self.game = game_loop(window=self.game, event=event)

    def operate_analize_window(self, event):
        if self.current_window == 'analise':
            if event.type in ANALISE_EVENTS:
                self.current_window = analise_loop(window=self.analise, event=event)
                self.current_window = self.current_window if self.current_window else 'analise'

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.operate_main_window(event)
                self.operate_game_window(event)
                self.operate_analize_window(event)

            self.update()

    def update(self):
        # Rysowanie aktualnego okna
        if self.current_window == "main":
            self.main_window.draw_myself()
        elif self.current_window == "game" and self.game:
            self.game.update_window()
        elif self.current_window == 'analise':
            self.analise.update()

        # Aktualizacja ekranu
        pygame.display.flip()
        self.clock.tick(60)




