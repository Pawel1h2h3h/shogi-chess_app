import pygame
import shogi
from chess import CELL_SIZE, draw_board, draw_pieces, draw_back_button, screen, RECT_POS, RECT_SIZE
import sys
import json

# Inicjalizacja pygame
pygame.init()
pygame.font.init()  # Upewnij się, że czcionki zostały zainicjalizowane


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


def make_move():
    """
    Wykonuje kolejny ruch z listy ALL_MOVES i dodaje go do DONE_MOVES.
    """
    if ALL_MOVES:
        move = ALL_MOVES.pop(0)  # Pobiera pierwszy ruch z ALL_MOVES
        board.push(move)  # Wykonuje ruch na planszy
        DONE_MOVES.append(move)  # Dodaje ruch do listy DONE_MOVES
        print(f"Ruch wykonany: {move}")
    else:
        print("Brak ruchów do wykonania.")

def back_move():
    """
    Cofnięcie ostatniego ruchu z DONE_MOVES i dodanie go do ALL_MOVES.
    """
    if DONE_MOVES:
        move = DONE_MOVES.pop()  # Pobiera ostatni ruch z DONE_MOVES
        board.pop()  # Cofnięcie ruchu na planszy
        ALL_MOVES.insert(0, move)  # Dodaje cofnięty ruch na początek ALL_MOVES
        print(f"Ruch cofnięty: {move}")
    else:
        print("Brak ruchów do cofnięcia.")

def redo_move():
    """
    Wykonuje ponownie ruch cofnięty do BACKED_MOVES i dodaje go do DONE_MOVES.
    """
    if BACKED_MOVES:
        move = BACKED_MOVES.pop(0)  # Pobiera pierwszy cofnięty ruch
        board.push(move)  # Wykonuje ruch na planszy
        DONE_MOVES.append(move)  # Dodaje ruch do DONE_MOVES
        print(f"Ruch ponownie wykonany: {move}")
    else:
        print("Brak ruchów do ponownego wykonania.")



highlighted_squares = []
running = True
game_over = False
board = shogi.Board()

DONE_MOVES = []  # Ruchy, które zostały już wykonane
BACKED_MOVES = []  # Cofnięte ruchy


if __name__ == "__main__":
    game_file = sys.argv[1]
    ALL_MOVES, TIME = load_game(game_file)

    # Pętla gry
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Obsługa przycisku "Cofnij"
                if RECT_POS[0] <= x <= RECT_POS[0] + RECT_SIZE[0] // 2 and RECT_POS[1] <= y <= RECT_POS[1] + RECT_SIZE[1]:
                    back_move()

                # Obsługa przycisku "Do przodu"
                elif RECT_POS[0] + RECT_SIZE[0] // 2 <= x <= RECT_POS[0] + RECT_SIZE[0] and RECT_POS[1] <= y <= RECT_POS[1] + RECT_SIZE[1]:
                    make_move()

        # Rysowanie
        if not game_over:
            screen.fill((0, 53, 0))
            draw_back_button()
            draw_board()
            draw_pieces(board)
            pygame.display.flip()

    pygame.quit()
    sys.exit()




