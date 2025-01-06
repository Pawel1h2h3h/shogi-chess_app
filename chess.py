# Ustawienia planszy
import pygame
import sys
import shogi
import time
import json


# Ustawienia planszy
CELL_SIZE = 100
SCREEN_WIDTH, SCREEN_HEIGHT = 10*CELL_SIZE, 9*CELL_SIZE
BOARD_SIZE = 9


# Kolory planszy
LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
LINE_COLOR = (0, 0, 0)

# Kolory marginesu
GREY = (200, 200, 200)
BLACK = (0, 0, 0)

# Ustawienie marginesu
RECT_POS = CELL_SIZE*9 + 10, 10
RECT_SIZE = 80, 50
SAVE_POS = CELL_SIZE*9 +10, CELL_SIZE*8 + 10
SAVE_SIZE = RECT_SIZE

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shogi")

# Inicjalizacja stanu gry Shogi
board = shogi.Board()


# Rysowanie planszy
def draw_board():
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
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (SCREEN_WIDTH, i * CELL_SIZE), 1)
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_HEIGHT), 1)



def draw_pieces():
    font = pygame.font.SysFont("Arial", CELL_SIZE // 2, bold=True)
    for square in range(81):  # Plansza Shogi ma 81 pól (9x9)
        piece = board.piece_at(square)
        if piece:
            row = square // BOARD_SIZE
            col = square % BOARD_SIZE
            text_color = (0, 0, 0) if piece.color == shogi.BLACK else (255, 255, 255)
            symbol = piece.symbol()
            text = font.render(symbol, True, text_color)
            text_rect = text.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))
            screen.blit(text, text_rect)

def draw_back_button():
    x, y = RECT_POS
    width, height = RECT_SIZE

    # Rysowanie prostokąta
    pygame.draw.rect(screen, GREY, (x, y, width, height))

    # Rysowanie linii podziału
    pygame.draw.line(screen, BLACK, (x + width // 2, y), (x + width // 2, y + height), 2)

    # Rysowanie trójkąta "cofnij"
    left_triangle = [
        (x + 10, y + height // 2),  # Wierzchołek wewnętrzny
        (x + width // 4, y + 10),  # Wierzchołek górny
        (x + width // 4, y + height - 10),  # Wierzchołek dolny
    ]
    pygame.draw.polygon(screen, BLACK, left_triangle)

    # Rysowanie trójkąta "do przodu"
    right_triangle = [
        (x + width - 10, y + height // 2),  # Wierzchołek wewnętrzny
        (x + 3 * width // 4, y + 10),  # Wierzchołek górny
        (x + 3 * width // 4, y + height - 10),  # Wierzchołek dolny
    ]
    pygame.draw.polygon(screen, BLACK, right_triangle)


def draw_save_button():
    x, y = SAVE_POS
    width, height = SAVE_SIZE

    # Rysowanie prostokąta przycisku
    pygame.draw.rect(screen, GREY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)  # Kontur przycisku

    # Tekst na przycisku
    font = pygame.font.SysFont('Arial', 20, bold=True)
    message = 'SAVE'
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))

    # Rysowanie tekstu
    screen.blit(text, text_rect)



def find_piece(square):
    """Znajduje figurę o na odpowiednim polu"""
    return board.piece_at(square)


def get_square_from_position(pos):
    x, y = pos
    col = x // CELL_SIZE
    row = y // CELL_SIZE

    # Mapowanie do notacji Shogi
    col_notation = 'ABCDEFGHI'
    row_notation = '987654321'

    if 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE:
        return f'{row_notation[row]}{col_notation[col]}'
    return None

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

#ROZRÓŻNIC GAME OVER
def show_game_over_message():
    """
    Wyświetla komunikat o zakończeniu gry.
    """
    font = pygame.font.SysFont("Arial", 48, bold=True)
    message = f"GAME OVER"
    text = font.render(message, True, (255, 255, 255))  # Biały tekst
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
        print("Cofnięto ruch:", move)
    else:
        print("Brak ruchów do cofnięcia.")

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
        print("Przywrócono ruch:", move)
    else:
        print("Brak ruchów do przywrócenia.")

    selected_piece = None
    selected_square = None
    return selected_piece, selected_square


def save_game(filename="Top10/saved_game.json", timex=10):
    """
    Zapisuje aktualny stan partii do pliku w formacie JSON oraz wszystkie wykonane ruchy.

    :param filename: Nazwa pliku do zapisu
    :param timex: Czas partii
    """
    data = {
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
                    "promo": move.promotion
                }
                data["moves"].append(move_data)

            # Zapis danych do pliku JSON
            json.dump(data, file, indent=4)

        print(f"Partia została zapisana do pliku: {filename}")
    except IOError as e:
        print(f"Błąd podczas zapisywania partii: {e}")

def show_save_confirmation(screen):
    """
    Wyświetla komunikat o pomyślnym zapisaniu partii na ekranie.

    :param screen: Obiekt ekranu pygame
    """
    font = pygame.font.SysFont("Arial", 24)
    message = font.render("Partia zapisana!", True, (0, 255, 0))
    screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT - 50))
    pygame.display.flip()
    pygame.time.wait(2000)  # Wyświetl przez 2 sekundy


def load_game(filename='Top10/saved_game.json'):
    """
    Wczytuje partię z pliku JSON i ustawia stan planszy.

    :param filename: Nazwa pliku z zapisem w formacie JSON
    :return: Lista ruchów i czas gry
    """
    try:
        with open(filename, "r") as fp:
            # Wczytaj dane z pliku JSON
            data = json.load(fp)

            # Pobierz czas gry
            game_time = data.get("time", 0)

            # Pobierz listę ruchów
            moves = []
            for move_params in data.get("moves", []):
                move = shogi.Move(
                    from_square=move_params["from"],
                    to_square=move_params["to"],
                    promotion=move_params["promo"]
                )
                moves.append(move)

            print(f"Partia wczytana z pliku: {filename}")
            return moves, game_time

    except FileNotFoundError:
        print(f"Błąd: Plik {filename} nie został znaleziony.")
        return None, None
    except json.JSONDecodeError:
        print(f"Błąd: Nieprawidłowy format pliku JSON: {filename}")
        return None, None

# Pozycja i rozmiar przycisku "LOAD"
LOAD_POS = SAVE_POS[0], SAVE_POS[1] - SAVE_SIZE[1] - 10

def draw_load_button():
    x, y = LOAD_POS
    width, height = SAVE_SIZE

    # Rysowanie prostokąta przycisku
    pygame.draw.rect(screen, GREY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)  # Kontur przycisku

    # Tekst na przycisku
    font = pygame.font.SysFont('Arial', 20, bold=True)
    message = 'LOAD'
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))

    # Rysowanie tekstu
    screen.blit(text, text_rect)

def show_load_confirmation(screen):
    font = pygame.font.SysFont("Arial", 24)
    message = font.render("Partia wczytana!", True, (0, 255, 0))
    screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT - 50))
    pygame.display.flip()
    pygame.time.wait(2000)  # Wyświetl przez 2 sekundy


