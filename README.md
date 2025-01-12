# Aplikacja Shogi

## Dane autora
- **Autor:** Paweł Lisowski
- **Kontakt:** 01187247@pw.edu.pl

## Cel i opis projektu
Aplikacja służy do gry w Shogi oraz analizy zapisanych partii. Użytkownik ma do dyspozycji:
- Główne menu z przyciskiem startu gry i listą zapisanych gier (Top 10).
- Okno gry, w którym może rozgrywać partie w czasie rzeczywistym.
- Okno analizy, pozwalające przeglądać ruchy uprzednio zapisanej gry (cofanie, wznawianie ruchów).

Aplikacja oparta jest na bibliotece **Pygame** (zarządzanie oknem gry i interfejsem) oraz **shogi** (logika gry w Shogi, zarządzanie ruchem figur).

## Podział programu na klasy i opis klas

### `App`
Główna klasa aplikacji, zajmująca się:
- Inicjalizacją okna i zasobów Pygame.
- Zarządzaniem stanami (główne menu, okno gry, okno analizy).
- Uruchamianiem pętli głównej i delegowaniem zdarzeń do właściwych okien.

### `MainWindow`
Klasa reprezentująca główne okno (menu startowe). Odpowiada za:
- Wyświetlanie przycisku startu gry i przycisku wyświetlającego listę zapisanych gier.
- Ładowanie i rysowanie tła.
- Tworzenie przycisków reprezentujących pliki z zapisanymi grami w katalogu `Top10`.

### `GameWindow`
Klasa reprezentująca okno gry w Shogi:
- Zarządza logiką gry (plansza `shogi.Board`, ruchy figur, promocje).
- Rysuje planszę oraz interfejs użytkownika (pola, zbite figury, czas gry).
- Obsługuje cofanie i ponawianie ruchów, a także zapis stanu gry do pliku JSON.

### `AnaliseWindow`
Klasa dziedzicząca z `GameWindow`, rozszerzona o:
- Możliwość odtwarzania ruchów z listy zapisanej gry (sekwencyjne wykonywanie i cofanie).
- Wyróżnianie ruchów, które zostały wykonane lub cofnięte podczas analizy.

### `Button`
Klasa potomna `pygame.Rect`, reprezentująca interaktywny przycisk:
- Może wyświetlać tekst, kolor tła oraz opcjonalnie rysować obwódkę tekstu.
- Pozwala sprawdzać, czy przycisk został kliknięty (obsługa pozycji myszy).
- Stosowana zarówno w interfejsie głównego menu, jak i w planszy gry (np. pola planszy, przyciski marginesu).

### `Game`
Klasa przechowująca informacje o zapisanej partii:
- Listę ruchów (obiekty `shogi.Move`).
- Datę i czas gry.
- Nazwę pliku, w którym gra została zapisana.

### `LoadGameError`
Klasa wyjątku wywoływanego w przypadku błędów podczas ładowania gry z pliku (np. brak pliku lub uszkodzony format JSON).

### `SaveGameError`
   - Klasa reprezentująca wyjątek, który jest zgłaszany podczas problemów z zapisywaniem gry.
   - **Opis:**
     Wyjątek jest zgłaszany, gdy zapis partii Shogi nie powiedzie się, np. z powodu:
     - Błędnego formatu JSON.
     - Braku dostępu do katalogu zapisu.
     - Innych problemów z systemem plików.

### `ModerateGameNamesError`
   - Klasa wyjątków używana w sytuacjach związanych z problemami w nazwach zapisanych gier.
   - **Opis:**
     Wyjątek może wystąpić w sytuacji, gdy:
     - Nazwy plików nie spełniają ustalonych standardów (np. zbyt długa nazwa).

## Instrukcja użytkownika

1. **Uruchamianie aplikacji:**
   - W celu instalacji zależności uruchom plik `setup.py`, który automatycznie utworzy wirtualne środowisko `.venv` i zainstaluje wymagane biblioteki (m.in. `pygame` oraz `python-shogi`).
   - Następnie aktywuj wirtualne środowisko:
     - **Na Windows (PowerShell):**
       ```bash
       .venv\Scripts\Activate.ps1
       ```
     - **Na MacOS/Linux:**
       ```bash
       source .venv/bin/activate
       ```
   - Jeśli `setup.py` nie zadziała, wykonaj następujące kroki ręcznie:
     1. **Utwórz wirtualne środowisko:**
        - W terminalu lub PowerShell wpisz:
          ```bash
          python -m venv .venv
          ```
     2. **Aktywuj wirtualne środowisko:**
        - **Na Windows (PowerShell):**
          ```bash
          .venv\Scripts\Activate.ps1
          ```
        - **Na MacOS/Linux:**
          ```bash
          source .venv/bin/activate
          ```
     3. **Zainstaluj wymagane zależności:**
        - W aktywowanym środowisku uruchom:
          ```bash
          pip install -r requirements.txt
          ```

   - Następnie uruchom główny plik aplikacji:
     ```bash
     python main.py
     ```

---

### Dodatkowe uwagi:
- **Problemy z PowerShell na Windows:**
  - Jeśli aktywacja środowiska w PowerShell powoduje błąd, ustaw politykę wykonywania skryptów za pomocą:
    ```bash
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    ```
   - warto równiez usunąc katalog .venv jezeli się utworzył
  - Po ustawieniu odpowiedniej polityki ponownie spróbuj aktywować środowisko.


- **Sprawdzanie poprawności instalacji:**
  - Po aktywacji środowiska sprawdź wersje zainstalowanych bibliotek:
    ```bash
    pip list
    ```
  - Upewnij się, że `pygame` i `python-shogi` są na liście.

- **Dezaktywacja wirtualnego środowiska:**
  - Aby wyjść z wirtualnego środowiska, wpisz:
    ```bash
    deactivate
    ```

2. **Główne menu (MainWindow):**
   - **Przycisk `START`:** Rozpoczyna nową partię w oknie gry.
   - **Przycisk `Top 10`:** Wyświetla listę zapisanych partii znajdujących się w katalogu `Top10`.
     - Kliknięcie na wybraną pozycję na liście otwiera okno analizy (`AnaliseWindow`).

3. **Rozgrywka (GameWindow):**
   - Po uruchomieniu gry w oknie `GameWindow` można wykonywać ruchy figurami Shogi.
   - Aplikacja wyświetla aktualny stan planszy, zbite figury oraz czas gry.
   - Dostępne są opcje cofania i ponawiania ruchów.
   - Na koniec można zapisać stan gry (plik JSON) w katalogu `Top10`.

4. **Analiza partii (AnaliseWindow):**
   - Wyświetla zapisaną wcześniej partię.
   - Możliwe jest odtwarzanie ruchów (przycisk „do przodu”) lub cofanie wykonanych ruchów (przycisk „do tyłu”).
   - Użytkownik może w dowolnym momencie wyjść do głównego menu.

5. **Zakończenie pracy:**
   - Wyjście z aplikacji następuje poprzez zamknięcie okna (zdarzenie `pygame.QUIT`).

## Opis formatu plików

Aplikacja przechowuje zapisy partii w formacie **JSON** w katalogu `Top10`. Każdy plik ma postać:
```json
{
  "date": "YYYY-MM-DD HH:MM:SS",
  "time": 123,
  "moves": [
    {
      "from": 36,
      "to": 27,
      "promo": false,
      "dropped_type": null
    },
    ...
  ]
}

