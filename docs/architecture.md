# Tetris – Architektur und Abläufe

[← Startseite der Dokumentation](index.md)

Dokumentation zu den Modulen in `Quickstart mit Claude/`.
Die Diagramme sind in [Mermaid](https://mermaid.js.org/) geschrieben und werden
z. B. auf GitHub und in VS Code direkt als Grafik angezeigt.

Die Software ist objektorientiert und wird deshalb mit UML beschrieben:

| UML-Diagramm | Abschnitt | Umsetzung in Mermaid |
|---|---|---|
| Paketdiagramm | „Module und Abhängigkeiten“ | ersatzweise `flowchart` mit Subgraph |
| Klassendiagramm | „Klassendiagramm“ | `classDiagram` |
| Zustandsdiagramm | „Spielzustände“, „Zustände der Lösch-Animation“ | `stateDiagram-v2` |
| Sequenzdiagramm | „Zusammenspiel der Objekte“ | `sequenceDiagram` |
| Aktivitätsdiagramm | „Grober Ablauf“ und die Details dazu | ersatzweise `flowchart` |

Mermaid kennt kein Paket- und kein Aktivitätsdiagramm. Die Ersatzdiagramme
halten sich an deren Bedeutung: Pfeile zwischen Modulen sind
Import-Abhängigkeiten, Rauten sind Entscheidungen, abgerundete Kästen Start
und Ende.

## Module und Abhängigkeiten

<!-- --8<-- [start:module] -->
```mermaid
flowchart TB
    app["Quickstart_mit_Claude.py<br/>TetrisApp"]
    view["view.py<br/>Renderer"]
    tk[["tkinter"]]
    test["test_tetris.py<br/>Unit-Tests"]

    subgraph logik ["ohne tkinter"]
        direction LR
        model["model.py<br/>Piece · Board · Bag · Game"]
        menu["menu.py<br/>PauseMenu"]
        anim["animation.py<br/>ClearAnimation"]
    end

    app --> view
    app --> logik
    view --> logik
    test --> logik
    app -.-> tk
    view -.-> tk
```

Paketdiagramm (Ersatz): Ein Pfeil bedeutet „importiert“; ein Pfeil auf den Kasten heißt, dass alle
drei Module darin importiert werden. Nur `view.py` und
`Quickstart_mit_Claude.py` hängen von tkinter ab (gestrichelt). Alles im Kasten
„ohne tkinter“ lässt sich ohne Fenster testen.
<!-- --8<-- [end:module] -->

## Klassendiagramm

```mermaid
classDiagram
    direction LR

    namespace model {
        class Piece {
            <<frozen dataclass>>
            +tuple shape
            +int x
            +int y
            +cells() Iterator
            +moved(dx, dy) Piece
            +rotated() Piece
        }
        class Board {
            +int cols
            +int rows
            -list _grid
            +grid tuple
            +collides(piece) bool
            +place(piece)
            +full_rows() list
            +remove_rows(rows)
        }
        class Bag {
            -tuple _shapes
            -Random _rng
            -list _items
            +take() tuple
        }
        class GameState {
            <<enum>>
            PLAYING
            CLEARING
            GAME_OVER
        }
        class Game {
            -Bag _bag
            +Game(board, bag)
            +board Board
            +piece Piece
            +next_shape tuple
            +score int
            +lines int
            +level int
            +state GameState
            +clearing list
            +tick_delay int
            +spawn()
            +move(dx, dy) bool
            +rotate() bool
            +soft_drop() bool
            +hard_drop() bool
            +step() bool
            +lock() bool
            +finish_clear()
            +ghost() Piece
        }
    }

    namespace menu {
        class PauseMenu {
            +tuple ITEMS$
            +is_open bool
            +index int
            +selected str
            +open()
            +close()
            +up()
            +down()
        }
    }

    namespace animation {
        class ClearAnimation {
            +int BLINK_FRAMES = 6$
            +int BLINK_DELAY = 70$
            +int WIPE_DELAY = 40$
            +list rows
            +int cols
            -int _frame
            -int _wiped
            +flash bool
            +step() Optional~int~
            +hides(col) bool
        }
    }

    namespace view {
        class Renderer {
            +Canvas canvas
            +int width
            +int height
            +draw(game, menu, anim)
            +draw_board(game, anim)
            +draw_panel(game)
            +draw_menu(menu)
            +draw_game_over()
            +draw_overlay_box(half_height)
            +cell(c, r, size, ox, oy, ghost)
        }
    }

    namespace Quickstart_mit_Claude {
        class TetrisApp {
            +Tk root
            +int cols
            +int rows
            +Renderer renderer
            +PauseMenu menu
            -Game _game
            -ClearAnimation _anim
            -str _job
            -str _anim_job
            +TetrisApp(root, cols, rows, renderer, menu)
            +new_game()
            +cancel_tick()
            +cancel_timers()
            +draw()
            +schedule()
            +tick()
            +start_clear_animation()
            +animate_clear()
            +on_key(event)
            +on_game_key(key)
            +on_menu_key(key)
            +select_menu_item()
        }
    }

    Game o-- Board
    Game o-- Bag
    Game --> Piece : piece
    Game --> GameState : state
    Board ..> Piece : prüft / setzt ab
    TetrisApp *-- Game
    TetrisApp o-- PauseMenu
    TetrisApp o-- Renderer
    TetrisApp "1" --> "0..1" ClearAnimation : _anim
    Renderer ..> Game : liest
    Renderer ..> PauseMenu : liest
    Renderer ..> ClearAnimation : liest
```

Die Klassen verteilen sich auf fünf Module:

| Modul | Klassen | Kennt tkinter? |
|---|---|---|
| `model.py` | `Piece`, `Board`, `Bag`, `GameState`, `Game` | nein |
| `menu.py` | `PauseMenu` | nein |
| `animation.py` | `ClearAnimation` | nein |
| `view.py` | `Renderer` | ja |
| `Quickstart_mit_Claude.py` | `TetrisApp`, `main()` | ja |

- **`Piece` ist unveränderlich.** `moved()` und `rotated()` liefern neue Steine.
  `Game` probiert einen Kandidaten aus und übernimmt ihn nur, wenn
  `Board.collides()` nichts dagegen hat.
- **`Game` prüft seinen Zustand selbst.** Bewegungen wirken nur in `PLAYING`.
  Deshalb muss die `TetrisApp` nicht überall Flags abfragen.
- **`Game` meldet volle Reihen.** `step()` und `hard_drop()` geben True
  zurück, wenn der Stein abgesetzt wurde und Reihen voll sind. Die
  `TetrisApp` startet dann die Animation.
- **`ClearAnimation.step()`** liefert die Wartezeit bis zum nächsten Schritt
  in ms, am Ende der Animation `None`.
- **Der `Renderer` liest nur.** Er bekommt `Game`, `PauseMenu` und
  `ClearAnimation` übergeben und verändert nichts daran.
- **Zustand ist gekapselt.** Veränderlicher Zustand liegt in `_`-Attributen
  (im Diagramm mit `-`); nach außen gibt es nur lesende Properties (ohne
  Typ davor, z. B. `score int`). `Board.grid` liefert eine unveränderliche
  Kopie. Ändern lässt sich das Spiel nur über seine Aktionen.
- **Abhängigkeiten werden übergeben.** `Game` bekommt `Board` und `Bag`,
  die `TetrisApp` bekommt `Renderer` und `PauseMenu` optional über den
  Konstruktor (im Diagramm `o--`). Ohne Angabe legen sie Standardobjekte an.
  So können Tests z. B. ein kleines Spielfeld oder einen Beutel mit festem
  Zufall übergeben.
- **UML-Notation:** `+` öffentlich, `-` privat (in Python: `_`-Präfix),
  `$` statisch. Rauten: `*--` Komposition (das Ganze erzeugt den Teil),
  `o--` Aggregation (der Teil kann übergeben werden), gestrichelt `..>`
  Abhängigkeit. Multiplizitäten stehen nur, wo sie nicht 1 sind: Eine
  `TetrisApp` hat höchstens eine laufende `ClearAnimation`.
- **Abweichung von UML:** Properties stehen als `name typ` ohne Klammern.
  In UML wären es Attribute mit `{readOnly}`; diesen Zusatz kann Mermaid
  nicht darstellen.
- `_job` und `_anim_job` in der `TetrisApp` enthalten die IDs der mit
  `root.after()` geplanten Timer oder `None`, wenn gerade keiner geplant ist.

## Spielzustände

<!-- --8<-- [start:zustaende] -->
```mermaid
stateDiagram-v2
    [*] --> PLAYING : Game()
    PLAYING --> CLEARING : lock() mit vollen Reihen
    CLEARING --> PLAYING : finish_clear()
    PLAYING --> GAME_OVER : spawn() ohne Platz
    CLEARING --> GAME_OVER : finish_clear() → spawn() ohne Platz
    GAME_OVER --> [*]
```
<!-- --8<-- [end:zustaende] -->

Die Pause ist kein Spielzustand: Sie gehört zur Oberfläche und steckt in
`PauseMenu.is_open`. Das `Game` merkt davon nichts, die `TetrisApp` ruft
während der Pause einfach `game.step()` nicht auf.

## Zustände der Lösch-Animation

<!-- --8<-- [start:animation_zustaende] -->
```mermaid
stateDiagram-v2
    state "Blinken" as Blinken
    state "Auflösen" as Aufloesen
    [*] --> Blinken : ClearAnimation(rows, cols)
    Blinken --> Blinken : step() → 70 ms, flash wechselt
    Blinken --> Aufloesen : step() nach BLINK_FRAMES Schritten
    Aufloesen --> Aufloesen : step() → 40 ms, je Seite eine Spalte mehr
    Aufloesen --> [*] : step() → None, alle Spalten aufgelöst
```
<!-- --8<-- [end:animation_zustaende] -->

Die Phasen sind kein eigenes Attribut, sondern ergeben sich aus dem
internen Schrittzähler. Bei 10 Spalten dauert die Animation
6 × 70 ms + 5 × 40 ms = 620 ms.

## Zusammenspiel der Objekte

### Spieltakt mit vollen Reihen

Ein Stein setzt auf, füllt eine Reihe, und die Reihe wird nach der Animation
gelöscht.

<!-- --8<-- [start:sequenz_loeschen] -->
```mermaid
sequenceDiagram
    participant Tk as tkinter (root)
    participant App as TetrisApp
    participant G as Game
    participant B as Board
    participant A as ClearAnimation
    participant R as Renderer

    Tk->>App: tick()
    App->>G: step()
    G->>G: move(0, 1) → False, kein Platz
    G->>G: lock()
    G->>B: place(piece)
    G->>B: full_rows()
    B-->>G: Zeilennummern
    Note over G: state = CLEARING
    G-->>App: True
    App->>App: start_clear_animation()
    App->>Tk: after_cancel(_job)
    App->>A: ClearAnimation(game.clearing, cols)
    loop solange step() eine Wartezeit liefert
        App->>A: step()
        A-->>App: 70 oder 40 ms
        App->>R: draw(game, menu, anim)
        R->>A: flash, hides(col)
        App->>Tk: after(delay, animate_clear)
        Tk->>App: animate_clear()
    end
    App->>A: step()
    A-->>App: None
    App->>G: finish_clear()
    G->>B: remove_rows(rows)
    G->>G: spawn()
    Note over G: state = PLAYING
    App->>R: draw(game, menu, None)
    App->>Tk: after(game.tick_delay, tick)
```
<!-- --8<-- [end:sequenz_loeschen] -->

### Tastendruck im laufenden Spiel

<!-- --8<-- [start:sequenz_taste] -->
```mermaid
sequenceDiagram
    participant Tk as tkinter (root)
    participant App as TetrisApp
    participant M as PauseMenu
    participant G as Game
    participant R as Renderer

    Tk->>App: on_key(event)
    App->>M: is_open
    M-->>App: False
    App->>G: state
    G-->>App: PLAYING
    App->>App: on_game_key(key)
    alt ← oder →
        App->>G: move(-1 oder 1, 0)
    else ↑
        App->>G: rotate()
    else ↓
        App->>G: soft_drop()
    else Esc oder P
        App->>M: open()
    else Leertaste
        App->>G: hard_drop()
        G-->>App: True bei vollen Reihen
        Note over App,G: volle Reihen: start_clear_animation()<br/>wie im Spieltakt, statt draw()
    end
    App->>R: draw(game, menu, anim)
```
<!-- --8<-- [end:sequenz_taste] -->

Die `Game`-Methoden prüfen selbst, ob der Zug erlaubt ist. Die `TetrisApp`
zeichnet danach immer neu, auch wenn sich nichts geändert hat.

## Grober Ablauf

Aktivitätsdiagramm (Ersatz): Nach dem Start übernimmt die Tk-Ereignisschleife. Sie ruft drei Callbacks der
`TetrisApp` auf, die sich über Timer (`root.after`) wieder anmelden.

<!-- --8<-- [start:ablauf] -->
```mermaid
flowchart TD
    start(["Programmstart"]) --> main["main()<br/>root = tk.Tk()"]
    main --> init["TetrisApp.__init__()<br/>Renderer und PauseMenu anlegen,<br/>on_key an Tasten binden"]
    init --> ng["new_game()<br/>Timer abbrechen,<br/>neues Game(Board(cols, rows))"]
    ng --> sched["schedule()<br/>root.after(game.tick_delay, tick)"]
    sched --> loop{{"root.mainloop()<br/>Tk wartet auf Ereignisse"}}

    loop -->|"Takt-Timer"| tick["tick()<br/>game.step()"]
    loop -->|"Taste"| key["on_key()<br/>game.move/rotate/…, Menü"]
    loop -->|"Animations-Timer"| anim["animate_clear()<br/>anim.step()"]
    loop -->|"root.destroy()"| stop(["Programmende"])

    tick -->|"nächster Takt"| sched
    tick -->|"step() = True"| anim
    key -->|"hard_drop() = True"| anim
    anim -->|"nächster Schritt"| loop
    anim -->|"fertig: game.finish_clear()"| sched
    key --> loop
    key -->|"R / Neustart"| ng
```
<!-- --8<-- [end:ablauf] -->

### Detail: Spieltakt `tick()`

Aktivitätsdiagramm (Ersatz) für den Ablauf in der Methode.

<!-- --8<-- [start:tick] -->
```mermaid
flowchart TD
    tick["TetrisApp.tick()"] --> paused{"Menü offen?"}
    paused -->|ja| tnext
    paused -->|nein| step["game.step()"]
    step --> down{"Platz darunter?"}
    down -->|ja| moved["Stein eine Zeile tiefer"]
    down -->|nein| lock["game.lock()<br/>board.place(piece)"]
    lock --> full{"board.full_rows()?"}
    full -->|nein| spawn["game.spawn()<br/>(kein Platz: GAME_OVER)<br/>step() gibt False zurück"]
    full -->|ja| clearing["state = CLEARING<br/>step() gibt True zurück"]
    moved --> draw["draw()"]
    spawn --> draw
    clearing --> sca["start_clear_animation()"]
    draw --> tnext{"state = PLAYING?"}
    sca --> tnext
    tnext -->|ja| sched["schedule()<br/>nächster tick()"]
    tnext -->|nein| none["kein neuer Takt"]
```
<!-- --8<-- [end:tick] -->

### Detail: Lösch-Animation `animate_clear()`

Aktivitätsdiagramm (Ersatz) für den Ablauf in der Methode.

<!-- --8<-- [start:animation] -->
```mermaid
flowchart TD
    sca["start_clear_animation()<br/>cancel_tick(),<br/>anim = ClearAnimation(...)"] --> anim
    anim["animate_clear()<br/>delay = anim.step()"] --> q{"delay?"}
    q -->|"70 ms: Blinkphase"| blink["anim.flash wechselt<br/>Reihen gefüllt / als Umriss"]
    q -->|"40 ms: Auflösephase"| wipe["je Seite eine Spalte mehr aufgelöst<br/>Renderer blendet Spalten<br/>von der Mitte aus aus"]
    blink --> again["draw()<br/>root.after(delay, animate_clear)"]
    wipe --> again
    q -->|"None: fertig"| fin["game.finish_clear()<br/>Reihen entfernen, Punkte und Level,<br/>spawn(), draw()"]
    fin -->|"state = PLAYING"| sched["schedule()<br/>Spieltakt läuft wieder"]
```
<!-- --8<-- [end:animation] -->

### Detail: Tastatur `on_key()`

Aktivitätsdiagramm (Ersatz) für den Ablauf in der Methode.

<!-- --8<-- [start:tastatur] -->
```mermaid
flowchart TD
    key["on_key()"] --> paused{"Pausenmenü<br/>offen?"}
    paused -->|ja| menu["on_menu_key()"]
    menu --> m1["↑ ↓: menu.up() / menu.down()"]
    menu --> m2["Enter / Leer: select_menu_item()<br/>Weiter · Neustart · Beenden"]
    menu --> m3["Esc / P: menu.close()"]
    paused -->|nein| r{"R?"}
    r -->|ja| ng["new_game()"]
    r -->|nein| blocked{"state ≠ PLAYING?"}
    blocked -->|"ja (Esc bei GAME_OVER: destroy())"| ignore["Taste ignorieren"]
    blocked -->|nein| gk["on_game_key()"]
    gk --> act["← → game.move()<br/>↑ game.rotate()<br/>↓ game.soft_drop()<br/>Esc / P menu.open()"]
    gk -->|Leertaste| hd{"game.hard_drop()<br/>volle Reihen?"}
    hd -->|ja| ksca["start_clear_animation()"]
    hd -->|nein| kdraw
    act --> kdraw["draw()"]
```
<!-- --8<-- [end:tastatur] -->

### Erläuterung

- **Keine eigene Schleife:** Die Endlosschleife ist `root.mainloop()`. Tk ruft
  von dort aus die Callbacks `tick()`, `on_key()` und `animate_clear()` auf.
- **Spieltakt:** `schedule()` meldet mit `root.after()` den nächsten `tick()`
  an, `tick()` ruft am Ende wieder `schedule()` auf. Die Wartezeit kommt aus
  `game.tick_delay` und sinkt mit dem Level von 500 ms auf minimal 80 ms.
- **Pause:** `tick()` läuft weiter, ruft aber `game.step()` nicht auf.
- **Lösch-Animation:** `Game` bleibt im Zustand `CLEARING`, bis die
  `TetrisApp` nach der Animation `finish_clear()` aufruft. Bis dahin ist der
  Spieltakt angehalten. Die Animation verändert das Spielfeld nicht, der
  `Renderer` blendet die Zellen nur aus.
- **Leertaste:** `game.hard_drop()` setzt den Stein direkt an die Position
  von `ghost()` und ruft dann `lock()` auf, mit denselben Folgen wie im
  Spieltakt. Ohne volle Reihen läuft der bestehende Takt-Timer einfach weiter.
  Mit vollen Reihen bricht `start_clear_animation()` ihn ab, bis die
  Animation fertig ist.
- **Programmende:** `root.destroy()` (Menüpunkt „Beenden“ oder Esc bei Game
  Over) schließt das Fenster, dadurch kehrt `mainloop()` zurück.
