import pygame
from chess import GameWindow, AnaliseWindow, MainWindow, game_loop, analise_loop


GAME_EVENTS = [pygame.K_n, pygame.K_y, pygame.MOUSEBUTTONDOWN, pygame.K_ESCAPE]

ANALISE_EVENTS = [pygame.MOUSEBUTTONDOWN]

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((12 * 80, 9 * 80))

    icon = pygame.image.load('icon.jpg')
    pygame.display.set_icon(icon)

    # Inicjalizacja okna
    main_window = MainWindow(screen=screen)
    game = False

    # Flagi stanu
    current_window = "main"  # Może być "main", "game" lub 'analise

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_window == "main":
                # Obsługa zdarzeń dla MainWindow
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if main_window.start_button.clicked(event.pos):
                        current_window = "game"
                    elif main_window.top10_button.clicked(event.pos):
                        main_window.change_top10_status()

                    if main_window.top10_clicked:
                        analise = main_window.open_saved_games(event.pos)
                        if analise:
                            current_window = 'analise'

            elif current_window == "game":
                if not game:
                    game = GameWindow(screen)
                if event.type in GAME_EVENTS:
                    current_window, game = game_loop(window=game, event=event)

            elif current_window == 'analise':
                if event.type in ANALISE_EVENTS:
                    current_window = analise_loop(window=analise, event=event)
                    current_window = current_window if current_window else 'analise'

        # Rysowanie aktualnego okna
        if current_window == "main":
            main_window.draw_myself()
        elif current_window == "game" and game:
            game.update_window()
        elif current_window == 'analise':
            analise.update()

        # Aktualizacja ekranu
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()


