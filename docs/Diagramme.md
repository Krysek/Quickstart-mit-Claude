# Tetris – Diagramme

Dokumentation zu den Modulen in `Quickstart mit Claude/`.
Die Diagramme sind in [Mermaid](https://mermaid.js.org/) geschrieben und werden
z. B. auf GitHub und in VS Code direkt als Grafik angezeigt.

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

Ein Pfeil bedeutet „importiert“; ein Pfeil auf den Kasten heißt, dass alle
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
            +list grid
            +collides(piece) bool
            +place(piece)
            +full_rows() list
            +remove_rows(rows)
        }
        class Bag {
            +tuple shapes
            +Random rng
            +list items
            +take() tuple
        }
        class GameState {
            <<enum>>
            PLAYING
            CLEARING
            GAME_OVER
        }
        class Game {
            +Board board
            +Bag bag
            +Piece piece
            +tuple next_shape
            +int score
            +int lines
            +int level
            +GameState state
            +list clearing
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
            +bool is_open
            +int index
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
            +list rows
            +int cols
            +int frame
            +bool flash
            +int wiped
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
            +cell(c, r, size, ox, oy, ghost)
        }
    }

    class TetrisApp {
        +Tk root
        +int cols
        +int rows
        +Renderer renderer
        +PauseMenu menu
        +Game game
        +ClearAnimation anim
        +str job
        +str anim_job
        +new_game()
        +cancel_tick()
        +cancel_timers()
        +draw()
        +schedule()
        +tick()
        +start_clear_animation()
        +animate_clear()
        +on_key(event)
        +on_menu_key(key)
        +select_menu_item()
    }

    Game *-- Board
    Game *-- Bag
    Game --> Piece : piece
    Game --> GameState : state
    Board ..> Piece : prüft / setzt ab
    TetrisApp *-- Game
    TetrisApp *-- PauseMenu
    TetrisApp *-- Renderer
    TetrisApp --> ClearAnimation : anim
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
- `job` und `anim_job` in der `TetrisApp` enthalten die IDs der mit
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

## Grober Ablauf

Nach dem Start übernimmt die Tk-Ereignisschleife. Sie ruft drei Callbacks der
`TetrisApp` auf, die sich über Timer (`root.after`) wieder anmelden.

<!-- --8<-- [start:ablauf] -->
```mermaid
flowchart TD
    start(["Programmstart"]) --> main["main()<br/>root = tk.Tk()"]
    main --> init["TetrisApp.__init__()<br/>Renderer und PauseMenu anlegen,<br/>on_key an Tasten binden"]
    init --> ng["new_game()<br/>Timer abbrechen, neues Game()"]
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

<!-- --8<-- [start:animation] -->
```mermaid
flowchart TD
    sca["start_clear_animation()<br/>cancel_tick(),<br/>anim = ClearAnimation(...)"] --> anim
    anim["animate_clear()<br/>delay = anim.step()"] --> q{"delay?"}
    q -->|"70 ms: Blinkphase"| blink["anim.flash wechselt<br/>Reihen gefüllt / als Umriss"]
    q -->|"40 ms: Auflösephase"| wipe["anim.wiped += 1<br/>Renderer blendet Spalten<br/>von der Mitte aus aus"]
    blink --> again["draw()<br/>root.after(delay, animate_clear)"]
    wipe --> again
    q -->|"None: fertig"| fin["game.finish_clear()<br/>Reihen entfernen, Punkte und Level,<br/>spawn(), draw()"]
    fin -->|"state = PLAYING"| sched["schedule()<br/>Spieltakt läuft wieder"]
```
<!-- --8<-- [end:animation] -->

### Detail: Tastatur `on_key()`

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
    blocked -->|nein| act["← → game.move()<br/>↑ game.rotate()<br/>↓ game.soft_drop()<br/>Esc / P menu.open()"]
    blocked -->|"nein, Leertaste"| hd{"game.hard_drop()<br/>volle Reihen?"}
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
