import pytest
from chess import GameWindow
import pygame
import json
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from chess import GameWindow, Game, LoadGameError, Button
from shogi import Move, Board


# Ustawienia planszy
CELL_SIZE = 80
SCREEN_WIDTH, SCREEN_HEIGHT = 12*CELL_SIZE, 9*CELL_SIZE
BOARD_SIZE = 9


# Kolory planszy
LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
LINE_COLOR = (0, 0, 0)

# Kolory marginesu
GREY = (200, 200, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (73, 50, 103)
BEIGE = (255, 240, 219)
GRAY = (149, 165, 166)
BLUE = (137, 204, 240)

# Ustawienie marginesu
RECT_POS = CELL_SIZE*9 + 20, 10
RECT_SIZE = 2* CELL_SIZE - 40, 40
SAVE_POS = CELL_SIZE*9 +10, CELL_SIZE*8 + 10
SAVE_SIZE = RECT_SIZE

# Pozycja i rozmiar przycisku "LOAD"
LOAD_POS = SAVE_POS[0], SAVE_POS[1] - SAVE_SIZE[1] - 10

# MARGINES - wymiary
MARGINES_X = BOARD_SIZE * CELL_SIZE  # Początek marginesu w osi X
MARGINES_X1 = MARGINES_X + 10 * CELL_SIZE  # Koniec marginesu w osi X
ROW_SIZE = 8 * CELL_SIZE / 14  # Wysokość każdego wiersza marginesu
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


@pytest.fixture(scope="module")
def pygame_setup():
    """Inicjalizuje Pygame przed uruchomieniem testów."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def game_window(pygame_setup):
    """Fixture tworzący instancję GameWindow."""
    window = GameWindow(screen)
    window.board.move_stack = [
        Move(from_square=1, to_square=2, promotion=False, drop_piece_type=None),
        Move(from_square=3, to_square=4, promotion=True, drop_piece_type=None)
    ]
    return window


def test_initial_state(game_window):
    """Testuje początkowy stan obiektu GameWindow."""
    assert game_window.board_size == 9
    assert len(game_window.squares) == 81  # 9x9
    assert game_window.selected_piece is None
    assert game_window.legal_moves is False
    assert game_window.game_over is False
    assert game_window.start_time is None


def test_create_board(game_window):
    """Testuje, czy plansza została poprawnie utworzona."""
    assert len(game_window.squares) == 81  # 9x9
    # Sprawdzenie pierwszego pola planszy
    first_square = game_window.squares[0]
    assert first_square.x == 0
    assert first_square.y == 0
    assert first_square.width == CELL_SIZE
    assert first_square.height == CELL_SIZE


def test_create_board_colors(game_window):
    for square in game_window.squares:
        if square.id % 2 == 0:
            assert square.color == LIGHT_COLOR
        else:
            assert square.color == DARK_COLOR



def test_draw_board_lines(game_window):
    """Testuje rysowanie linii na planszy."""
    # Mockowanie metody draw.line
    with pytest.MonkeyPatch.context() as monkeypatch:
        draw_calls = []

        def mock_draw_line(surface, color, start_pos, end_pos, width):
            draw_calls.append((color, start_pos, end_pos, width))

        monkeypatch.setattr(pygame.draw, "line", mock_draw_line)
        game_window.draw_board_lines()

        # Powinno być 10 poziomych i 10 pionowych linii
        assert len(draw_calls) == 20




def test_load_game_file_not_found(game_window):
    """Test wczytywania gry, gdy plik nie istnieje."""
    with patch("pathlib.Path.open", side_effect=FileNotFoundError):
        with pytest.raises(LoadGameError, match="Nie znaleziono pliku"):
            game_window.load_game("nonexistent.json")


def test_load_game_invalid_json(game_window):
    """Test wczytywania gry z niepoprawnym JSON-em."""
    with patch("pathlib.Path.open", mock_open(read_data="INVALID JSON")):
        with pytest.raises(LoadGameError):
            game_window.load_game("invalid.json")


def test_load_game_missing_keys(game_window):
    """Test wczytywania gry z brakującymi kluczami w JSON."""
    game_data = {
        "date": "2025-01-12 12:00:00",
        "time": 120
        # Brakuje klucza "moves"
    }

    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(game_data))):
        with pytest.raises(LoadGameError):
            game_window.load_game("game.json")


def test_create_margin_buttons(game_window):
    """Testuje poprawne tworzenie przycisków marginesu."""
    game_window.create_margin_buttons()

    # Sprawdzenie liczby przycisków
    assert len(game_window.margin_buttons) == 2

    # Sprawdzenie właściwości przycisków
    undo_button, redo_button = game_window.margin_buttons
    back_button = game_window.back_button

    assert isinstance(undo_button, Button)
    assert undo_button.x == RECT_POS[0]
    assert undo_button.y == RECT_POS[1]
    assert undo_button.width == RECT_SIZE[0] // 2
    assert undo_button.height == RECT_SIZE[1]

    assert isinstance(redo_button, Button)
    assert redo_button.x == RECT_POS[0] + RECT_SIZE[0] // 2
    assert redo_button.y == RECT_POS[1]
    assert redo_button.width == RECT_SIZE[0] // 2
    assert redo_button.height == RECT_SIZE[1]

    assert isinstance(back_button, Button)
    assert back_button.text == "MENU"
    assert back_button.x == RECT_POS[0] + 7 * RECT_SIZE[0] // 6
    assert back_button.y == RECT_POS[1]
    assert back_button.width == RECT_SIZE[0] // 2
    assert back_button.height == RECT_SIZE[1]


def test_rename_files(game_window):
    """Testuje poprawne działanie funkcji rename_files."""
    mock_files = [Path(f"game_{i}.json") for i in range(5)]
    with patch("pathlib.Path.iterdir", return_value=mock_files):
        with patch("pathlib.Path.mkdir") as mocked_mkdir:
            with patch("pathlib.Path.rename") as mocked_rename:
                # Mockowanie metod prywatnych
                game_window._normalize_file_names = MagicMock()
                game_window._load_and_sort_games = MagicMock(return_value=[
                    MagicMock(get_filename=lambda: f"game_{i}.json", time=120 - i) for i in range(5)
                ])
                game_window._assign_top_filenames = MagicMock()

                game_window.rename_files()

                # Sprawdzenie, czy funkcje były wywołane
                mocked_mkdir.assert_any_call(parents=True, exist_ok=True)
                game_window._normalize_file_names.assert_called_once()
                game_window._load_and_sort_games.assert_called_once()
                game_window._assign_top_filenames.assert_called_once()

import pytest
from unittest.mock import MagicMock
from chess import AnaliseWindow, Game
import shogi


@pytest.fixture
def mock_analise_window():
    """Fixture tworzący instancję AnaliseWindow z mockowanym ekranem i grą."""
    window = AnaliseWindow(screen)
    window.game = Game(
        date="2025-01-12 12:00:00",
        time=120,
        moves=[
            shogi.Move.from_usi("7g7f"),  # Przykładowy ruch
            shogi.Move.from_usi("3c3d"),  # Przykładowy ruch przeciwnika
        ]
    )
    return window


def test_initial_state(mock_analise_window):
    """Testuje początkowy stan klasy AnaliseWindow."""
    assert mock_analise_window.done_moves == []
    assert mock_analise_window.backed_moves == []
    assert isinstance(mock_analise_window.board, shogi.Board)
    assert mock_analise_window.game is not None
    assert len(mock_analise_window.game.moves) == 2


def test_make_move(mock_analise_window):
    """Testuje wykonanie ruchu."""
    # Przed wykonaniem ruchu
    assert len(mock_analise_window.game.moves) == 2
    assert len(mock_analise_window.done_moves) == 0

    mock_analise_window.make_move()

    # Po wykonaniu ruchu
    assert len(mock_analise_window.game.moves) == 1  # Jeden ruch pozostał
    assert len(mock_analise_window.done_moves) == 1  # Jeden ruch w done_moves
    assert mock_analise_window.done_moves[-1].usi() == "7g7f"  # Ostatni wykonany ruch


def test_make_move_no_moves(mock_analise_window):
    """Testuje wykonanie ruchu, gdy lista ruchów jest pusta."""
    mock_analise_window.game.moves.clear()  # Usuń wszystkie ruchy
    assert len(mock_analise_window.game.moves) == 0

    mock_analise_window.make_move()

    # Nie powinno być zmian
    assert len(mock_analise_window.done_moves) == 0


def test_back_move(mock_analise_window):
    """Testuje cofnięcie ruchu."""
    # Najpierw wykonaj ruch
    mock_analise_window.make_move()

    # Przed cofnięciem ruchu
    assert len(mock_analise_window.done_moves) == 1
    assert len(mock_analise_window.game.moves) == 1

    mock_analise_window.back_move()

    # Po cofnięciu ruchu
    assert len(mock_analise_window.done_moves) == 0
    assert len(mock_analise_window.game.moves) == 2  # Ruch wrócił na początek
    assert mock_analise_window.game.moves[0].usi() == "7g7f"  # Pierwszy ruch przywrócony


def test_back_move_no_moves(mock_analise_window):
    """Testuje cofnięcie ruchu, gdy lista wykonanych ruchów jest pusta."""
    assert len(mock_analise_window.done_moves) == 0

    mock_analise_window.back_move()

    # Nie powinno być zmian
    assert len(mock_analise_window.game.moves) == 2  # Ruchy pozostały bez zmian