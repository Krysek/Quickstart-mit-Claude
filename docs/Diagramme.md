# Tetris – Diagramme

Dokumentation zu den Modulen in `Quickstart mit Claude/`.
Die Diagramme sind in [Mermaid](https://mermaid.js.org/) geschrieben und werden
z. B. auf GitHub und in VS Code direkt als Grafik angezeigt.

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
            +hard_drop()
            +step()
            +lock()
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

    namespace view {
        class ClearAnimation {
            +int BLINK_FRAMES = 6$
            +list rows
            +int cols
            +int frame
            +bool flash
            +int wiped
            +step() int
            +hides(col) bool
        }
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
        +Renderer renderer
        +PauseMenu menu
        +Game game
        +ClearAnimation anim
        +str job
        +str anim_job
        +new_game()
        +update()
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

Die Klassen verteilen sich auf vier Module:

| Modul | Klassen | Kennt tkinter? |
|---|---|---|
| `model.py` | `Piece`, `Board`, `Bag`, `GameState`, `Game` | nein |
| `menu.py` | `PauseMenu` | nein |
| `view.py` | `ClearAnimation`, `Renderer` | ja (nur `Renderer`) |
| `Quickstart_mit_Claude.py` | `TetrisApp`, `main()` | ja |

- **`Piece` ist unveränderlich.** `moved()` und `rotated()` liefern neue Steine.
  `Game` probiert einen Kandidaten aus und übernimmt ihn nur, wenn
  `Board.collides()` nichts dagegen hat.
- **`Game` prüft seinen Zustand selbst.** Bewegungen wirken nur in `PLAYING`.
  Deshalb muss die `TetrisApp` nicht überall Flags abfragen.
- **Der `Renderer` liest nur.** Er bekommt `Game`, `PauseMenu` und
  `ClearAnimation` übergeben und verändert nichts daran.
- `job` und `anim_job` in der `TetrisApp` enthalten die IDs der mit
  `root.after()` geplanten Timer oder `None`, wenn gerade keiner geplant ist.

## Spielzustände

```mermaid
stateDiagram-v2
    [*] --> PLAYING : Game()
    PLAYING --> CLEARING : lock() mit vollen Reihen
    CLEARING --> PLAYING : finish_clear()
    PLAYING --> GAME_OVER : spawn() ohne Platz
    CLEARING --> GAME_OVER : finish_clear() → spawn() ohne Platz
    GAME_OVER --> [*]
```

Die Pause ist kein Spielzustand: Sie gehört zur Oberfläche und steckt in
`PauseMenu.is_open`. Das `Game` merkt davon nichts, die `TetrisApp` ruft
während der Pause einfach `game.step()` nicht auf.

## Grober Ablauf

Nach dem Start übernimmt die Tk-Ereignisschleife. Sie ruft drei Callbacks der
`TetrisApp` auf, die sich über Timer (`root.after`) wieder anmelden.

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
    tick -->|"state = CLEARING"| anim
    key -->|"state = CLEARING"| anim
    anim -->|"nächster Schritt"| loop
    anim -->|"fertig: game.finish_clear()"| sched
    key --> loop
    key -->|"R / Neustart"| ng
```

### Detail: Spieltakt `tick()`

```mermaid
flowchart TD
    tick["TetrisApp.tick()"] --> paused{"Menü offen?"}
    paused -->|ja| tnext
    paused -->|nein| step["game.step()"]
    step --> down{"Platz darunter?"}
    down -->|ja| moved["Stein eine Zeile tiefer"]
    down -->|nein| lock["game.lock()<br/>board.place(piece)"]
    lock --> full{"board.full_rows()?"}
    full -->|nein| spawn["game.spawn()<br/>(kein Platz: GAME_OVER)"]
    full -->|ja| clearing["state = CLEARING"]
    moved --> upd
    spawn --> upd
    clearing --> upd["update()<br/>CLEARING: start_clear_animation()<br/>sonst: draw()"]
    upd --> tnext{"state = PLAYING?"}
    tnext -->|ja| sched["schedule()<br/>nächster tick()"]
    tnext -->|nein| none["kein neuer Takt"]
```

### Detail: Lösch-Animation `animate_clear()`

```mermaid
flowchart TD
    sca["start_clear_animation()<br/>Takt-Timer abbrechen,<br/>anim = ClearAnimation(...)"] --> anim
    anim["animate_clear()<br/>delay = anim.step()"] --> q{"delay?"}
    q -->|"70 ms: Blinkphase"| blink["anim.flash wechselt<br/>Reihen gefüllt / als Umriss"]
    q -->|"40 ms: Auflösephase"| wipe["anim.wiped += 1<br/>Renderer blendet Spalten<br/>von der Mitte aus aus"]
    blink --> again["draw()<br/>root.after(delay, animate_clear)"]
    wipe --> again
    q -->|"None: fertig"| fin["game.finish_clear()<br/>Reihen entfernen, Punkte und Level,<br/>spawn(), draw()"]
    fin -->|"state = PLAYING"| sched["schedule()<br/>Spieltakt läuft wieder"]
```

### Detail: Tastatur `on_key()`

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
    blocked -->|nein| act["← → game.move()<br/>↑ game.rotate()<br/>↓ game.soft_drop()<br/>Leer game.hard_drop()<br/>Esc / P menu.open()"]
    act --> kupd["update()"]
```

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
- **Leertaste:** `game.hard_drop()` lässt den Stein ganz nach unten fallen und
  ruft dann `lock()` auf, mit denselben Folgen wie im Spieltakt. Einen neuen
  Takt plant es nicht ein, der bestehende Timer läuft einfach weiter.
- **Programmende:** `root.destroy()` (Menüpunkt „Beenden“ oder Esc bei Game
  Over) schließt das Fenster, dadurch kehrt `mainloop()` zurück.