undone_moves = []
running = True
selected_piece = None
selected_square = None
highlighted_squares = []
king_in_check_square = None
game_over = False
start_time = None
end_time = None  # Czas zakończenia gry, początkowo None

pygame.init()


# Pętla gry
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if y < 9 * CELL_SIZE and x < 9 * CELL_SIZE:
                square = (y // CELL_SIZE) * BOARD_SIZE + (x // CELL_SIZE)

            # Rozpoczęcie liczenia czasu przy pierwszym ruchu
            if start_time is None:
                start_time = time.time()

            # Obsługa przycisku "Cofnij"
            if RECT_POS[0] <= x <= RECT_POS[0] + RECT_SIZE[0] // 2 and RECT_POS[1] <= y <= RECT_POS[1] + RECT_SIZE[1]:
                selected_piece, selected_square = undo_last_move(undone_moves, selected_piece, selected_square)

            # Obsługa przycisku "Do przodu"
            elif RECT_POS[0] + RECT_SIZE[0] // 2 <= x <= RECT_POS[0] + RECT_SIZE[0] and RECT_POS[1] <= y <= RECT_POS[1] + RECT_SIZE[1]:
                selected_piece, selected_square = redo_last_move(undone_moves, selected_piece, selected_square)

            elif SAVE_POS[0] <= x <= SAVE_POS[0] + SAVE_SIZE[0] and SAVE_POS[1] <= y <= SAVE_POS[1] + SAVE_SIZE[1]:
                save_game()
                show_save_confirmation(screen)
            elif LOAD_POS[0] <= x <= LOAD_POS[0] + SAVE_SIZE[0] and LOAD_POS[1] <= y <= LOAD_POS[1] + SAVE_SIZE[1]:
                x, y = load_game()
                print(x)


            # Obsługa kliknięcia na planszy
            elif selected_piece is None:
                piece = find_piece(square)
                if piece is not None:
                    selected_piece = piece
                    selected_square = square
                    highlighted_squares = get_legal_moves(square)
            else:
                if square in highlighted_squares:
                    promotion = False
                    if is_in_promotion_zone(square, selected_piece.color) and not selected_piece.is_promoted():
                        promotion = ask_for_promotion_gui()

                    move = shogi.Move(from_square=selected_square, to_square=square, promotion=promotion)
                    board.push(move)
                    undone_moves.clear()

                selected_piece = None
                selected_square = None
                highlighted_squares = []

            king_in_check_square = get_king_square_in_check()

            if board.is_game_over():
                game_over = True
                end_time = time.time()  # Zapisz czas zakończenia gry
                show_game_over_message()

    # Obliczanie czasu gry
    if start_time is not None:
        if end_time is None:
            elapsed_time = time.time() - start_time  # Gra w toku
        else:
            elapsed_time = end_time - start_time  # Gra zakończona
    else:
        elapsed_time = 0  # Wyświetla 00:00 przed pierwszym ruchem

    minutes, seconds = divmod(int(elapsed_time), 60)
    pygame.display.set_caption(f'SHOGI-GAME {minutes:02}:{seconds:02}')

    # Rysowanie
    if not game_over:
        screen.fill((0, 53, 0))
        draw_back_button()
        draw_save_button()
        draw_load_button()
        draw_board()
        draw_pieces()
        pygame.display.flip()

pygame.quit()
sys.exit()

