import pytest
import pygame
from app import App
from chess import MainWindow, GameWindow, AnaliseWindow


@pytest.fixture
def app_instance():
    """Fixture tworzący instancję klasy App."""
    pygame.init()
    screen = pygame.display.set_mode((960, 720))  # Rozmiar okna
    app = App()
    app.screen = screen  # Przypisanie ekranu Pygame
    return app


def test_initial_state(app_instance):
    """Test sprawdzający początkowy stan klasy App."""
    assert app_instance.current_window == "main"
    assert app_instance.game is False
    assert app_instance.analise is False


def test_operate_main_window_start_game(app_instance):
    """Test obsługi kliknięcia przycisku START w MainWindow."""
    x = app_instance.main_window.start_button.x
    y = app_instance.main_window.start_button.y
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (x+1, y+2)})

    # Ustawienie rzeczywistej pozycji przycisku START
    app_instance.main_window.start_button.x = 350
    app_instance.main_window.start_button.y = 250
    app_instance.main_window.start_button.width = 200
    app_instance.main_window.start_button.height = 50

    app_instance.operate_main_window(mock_event)



def test_update_main_window(app_instance):
    """Test aktualizacji głównego okna."""
    app_instance.current_window = "main"

    app_instance.update()

    # Brak błędów wskazuje, że metoda `draw_myself` została poprawnie wywołana


def test_update_game_window(app_instance):
    """Test aktualizacji okna gry."""
    app_instance.current_window = "game"
    app_instance.game = GameWindow(app_instance.screen)

    app_instance.update()

    # Brak błędów wskazuje, że metoda `update_window` działa poprawnie


def test_update_analise_window(app_instance):
    """Test aktualizacji okna analizy."""
    app_instance.current_window = "analise"
    app_instance.analise = AnaliseWindow(app_instance.screen)  # W przypadku analizy używamy GameWindow

    app_instance.update()

    # Brak błędów wskazuje, że metoda `update` działa poprawnie


@pytest.fixture(autouse=True)
def teardown():
    """Zamyka Pygame po zakończeniu testów."""
    yield
    pygame.quit()