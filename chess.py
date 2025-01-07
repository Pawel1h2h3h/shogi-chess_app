# Ustawienia planszy
import pygame
import sys
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
SCREEN_WIDTH, SCREEN_HEIGHT = 11*CELL_SIZE, 9*CELL_SIZE
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

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shogi")

# Inicjalizacja stanu gry Shogi
board = shogi.Board()


# Rysowanie planszy
def draw_board():
    """
    Rysuje szachownice
    """
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            square = row * BOARD_SIZE + col

            # Podświetlenie pola króla w szachu
            if square == king_in_check_square:
                color = (255, 102, 102)  # Lekki czerwony

            # Podświetlenie legalnych pól
            if square in highlighted_squares:
                color = (173, 216, 230)  # Lekki błękit

            pygame.draw.rect(
                screen,
                color,
                (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (9*CELL_SIZE, i * CELL_SIZE), 1)
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_HEIGHT), 1)



def draw_pieces(board):
    """
    Rysuje figury na planszy
    """
    font = pygame.font.SysFont("Arial", CELL_SIZE // 2, bold=True)
    for square in range(81):  # Plansza Shogi ma 81 pól (9x9)
        piece = board.piece_at(square)
        if piece:
            row = square // BOARD_SIZE
            col = square % BOARD_SIZE
            text_color = BLACK if piece.color == shogi.BLACK else WHITE
            symbol = piece.symbol()
            text = font.render(symbol, True, text_color)
            text_rect = text.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))
            screen.blit(text, text_rect)

