# Ustawienia planszy
import pygame
from pathlib import Path
import shogi
import time
import json
import os
import datetime


class SaveGameError(Exception):
    def __init__(self, error) -> None:
        super().__init__(f"Cannot save game: {error}")

class ModerateGameNamesError(Exception):
    def __init__(self, error) -> None:
        super().__init__(f"Cannot moderate Top10 fieles: {error}")

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


class GameWindow:
    def __init__(self, screen) -> None:
        self.squares = []
        self.board_size = 9
        self.screen = screen
        self.board = shogi.Board()

        self.king_square = None
        self.selected_piece = None
        self.legal_moves = False
        self.selected_square = None
        self.promotion = False
        self.undone_moves = []
        self.captured_pieces = {}
        self.margin_captured_buttons = []
        self.margin_buttons = []
        self.selected_piece_color = None
        self.back_button = None
        self.selected_captured_button = None

        self.message = None

        self.add_mode = False
        self.game_over = False
        self.start_time = None
        self.end_time = None
        self.create_board()
        self.create_margines()
        self.create_margin_buttons()

    def set_screen(self, new_screen):
        self.screen = new_screen

    def draw_board_lines(self):
        for i in range(self.board_size + 1):
            pygame.draw.line(self.screen, LINE_COLOR, (0, i * CELL_SIZE), (9*CELL_SIZE, i * CELL_SIZE), 1)
            pygame.draw.line(self.screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_HEIGHT), 1)

    def create_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                square = row * BOARD_SIZE + col
                button = Button(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE, color=color, id=square)
                self.squares.append(button)
        self.draw_board_lines()

    def update_board(self):
        for square in self.squares:
            # Resetuj kolor pola do domyślnego
            default_color = LIGHT_COLOR if (square.id // self.board_size + square.id % self.board_size) % 2 == 0 else DARK_COLOR
            square.set_color(default_color)

            # Podświetlenie pola króla w szachu
            if square == self.king_square:
                color = (255, 102, 102)  # Lekki czerwony
                square.set_color(color)

            # Podświetlenie legalnych pól, jeśli są ustawione
            if self.legal_moves and square in self.legal_moves:
                color = (173, 216, 230)  # Lekki błękit
                square.set_color(color)

            # Rysowanie pola (bez tekstu)
            if not square.text:
                square.draw(self.screen)

        # Rysowanie linii siatki
        self.draw_board_lines()

    def get_king_square_in_check(self):
        """
        Zwraca pole króla, jeśli jest w szachu, w przeciwnym razie None.
        """
        king_square = self.board.king_squares[self.board.turn]  # Znajdź pole króla aktualnego gracza
        if self.board.is_attacked_by(self.board.turn ^ 1, king_square):  # Sprawdź, czy król jest atakowany
            for square in self.squares:
                if square.id == king_square:
                    king_square = square
            return king_square
        return None

    def draw_pieces(self):
        """
        Rysuje figury na planszy i resetuje pola bez figur.
        """
        for square in self.squares:
            # Reset tekstu na polach
            square.set_text(None)

            # Pobierz figurę z planszy na odpowiednim polu
            piece = self.board.piece_at(square.id)
            if piece:
                # Ustaw kolor tekstu w zależności od koloru figury
                text_color = BLACK if piece.color == shogi.BLACK else WHITE
                symbol = piece.symbol()  # Symbol figury
                square.set_text(symbol)

                # Rysowanie pola z odpowiednim kolorem tekstu
                square.draw(self.screen, font_size=CELL_SIZE // 2, text_color=text_color)
            else:
                # Rysowanie pustego pola
                square.draw(self.screen, BLACK)

    def get_legal_moves(self, square):
        """
        Zwraca listę pól, na które wybrana figura może się ruszyć.
        """
        square = square.id
        moves = list(self.board.legal_moves)  # Wszystkie możliwe ruchy
        legal_squares_ids = [
            move.to_square for move in moves if move.from_square == square
        ]

        legal_squares = [square for square in self.squares if square.id in legal_squares_ids]
        self.legal_moves = legal_squares
        return legal_squares

    def clicked(self, pos):
        x, y = pos
        return y < 9 * CELL_SIZE and x < 9 * CELL_SIZE

    def clicked_square(self, pos):
        for square in self.squares:
            if square.clicked(pos):
                return square

    def find_piece(self, square):
        """Znajduje figurę o na odpowiednim polu"""
        if square.text:
            piece = self.board.piece_at(square.id)
            self.selected_piece = piece
        else:
            self.selected_piece = None

    def make_move(self, from_square, to_square):
        move = shogi.Move(from_square.id, to_square.id, self.promotion)
        if move in self.board.legal_moves:
            self.board.push(move)

    def set_promotion(self, value):
        self.promotion = value

    def is_in_promotion_zone(self, square, color):
        """
        Sprawdza, czy pole znajduje się w strefie promocji.
        """
        square = square.id
        if color == shogi.BLACK:
            return square // BOARD_SIZE in [0, 1, 2]  # Trzy ostatnie rzędy dla czarnych
        elif color == shogi.WHITE:
            return square // BOARD_SIZE in [6, 7, 8]  # Trzy ostatnie rzędy dla białych
        return False

    def ask_for_promotion_gui(self):
        """
        Wyświetla okno dialogowe z pytaniem o promocję.
        """
        font = pygame.font.SysFont("Arial", 24)
        question = font.render("Promote piece? (Y/N)", True, (25, 255, 255))
        self.screen.blit(question, (SCREEN_WIDTH // 2 - question.get_width() // 2, SCREEN_HEIGHT // 2 - question.get_height() // 2))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        return True
                    elif event.key == pygame.K_n:
                        return False

    def draw_margines(self):
        """
        Rysuje linie marginesu po prawej stronie planszy shogi z podziałem na rzędy.
        """

        font = pygame.font.SysFont("Arial", 14, bold=True)
        text = font.render('↓Captured pieces↓', True, BLACK)
        self.screen.blit(text, (MARGINES_X + 18, CELL_SIZE - 20))

        # Górna i dolna linia marginesu
        pygame.draw.line(self.screen, LINE_COLOR, (MARGINES_X, CELL_SIZE), (MARGINES_X1, CELL_SIZE))
        pygame.draw.line(self.screen, LINE_COLOR, (MARGINES_X, 14 * CELL_SIZE), (MARGINES_X1, 14 * CELL_SIZE))

        # Linie podziału na wiersze
        for button in self.margin_captured_buttons:
            pygame.draw.line(self.screen, LINE_COLOR, (MARGINES_X, CELL_SIZE + button.id * ROW_SIZE), (MARGINES_X1, CELL_SIZE + button.id * ROW_SIZE))



            # Wyróżnij środkową linię
            if button.id == 7:
                pygame.draw.line(self.screen, BLACK, (MARGINES_X, CELL_SIZE + button.id * ROW_SIZE), (MARGINES_X1, CELL_SIZE + button.id * ROW_SIZE), 4)


    def draw_margin_buttons(self):

        x, y = self.margin_buttons[0].x, self.margin_buttons[0].y
        width, height = RECT_SIZE


        for button in self.margin_buttons:
            if self.selected_captured_button:
                if self.add_mode:
                    self.selected_captured_button.set_color(GREY)
                else:
                    self.selected_captured_button.set_color(None)
            button.draw(self.screen)
            pygame.draw.rect(self.screen, BLACK, button, width=2)

        pygame.draw.rect(self.screen, BLACK, self.back_button, width=2)
        self.back_button.draw(self.screen, font_size=16)

        # Rysowanie trójkąta "cofnij"
        left_triangle = [
            (x + 10, y + height // 2),
            (x + width // 4, y + 10),
            (x + width // 4, y + height - 10),
        ]
        pygame.draw.polygon(self.screen, BLACK, left_triangle)

        # Rysowanie trójkąta "do przodu"
        right_triangle = [
            (x + width - 10, y + height // 2),
            (x + 3 * width // 4, y + 10),
            (x + 3 * width // 4, y + height - 10),
        ]
        pygame.draw.polygon(self.screen, BLACK, right_triangle)

    def create_margin_buttons(self):
        """
        Tworzy przciski przewijania ruchów
        """
        x, y = RECT_POS
        width, height = RECT_SIZE

        undo_button = Button(x=x, y=y, width=width//2, height=height)
        redo_button = Button(x=(x+width//2), y=y, width=width//2, height=height)

        self.back_button = Button(x=(x + 7 * width//6), y=y, width=width//2, height=height, text='MENU')

        self.margin_buttons = undo_button, redo_button


    def create_margines(self):
        x = self.board_size * CELL_SIZE
        y = CELL_SIZE

        width = SCREEN_WIDTH - self.board_size * CELL_SIZE
        height = ROW_SIZE
        id = 0
        for i in range(1, 15):
            margin_pole = Button(x, y, width, height=height, id=id)
            y += ROW_SIZE
            id += 1
            self.margin_captured_buttons.append(margin_pole)


    def set_message(self, message=None, font_size=48, color=WHITE, timex=3000):
        """
        Wyświetla komunikat.
        """
        self.message = message
        if self.message:
            font = pygame.font.SysFont("Arial", font_size, bold=True)
            text_surface = font.render(message, True, color)  # Biały tekst
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        return text_surface, text_rect


    def undo_last_move(self):
        """
        Cofa ostatni ruch na planszy i zapisuje go do listy cofniętych ruchów.

        :param undone_moves: Lista cofniętych ruchów
        :param selected_piece: Wybrana figura (resetuje po cofnięciu ruchu)
        :param selected_square: Wybrane pole (resetuje po cofnięciu ruchu)
        :return: Zaktualizowane zmienne gry
        """
        if self.board.move_stack:
            move = self.board.pop()  # Cofnij ostatni ruch
            self.undone_moves.append(move)  # Zapisz cofnięty ruch
        else:
            self.set_message("No moves to undo!", timex=1000)

        self.king_square = self.get_king_square_in_check()
        self.selected_piece = None
        self.selected_square = None

    def redo_last_move(self):
        """
        Przywraca ostatni cofnięty ruch.

        :param undone_moves: Lista cofniętych ruchów
        :param selected_piece: Wybrana figura (resetuje po przywróceniu ruchu)
        :param selected_square: Wybrane pole (resetuje po przywróceniu ruchu)
        :return: Zaktualizowane zmienne gry
        """
        if self.undone_moves:
            move = self.undone_moves.pop()  # Pobierz ostatni cofnięty ruch
            self.board.push(move)  # Przywróć ruch na planszy
        else:
            self.set_message('No moves to redo', timex=1000)

        self.selected_piece = None
        self.selected_square = None
        self.king_square = self.get_king_square_in_check()


    def draw_captured_pieces(self):
        """
        Rysuje zbite figury (czarnych lub białych) wraz z ich liczbą na marginesie.
        """
        # Dane graczy
        players = [
            {"color": shogi.BLACK, "buttons_offset": 7, "text_color": BLACK},
            {"color": shogi.WHITE, "buttons_offset": 0, "text_color": WHITE},
        ]

        # Rysowanie dla każdego gracza
        for player in players:
            pieces = self.convert_captured_to_symbols(self.get_captured(player["color"]))
            if pieces:
                for i, (symbol, count) in enumerate(pieces.items()):
                    button_id = i + player["buttons_offset"]
                    for button in self.margin_captured_buttons:
                        if button.id == button_id:
                            # button.set_color(GREY)
                            button.set_text(f'{symbol} x {count}')
                            button.draw(self.screen, text_color=player["text_color"])


    def get_captured(self, color):
        """
        Zwraca zbite figury.

        Returns:
            dict: Słownik z typami figur i ich liczbą.
        """
        return self.board.pieces_in_hand[color]


    def convert_captured_to_symbols(self, captured_dict):
        """
        Konwertuje słownik zbitych figur na listę symboli.

        Args:
            captured_dict (dict): Słownik z typami figur i ich liczbą.

        Returns:
            dict: Słownik z symbolami figur jako kluczami i ich liczbą jako wartościami.
        """
        self.captured_pieces = {shogi.PIECE_SYMBOLS[piece]: count for piece, count in captured_dict.items()}
        return self.captured_pieces

    def place_piece_on_board(self):
        """
        Dostawia figurę z marginesu na planszę.

        Args:
            color: Kolor gracza (shogi.BLACK lub shogi.WHITE).

        Returns:
            bool: True, jeśli figura została pomyślnie dostawiona, inaczej False.
        """

        # Sprawdź, czy wybrane pole jest puste

        if self.board.piece_at(self.selected_square.id) is not None:
            return False

        # Sprawdź, czy gracz ma daną figurę w marginesie
        if not self.board.has_piece_in_hand(self.selected_piece, self.selected_piece_color):
            return False

        # Wykonaj ruch dostawienia figury na planszę
        move = shogi.Move(from_square=None, to_square=self.selected_square.id, promotion=False, drop_piece_type=self.selected_piece)
        if self.board.is_legal(move):
            self.board.push(move)
            return True
        else:
            self.set_message("illegal move - try something else")
            return False

    def calculate_time(self):
        if not self.game_over:
            # Obliczanie czasu gry
            if self.start_time is not None:
                if self.end_time is None:
                    elapsed_time = time.time() - self.start_time  # Gra w toku
                else:
                    elapsed_time = self.end_time
            else:
                elapsed_time = 0  # Wyświetla 00:00 przed pierwszym ruchem
            self.elapsed_time = elapsed_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            pygame.display.set_caption(f'SHOGI-GAME {minutes:02}:{seconds:02}')
        else:
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            pygame.display.set_caption(f'SHOGI-GAME {minutes:02}:{seconds:02}')

    def if_game_over(self):
        self.game_over = True
        if self.board.is_checkmate():
            if self.board.turn == shogi.WHITE:
                self.set_message('BLACK WON!', color=BLACK, timex=3000)
            else:
                self.set_message('WHITE WON!', color=WHITE, timex=3000)
        elif self.board.is_fourfold_repetition():
            self.set_message('Stalemate!', color=BLACK, timex=3000)
        if self.board.is_stalemate():
            self.set_message("Stalemate!", color=BLACK, time=3000)
        self.save_game()
        self.rename_files()
        self.get_message()

    def choose_piece_drop(self, button):
        symbol = button.text[:-4]
        # color = shogi.BLACK if button.id > 6 else shogi.WHITE
        self.selected_piece = shogi.Piece.from_symbol(symbol).piece_type
        self.selected_piece_color = shogi.BLACK if button.text_color == BLACK else shogi.WHITE
        self.add_mode = True


    def bg_image(self, path="pictures/gamewindow_image.jpg"):
        bg_image = pygame.image.load(path)
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(bg_image, (9*CELL_SIZE, 0))

    def update_window(self):
        self.screen.fill((149, 165, 166))
        self.bg_image()
        self.draw_margines()
        self.draw_captured_pieces()
        self.draw_margin_buttons()
        self.draw_pieces()
        self.update_board()
        self.calculate_time()
        self.get_message()


    def save_game(self, directory='Top10/'):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "date": date_time,
            "time": int(self.elapsed_time),
            "moves": [
                {
                    "from": move.from_square,
                    "to": move.to_square,
                    "promo": move.promotion,
                    "dropped_type": move.drop_piece_type
                } for move in self.board.move_stack
            ]
        }

        file_path = directory / f'game_{date_time.replace(":", "-")}.json'
        with file_path.open("w") as file:
            json.dump(data, file, indent=4)

    def load_game(self, path):
        """
        Wczytuje partię z pliku JSON.

        :param path: Ścieżka do pliku z zapisem w formacie JSON.
        """
        try:
            # Użycie Path do obsługi ścieżek
            file_path = Path(path)

            if not file_path.exists():
                raise FileNotFoundError(f"Plik '{path}' nie istnieje.")

            with file_path.open("r") as fp:
                # Wczytaj dane z pliku JSON
                data = json.load(fp)

            # Walidacja wymaganych kluczy w danych
            required_keys = ["date", "time", "moves"]
            for key in required_keys:
                if key not in data:
                    raise LoadGameError(f"Brak wymaganych danych: {key}")

            # Pobierz czas gry i datę
            game_time = data["time"]
            date = data["date"]

            # Pobierz listę ruchów
            moves = [
                shogi.Move(
                    from_square=move.get("from"),
                    to_square=move.get("to"),
                    promotion=move.get("promo"),
                    drop_piece_type=move.get("dropped_type")
                ) for move in data["moves"]
            ]

            # Utwórz obiekt gry
            self.game = Game(date, game_time, moves)

        except FileNotFoundError as e:
            raise LoadGameError(f"Nie znaleziono pliku: {e}")
        except json.JSONDecodeError as e:
            raise LoadGameError(f"Błąd dekodowania JSON: {e}")
        except KeyError as e:
            raise LoadGameError(f"Brak klucza w danych JSON: {e}")
        except Exception as e:
            raise LoadGameError(f"Nieoczekiwany błąd: {e}")


    def rename_files(self, dir='Top10', history_dir='History', top_limit=10):
        """
        Zmienia nazwy plików w katalogu 'Top10' i przenosi nadmiarowe do katalogu 'History'.
        :param dir: Katalog z zapisanymi grami.
        :param history_dir: Katalog na pliki przeniesione do historii.
        :param top_limit: Maksymalna liczba najlepszych gier w katalogu.
        """
        dir_path = Path(dir)
        history_path = Path(history_dir)

        # Upewnij się, że katalogi istnieją
        dir_path.mkdir(parents=True, exist_ok=True)
        history_path.mkdir(parents=True, exist_ok=True)

        # Przebuduj nazwy plików na numerowane
        self._normalize_file_names(dir_path)

        # Wczytaj gry i sortuj po czasie
        games = self._load_and_sort_games(dir_path)

        # Przypisz nowe nazwy do gier
        self._assign_top_filenames(games, dir_path, history_path, top_limit)

    def _normalize_file_names(self, dir_path):
        """
        Zmienia nazwy plików w katalogu na numerowane (0.json, 1.json, ...).
        """
        all_files = sorted([f for f in dir_path.iterdir() if f.suffix == ".json"])
        for count, file in enumerate(all_files):
            file.rename(dir_path / f"{count}.json")

    def _load_and_sort_games(self, dir_path):
        """
        Wczytuje gry z plików JSON w katalogu i sortuje je po czasie gry (malejąco).
        :return: Lista posortowanych gier.
        """
        games = []
        for file in dir_path.iterdir():
            if file.suffix == ".json":
                self.load_game(file)  # Wczytaj grę
                self.game.set_filename(file.name)  # Ustaw bieżącą nazwę pliku w obiekcie gry
                games.append(self.game)
        return sorted(games, key=lambda game: game.time, reverse=True)

    def _assign_top_filenames(self, games, dir_path, history_path, top_limit):
        """
        Przypisuje nowe nazwy plikom na podstawie rankingu i przenosi nadmiarowe pliki do historii.
        """
        for n, game in enumerate(games, start=1):
            old_filename = dir_path / game.get_filename()
            if n <= top_limit:
                # Nazwij pliki jako TOP 1, TOP 2, ...
                new_filename = dir_path / f"TOP {n}.json"
            else:
                # Przenieś nadmiarowe pliki do katalogu History
                history_index = len(list(history_path.glob("*.json"))) + 1
                new_filename = history_path / f"game{history_index}.json"
            game.set_filename(new_filename.name)
            old_filename.rename(new_filename)

    def get_message(self):
        if self.message:
            text_surface, text_rect = self.set_message(self.message)
            # Rysowanie komunikatu na ekranie
            self.screen.blit(text_surface, text_rect)
        if self.board.is_game_over():
            pygame.display.flip()
            pygame.time.wait(3000)




class LoadGameError(Exception):
    def __init__(self, error) -> None:
        super().__init__(f'Cannot load the game{error}')


class Game:
    def __init__(self, date, time, moves=None) -> None:
        self.moves = moves if moves else []
        self.date = date
        self.time = time
        self.filename = None

    def set_filename(self, new_filename):
        self.filename = new_filename

    def get_filename(self):
        return self.filename


class AnaliseWindow(GameWindow):
    def __init__(self, screen) -> None:
        super().__init__(screen)
        self.done_moves = []
        self.backed_moves = []
        self.board = shogi.Board()
        self.game = None

    def make_move(self):
        """
        Wykonuje kolejny ruch z listy.
        """
        if self.game.moves:
            move = self.game.moves.pop(0)  # Pobiera pierwszy ruch
            self.board.push(move)  # Wykonuje ruch na planszy
            self.done_moves.append(move)  # Dodaje ruch do listy
        else:
            pass

    def back_move(self):
        """
        Cofnięcie ostatniego ruchu.
        """
        if self.done_moves:
            move = self.done_moves.pop()  # Pobiera ostatni ruch
            self.board.pop()  # Cofnięcie ruchu na planszy
            self.game.moves.insert(0, move)  # Dodaje cofnięty ruch na początek
        else:
            pass


    def update(self):
        self.screen.fill((149, 165, 166))
        self.bg_image()
        self.draw_margines()
        self.draw_captured_pieces()
        self.draw_margin_buttons()
        self.draw_pieces()
        self.update_board()


class Button(pygame.Rect):
    def __init__(self, x, y, width, height, text=None, color=None, id=None):
        super().__init__(x, y, width, height)
        self.text = text if text else None
        self.color = color if color else None
        self.id = id
        self.text_color = None
        self._pressed = False

    def draw(self, surface, text_color=BLACK, font_type='Arial', font_size=24):
        self.text_color = text_color
        if self.color:
            pygame.draw.rect(surface, self.color, self)
        else:
            pygame.draw.rect(surface, BLACK, self, width=2)

        if self.text:
            font = pygame.font.SysFont(font_type, font_size, bold=True)
            text_surface = font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.center)
            surface.blit(text_surface, text_rect)

    def draw_date(self, surface, date, text_color=BLACK, font_size=24):
        text_pos = self.bottomright
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        text_surface = font.render(date, True, text_color)
        text_rect = text_surface.get_rect(center=text_pos)
        surface.blit(text_surface, text_rect)


    def set_color(self, new_color):
        self.color = new_color

    def set_text(self, new_text):
        self.text = new_text

    def clicked(self, pos):
        return self.collidepoint(pos)

    def is_pressed(self):
        return self._pressed

    def set_press(self, value):
        self._pressed = value

    def __eq__(self, other) -> bool:
        if isinstance(other, Button):
            return self.id == other.id
        return False

    def __str__(self):
        return f"{self.id} {self.text}"



class MainWindow:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.start_button = self.create_start()
        self.top10_button = self.create_top10()

        self.top10_clicked = False
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

    def bg_image(self, path="pictures/background.jpg"):
        bg_image = pygame.image.load(path)
        bg_image = pygame.transform.scale(bg_image, self.screen_size)
        self.screen.blit(bg_image, (0, 0))

    def start_game(self):
        if os.path.exists("chess.py"):
            # Uruchom plik jako osobny proces
            # subprocess.run(["python", "chess.py"])
            pass

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
            button_name = f'{filename.removesuffix(".json")}'
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
        analise = None
        for button in self.game_buttons:
            if button.clicked(pos):
                path = f'Top10/{button.text}.json'
                analise = AnaliseWindow(self.screen)
                analise.load_game(path)
        return analise



    def draw_myself(self):
        self.bg_image()
        self.top10_button.draw(self.screen, text_color=WHITE)
        self.start_button.draw(self.screen)
        if self.top10_clicked:
            self.update_game_buttons()
            for button in self.game_buttons:
                button.draw(self.screen, font_size=14)


def analise_loop(window, event):
    if window.margin_buttons[0].clicked(event.pos):
        window.back_move()
    elif window.margin_buttons[1].clicked(event.pos):
        window.make_move()
    elif window.back_button.clicked(event.pos):
        return 'main'


def game_loop(
        window: GameWindow,
        event
            ) -> tuple:

    window.message = None

    if window.back_button.clicked(event.pos):
        return 'main', False

    if not window.game_over:
        if not window.add_mode:
            square = window.clicked_square(event.pos)

            if window.selected_piece is None:
                # Spróbuj znaleźć figurę na klikniętym polu
                if square:
                    window.find_piece(square)
                    if window.selected_piece:
                        # Zaznacz figurę i podświetl legalne ruchy
                        window.selected_square = square
                        window.get_legal_moves(square)
                    else:
                        # Reset podświetlenia, jeśli kliknięto puste pole
                        window.selected_square = None
                        window.legal_moves = False
            else:
                # Kliknięcie na jedno z podświetlonych pól
                if square in window.legal_moves:
                    # Sprawdź, czy wymagana jest promocja
                    window.promotion = False
                    if window.is_in_promotion_zone(square, window.selected_piece.color) and not window.selected_piece.is_promoted() and window.selected_piece.piece_type not in [shogi.KING, shogi.GOLD]:
                        window.promotion = window.ask_for_promotion_gui()

                    # Wykonaj ruch
                    window.make_move(window.selected_square, square)

                    if not window.start_time:
                        window.start_time = time.time()

                    # Sprawdź czy król jest atakowany
                    window.king_square = window.get_king_square_in_check()

                    window.undone_moves.clear()

                    # Wyłącz podświetlenie po ruchu
                    window.selected_piece = None
                    window.selected_square = None
                    window.legal_moves = False
                else:
                    # Reset, jeśli kliknięto pole spoza legalnych ruchów
                    window.selected_piece = None
                    window.selected_square = None
                    window.legal_moves = False
        else:
            window.selected_square = window.clicked_square(event.pos)
            if window.selected_square in window.squares:
                window.place_piece_on_board()
                window.king_square = window.get_king_square_in_check()

                window.add_mode = False
                window.selected_piece = None
                window.selected_square = None
                window.selected_piece_color = None
            else:

                window.add_mode = False
                window.selected_piece = None
                window.selected_square = None
                window.selected_piece_color = None

        for button in window.margin_captured_buttons:
            if button.clicked(event.pos):
                if button.text:
                    window.choose_piece_drop(button)
                    window.selected_captured_button = button
                else:
                    window.set_message('No piece to drop', font_size=24)


        # Obsługa przycisków undo, redo
        if window.margin_buttons[0].clicked(event.pos):
            window.undo_last_move()
        if window.margin_buttons[1].clicked(event.pos):
            window.redo_last_move()

    if window.board.is_game_over() and not window.game_over:
        window.if_game_over()
        return 'main', False
    else:
        return 'game', window


