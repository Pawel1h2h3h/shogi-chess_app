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


### Część refleksyjna

W ramach projektu zrealizowano wiele istotnych funkcji, umożliwiających grę oraz analizę partii Shogi. Stworzono intuicyjny interfejs użytkownika, obsługę ruchów, promocji figur, cofania i ponawiania ruchów oraz system zapisu i odczytu partii w formacie JSON. W pełni zintegrowano aplikację z biblioteką `shogi`, co zapewniło precyzyjne odwzorowanie zasad gry.

#### Osiągnięcia:
1. Zrealizowano kluczowe funkcje:
   - Główne okno aplikacji z wyborem nowej gry oraz analizą zapisanych partii.
   - Obsługa logiki Shogi z wykorzystaniem biblioteki `shogi`.
   - Implementacja interfejsu graficznego z biblioteką `pygame`.
   - Obsługa zapisu i odczytu partii w formacie JSON, z dynamicznie generowaną listą zapisanych gier.
2. Aplikacja działa płynnie w środowiskach Windows, macOS i Linux.
3. Zapewniono łatwą konfigurację poprzez plik `setup.py` i obsługę wirtualnego środowiska.

#### Rzeczy, których nie udało się osiągnąć:
1. **Renderowanie bierek w postaci japońskich znaków:**
   - Gra w Shogi tradycyjnie korzysta z japońskich znaków do oznaczenia figur. Niestety, implementacja tego rozwiązania nie została ukończona.
   - **Powód:** Brak odpowiednich fontów lub obrazów dla bierek. Próba wykorzystania czcionek z japońskimi znakami w `pygame` napotkała problemy z kompatybilnością i czytelnością znaków na planszy.
   - **Skutki:** Bez tego rozwiązania gra może być łatwiejsza dla osób nieznających japońskich znaków.

2. **Pełna personalizacja wyglądu aplikacji:**
   - Choć zaimplementowano obsługę tła i ikon, brak jest zaawansowanej opcji dostosowywania interfejsu (np. zmiany motywu kolorystycznego przez użytkownika).
   - **Powód:** Ograniczenia czasowe.

#### Napotkane przeszkody:
1. **Problemy z bibliotekami:**
   - `pygame` okazało się nieco ograniczone w obsłudze zaawansowanego renderowania tekstu, co utrudniło wprowadzenie japońskich znaków.

#### Co się zmieniło w stosunku do planowanego rozwiązania:
1. Zrezygnowano z użycia japońskich znaków na rzecz bardziej uniwersalnych symboli figur, aby zapewnić minimalną funkcjonalność gry.
2. Wprowadzono bardziej szczegółowy system analizy partii (np. cofanie i odtwarzanie ruchów), co pierwotnie nie było planowane.
3. Aplikacja została zoptymalizowana do obsługi na wielu platformach, choć początkowo skupiano się głównie na jednym systemie operacyjnym.

#### Wnioski:
Projekt udało się zrealizować w dużej mierze zgodnie z założeniami, choć niektóre funkcje wymagały uproszczenia. Kluczowe wyzwania, takie jak obsługa czcionek z japońskimi znakami, wymagałyby więcej czasu na dokładniejsze zbadanie dostępnych rozwiązań. Mimo to aplikacja w obecnej formie stanowi solidną podstawę do dalszego rozwoju np.: tryb online multiplayer.
