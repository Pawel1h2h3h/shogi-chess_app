# Ustawienia planszy
import pygame
import sys
import shogi


# Ustawienia planszy
CELL_SIZE = 80
SCREEN_WIDTH, SCREEN_HEIGHT = 9*CELL_SIZE, 9*CELL_SIZE
BOARD_SIZE = 9


# Kolory
LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
LINE_COLOR = (0, 0, 0)

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shogi")

# Inicjalizacja stanu gry Shogi
board = shogi.Board()


highlighted_squares = []
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
    font = pygame.font.SysFont("Noto Serif JP", CELL_SIZE // 2, bold=True)
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


def find_piece(square):
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

def show_game_over_message():
    """
    Wyświetla komunikat o zakończeniu gry.
    """
    font = pygame.font.SysFont("Arial", 48, bold=True)
    message = f"GAME OVER"
    text = font.render(message, True, (255, 255, 255))  # Biały tekst
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Rysowanie komunikatu na ekranie
    screen.fill((0, 0, 0))  # Wypełnij ekran czarnym kolorem
    screen.blit(text, text_rect)
    pygame.display.flip()

    # Poczekaj kilka sekund
    pygame.time.wait(5000)

pygame.init()

running = True
selected_piece = None
selected_square = None
highlighted_squares = []
king_in_check_square = None
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            square = (pos[1] // CELL_SIZE) * BOARD_SIZE + (pos[0] // CELL_SIZE)

            if selected_piece is None:
                # Wybór figury
                piece = find_piece(square)
                if piece is not None:
                    selected_piece = piece
                    selected_square = square
                    highlighted_squares = get_legal_moves(square)
            else:
                # Ruch figury
                if square in highlighted_squares:
                    promotion = False
                    # Sprawdzenie promocji
                    if is_in_promotion_zone(square, selected_piece.color) and not selected_piece.is_promoted():
                        promotion = ask_for_promotion_gui()

                    move = shogi.Move(from_square=selected_square, to_square=square, promotion=promotion)
                    board.push(move)

                # Reset wyboru
                selected_piece = None
                selected_square = None
                highlighted_squares = []

            # Sprawdzenie szacha
            king_in_check_square = get_king_square_in_check()

            # Sprawdzenie szachmatu
            if board.is_checkmate():
                game_over = True
                show_game_over_message()

    # Rysowanie
    if not game_over:
        screen.fill((0, 0, 0))
        draw_board()
        draw_pieces()
        pygame.display.flip()

pygame.quit()
sys.exit()