def draw_undo_redo_buttons():
    """
    Rysuje przciski przewijania ruchów
    """
    x, y = RECT_POS
    width, height = RECT_SIZE

    pygame.draw.rect(screen, GREY, (x, y, width, height))

    pygame.draw.line(screen, BLACK, (x + width // 2, y), (x + width // 2, y + height), 2)

    # Rysowanie trójkąta "cofnij"
    left_triangle = [
        (x + 10, y + height // 2),
        (x + width // 4, y + 10),
        (x + width // 4, y + height - 10),
    ]
    pygame.draw.polygon(screen, BLACK, left_triangle)

    # Rysowanie trójkąta "do przodu"
    right_triangle = [
        (x + width - 10, y + height // 2),
        (x + 3 * width // 4, y + 10),
        (x + 3 * width // 4, y + height - 10),
    ]
    pygame.draw.polygon(screen, BLACK, right_triangle)



def find_piece(square):
    """Znajduje figurę o na odpowiednim polu"""
    return board.piece_at(square)


def is_in_promotion_zone(square, color):
    """
    Sprawdza, czy pole znajduje się w strefie promocji.
    """
    if color == shogi.BLACK:
        return square // BOARD_SIZE in [0, 1, 2]  # Trzy ostatnie rzędy dla czarnych
    elif color == shogi.WHITE:
        return square // BOARD_SIZE in [6, 7, 8]  # Trzy ostatnie rzędy dla białych
    return False


def ask_for_promotion_gui():
    """
    Wyświetla okno dialogowe z pytaniem o promocję.
    """
    font = pygame.font.SysFont("Arial", 24)
    question = font.render("Promote piece? (Y/N)", True, (25, 255, 255))
    screen.blit(question, (SCREEN_WIDTH // 2 - question.get_width() // 2, SCREEN_HEIGHT // 2 - question.get_height() // 2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False


def get_legal_moves(square):
    """
    Zwraca listę pól, na które wybrana figura może się ruszyć.
    """
    moves = list(board.legal_moves)  # Wszystkie możliwe ruchy
    legal_squares = [
        move.to_square for move in moves if move.from_square == square
    ]
    return legal_squares


def get_king_square_in_check():
    """
    Zwraca pole króla, jeśli jest w szachu, w przeciwnym razie None.
    """
    king_square = board.king_squares[board.turn]  # Znajdź pole króla aktualnego gracza
    if board.is_attacked_by(board.turn ^ 1, king_square):  # Sprawdź, czy król jest atakowany
        return king_square
    return None

def show_message(message="GAME OVER", size=48, color=WHITE):
    """
    Wyświetla komunikat.
    """
    font = pygame.font.SysFont("Arial", 48, bold=True)
    text = font.render(message, True, color)  # Biały tekst
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Rysowanie komunikatu na ekranie
    screen.blit(text, text_rect)
    pygame.display.flip()

    # Poczekaj kilka sekund
    pygame.time.wait(5000)

def undo_last_move(undone_moves, selected_piece, selected_square):
    """
    Cofa ostatni ruch na planszy i zapisuje go do listy cofniętych ruchów.

    :param undone_moves: Lista cofniętych ruchów
    :param selected_piece: Wybrana figura (resetuje po cofnięciu ruchu)
    :param selected_square: Wybrane pole (resetuje po cofnięciu ruchu)
    :return: Zaktualizowane zmienne gry
    """
    if board.move_stack:
        move = board.pop()  # Cofnij ostatni ruch
        undone_moves.append(move)  # Zapisz cofnięty ruch
    else:
        show_message("No moves to undo")

    selected_piece = None
    selected_square = None
    return selected_piece, selected_square


def redo_last_move(undone_moves, selected_piece, selected_square):
    """
    Przywraca ostatni cofnięty ruch.

    :param undone_moves: Lista cofniętych ruchów
    :param selected_piece: Wybrana figura (resetuje po przywróceniu ruchu)
    :param selected_square: Wybrane pole (resetuje po przywróceniu ruchu)
    :return: Zaktualizowane zmienne gry
    """
    if undone_moves:
        move = undone_moves.pop()  # Pobierz ostatni cofnięty ruch
        board.push(move)  # Przywróć ruch na planszy
    else:
        show_message('No moves to redo')

    selected_piece = None
    selected_square = None
    return selected_piece, selected_square


def save_game(date, filename="Top10/saved_game.json", timex=10):
    """
    Zapisuje partię do pliku w formacie JSON.

    :param date: Data odbycia partii
    :param filename: Nazwa pliku do zapisu
    :param timex: Czas partii
    """
    data = {
        "date": date,
        "time": timex,
        "moves": []  # Lista ruchów
    }
    try:
        with open(filename, "w") as file:
            # Dodajemy ruchy do listy w JSON
            for move in board.move_stack:
                move_data = {
                    "from": move.from_square,
                    "to": move.to_square,
                    "promo": move.promotion,
                    "dropped_type": move.drop_piece_type
                }
                data["moves"].append(move_data)

            # Zapis danych do pliku JSON
            json.dump(data, file, indent=4)

        show_save_confirmation()
    except IOError as e:
        show_message("Błąd podczas zapisywania partii")
        raise SaveGameError(e)


def rename_and_clean_top_games(directory_path):
    """
    Przetwarza pliki z zapisami partii, sortuje według czasu gry i:
    - Nadaje nazwy Top1_DATE.json do Top10_DATE.json dla 10 najdłuższych partii,
      gdzie DATE pochodzi z klucza 'date' w pliku JSON.
    - Usuwa pliki, które nie mieszczą się w Top10, jeśli plików jest więcej niż 10.

    Args:
        directory_path (str): Ścieżka do katalogu z plikami JSON partii.
    """
    games = []

    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)

        # Wczytaj plik JSON
        if file_name.endswith('.json'):
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if 'time' in data and 'date' in data:
                        games.append((file_name, data['time'], data['date']))
            except Exception as e:
                raise ModerateGameNamesError(e)

    # Sortowanie partii według czasu gry (malejąco)
    games.sort(key=lambda x: x[1], reverse=True)

    # Zmień nazwy dla 10 najdłuższych partii
    for i, (file_name, game_time, game_date) in enumerate(games[:10]):
        new_name = f"Top{i+1}_{game_date}.json"
        old_path = os.path.join(directory_path, file_name)
        new_path = os.path.join(directory_path, new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            raise ModerateGameNamesError(e)

    # Usuwanie pozostałych plików (tylko jeśli jest więcej niż 10 partii)
    if len(games) > 10:
        for file_name, game_time, game_date in games[10:]:
            file_path = os.path.join(directory_path, file_name)
            try:
                os.remove(file_path)
                print(f"Usunięto plik: {file_name}")
            except Exception as e:
                raise ModerateGameNamesError(e)



def show_save_confirmation():
    """
    Wyświetla komunikat o pomyślnym zapisaniu partii na ekranie.
    """
    font = pygame.font.SysFont("Arial", 20)
    message = font.render("Partia zapisana!", True, (0, 255, 0))
    screen.blit(message, (MARGINES_X + 10, CELL_SIZE+20))
    pygame.display.flip()
    pygame.time.wait(2000)  # Wyświetl przez 2 sekundy


def show_load_confirmation(screen):
    """
    :param screen: powierzchnia pygame

    Wyświetla komunikat o pomyślnym wczytaniu partii na ekranie.
    """
    font = pygame.font.SysFont("Arial", 20)
    message = font.render("Partia wczytana!", True, (0, 255, 0))
    screen.blit(message, (MARGINES_X + 10, CELL_SIZE+20))
    pygame.display.flip()
    pygame.time.wait(2000)  # Wyświetl przez 2 sekundy
    return True


def draw_margines():
    """
    Rysuje margines po prawej stronie planszy shogi z podziałem na rzędy.
    """

    font = pygame.font.SysFont("Arial", 14, bold=True)
    text = font.render('↓Captured pieces↓', True, BLACK)
    screen.blit(text, (MARGINES_X + 18, CELL_SIZE - 20))

    # Górna i dolna linia marginesu
    pygame.draw.line(screen, LINE_COLOR, (MARGINES_X, CELL_SIZE), (MARGINES_X1, CELL_SIZE))
    pygame.draw.line(screen, LINE_COLOR, (MARGINES_X, 14 * CELL_SIZE), (MARGINES_X1, 14 * CELL_SIZE))

    # Linie podziału na wiersze
    for i in range(1, 15):
        pygame.draw.line(screen, LINE_COLOR, (MARGINES_X, CELL_SIZE + i * ROW_SIZE), (MARGINES_X1, CELL_SIZE + i * ROW_SIZE))

        # Wyróżnij środkową linię
        if i == 7:
            pygame.draw.line(screen, BLACK, (MARGINES_X, CELL_SIZE + i * ROW_SIZE), (MARGINES_X1, CELL_SIZE + i * ROW_SIZE), 4)


def draw_captured_pieces(color):
    """
    Rysuje zbite figury wybranego gracza (czarnych lub białych) wraz z ich liczbą na marginesie.

    Args:
        color: Kolor gracza (BLACK dla czarnych, WHITE dla białych).
    """
    # Wybór figur na podstawie koloru
    if color == BLACK:
        pieces = convert_captured_to_symbols(get_captured_black())
        text_start_y = CELL_SIZE + 7 * ROW_SIZE + 10

    elif color == WHITE:
        pieces = convert_captured_to_symbols(get_captured_white())
        text_start_y = CELL_SIZE + 5
    else:
        raise ValueError("Nieznany kolor gracza: użyj BLACK lub WHITE.")

    font = pygame.font.SysFont(None, 30)

    text_start_x = MARGINES_X + 10  # Przesunięcie od lewej strony marginesu

    # Rysowanie zbitych figur
    for i, (symbol, count) in enumerate(pieces.items()):
        # Rysowanie symbolu figury
        text_surface = font.render(f"{symbol}", True, color)
        screen.blit(text_surface, (text_start_x, text_start_y + i * ROW_SIZE))

        # Rysowanie liczby figur
        count_surface = font.render(f"x{count}", True, color)
        screen.blit(count_surface, (text_start_x + 40, text_start_y + i * ROW_SIZE))


def get_captured_black():
    """
    Zwraca zbite figury czarnych (SENTE).

    Returns:
        dict: Słownik z typami figur i ich liczbą.
    """
    return board.pieces_in_hand[shogi.BLACK]

def get_captured_white():
    """
    Zwraca zbite figury białych (GOTE).

    Returns:
        dict: Słownik z typami figur i ich liczbą.
    """
    return board.pieces_in_hand[shogi.WHITE]

def convert_captured_to_symbols(captured_dict):
    """
    Konwertuje słownik zbitych figur na listę symboli.

    Args:
        captured_dict (dict): Słownik z typami figur i ich liczbą.

    Returns:
        dict: Słownik z symbolami figur jako kluczami i ich liczbą jako wartościami.
    """
    return {shogi.PIECE_SYMBOLS[piece]: count for piece, count in captured_dict.items()}


def get_clicked_margin_square(x, y):
    """
    Zwraca indeks pola na marginesie, na które kliknięto.

    Args:
        pos (tuple): Współrzędne kliknięcia myszy (x, y).

    Returns:
        int: Indeks klikniętego pola (0-13) lub None, jeśli kliknięto poza marginesem.
    """

    # Sprawdź, czy kliknięcie było na marginesie
    if MARGINES_X <= x <= MARGINES_X1 and CELL_SIZE <= y <= 14 * CELL_SIZE:
        row_index = (y - CELL_SIZE) // ROW_SIZE
        return int(row_index)  # Zwróć indeks pola (0-13)

    return None  # Kliknięcie poza marginesem


def is_margin_square_occupied(margin_square):
    """
    Sprawdza, czy na klikniętym polu marginesu znajduje się figura.

    Args:
        margin_square (int): Indeks pola na marginesie (0-13).
        color: Kolor gracza (shogi.BLACK lub shogi.WHITE).

    Returns:
        tuple: (symbol figury, liczba figur, typ figury, kolor) jeśli pole jest zajęte, inaczej None.
    """
    # Pobierz zbite figury białych lub czarnych
    if margin_square < 7:
        captured_pieces = get_captured_white()
        local_index = margin_square  # Indeks dla białych (0-6)
        color = shogi.WHITE
    else:
        captured_pieces = get_captured_black()
        local_index = margin_square - 7  # Indeks dla czarnych (7-13 -> 0-6)
        color = shogi.BLACK

    # Konwertuj zbite figury na listę
    captured_list = list(captured_pieces.items())

    # Sprawdź, czy pole mieści się w liczbie figur
    if local_index < len(captured_list):
        piece_type, count = captured_list[local_index]
        symbol = shogi.PIECE_SYMBOLS[piece_type]
        return symbol, count, piece_type, color  # Zwróć symbol, liczbę figur i typ figury

    return None  # Pole jest puste

def place_piece_on_board(color, piece_type, target_square):
    """
    Dostawia figurę z marginesu na planszę.

    Args:
        color: Kolor gracza (shogi.BLACK lub shogi.WHITE).
        piece_type: Typ figury do dostawienia (np. shogi.PAWN, shogi.ROOK).
        target_square: Pole, na które figura ma zostać dostawiona (0–80).

    Returns:
        bool: True, jeśli figura została pomyślnie dostawiona, inaczej False.
    """
    # Sprawdź, czy wybrane pole jest puste
    if board.piece_at(target_square) is not None:
        return False

    # Sprawdź, czy gracz ma daną figurę w marginesie
    if not board.has_piece_in_hand(piece_type, color):
        return False

    # Wykonaj ruch dostawienia figury na planszę
    move = shogi.Move(from_square=None, to_square=target_square, promotion=False, drop_piece_type=piece_type)
    if board.is_legal(move):
        board.push(move)
        return True
    else:
        show_message("illegal move - try something else")
        return False




undone_moves = []
running = True
selected_piece = None
selected_square = None
highlighted_squares = []
king_in_check_square = None
game_over = False
start_time = None
end_time = None
add_mode = False
add_piece_data = None


if __name__ == "__main__":
    pygame.init()

    # Pętla gry
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if not add_mode:
                    if y < 9 * CELL_SIZE and x < 9 * CELL_SIZE:
                        square = (y // CELL_SIZE) * BOARD_SIZE + (x // CELL_SIZE)
                    else:
                        square = 1
                else:
                    if y < 9 * CELL_SIZE and x < 9 * CELL_SIZE:
                        square = (y // CELL_SIZE) * BOARD_SIZE + (x // CELL_SIZE)
                        piece_type, color = add_piece_data
                        place_piece_on_board(color, piece_type, target_square=square)
                        add_mode = False

                # Obsługa przycisku "Cofnij"
                if RECT_POS[0] <= x <= RECT_POS[0] + RECT_SIZE[0] // 2 and RECT_POS[1] <= y <= RECT_POS[1] + RECT_SIZE[1]:
                    selected_piece, selected_square = undo_last_move(undone_moves, selected_piece, selected_square)

                # Obsługa przycisku "Do przodu"
                elif RECT_POS[0] + RECT_SIZE[0] // 2 <= x <= RECT_POS[0] + RECT_SIZE[0] and RECT_POS[1] <= y <= RECT_POS[1] + RECT_SIZE[1]:
                    selected_piece, selected_square = redo_last_move(undone_moves, selected_piece, selected_square)

                # Obsługa kliknięcia na margines
                if y > CELL_SIZE and x > 9 * CELL_SIZE:
                    margin_square = get_clicked_margin_square(x, y)
                    if is_margin_square_occupied(margin_square):
                        add_mode = True
                        symbol, count, piece_type, color = is_margin_square_occupied(margin_square)
                        add_piece_data = piece_type, color
                    else:
                        show_message("U have no piece to drop", 34, PURPLE)




                # Obsługa kliknięcia na planszy
                if not add_mode:
                    if selected_piece is None:
                        piece = find_piece(square)
                        if piece is not None:
                            selected_piece = piece
                            selected_square = square
                            highlighted_squares = get_legal_moves(square)
                    else:
                        if square in highlighted_squares:
                            promotion = False
                            if is_in_promotion_zone(square, selected_piece.color) and not selected_piece.is_promoted() and selected_piece.piece_type != shogi.KING:
                                promotion = ask_for_promotion_gui()

                            move = shogi.Move(from_square=selected_square, to_square=square, promotion=promotion)
                            board.push(move)
                            undone_moves.clear()

                            # Rozpoczęcie liczenia czasu przy pierwszym ruchu
                            if start_time is None:
                                start_time = time.time()

                        selected_piece = None
                        selected_square = None
                        highlighted_squares = []

                king_in_check_square = get_king_square_in_check()

                if board.is_game_over():
                    game_over = True
                    end_time = time.time()  # Zapisz czas zakończenia gry
                    end_time -= start_time
                    save_game(date=str(datetime.datetime.now())[:19], filename=f'Top10/game.json', timex=int(end_time))
                    rename_and_clean_top_games('Top10')
                    if board.is_stalemate():
                        show_message('Stalemate')
                    show_message()
                    running = False

        # Obliczanie czasu gry
        if start_time is not None:
            if end_time is None:
                elapsed_time = time.time() - start_time  # Gra w toku
            else:
                elapsed_time = end_time
        else:
            elapsed_time = 0  # Wyświetla 00:00 przed pierwszym ruchem

        minutes, seconds = divmod(int(elapsed_time), 60)
        pygame.display.set_caption(f'SHOGI-GAME {minutes:02}:{seconds:02}')

        # Rysowanie
        if not game_over:
            screen.fill((149, 165, 166))
            draw_margines()
            draw_captured_pieces(WHITE)
            draw_captured_pieces(BLACK)
            draw_undo_redo_buttons()
            draw_board()
            draw_pieces(board)
            pygame.display.flip()

    pygame.quit()
    sys.exit()
