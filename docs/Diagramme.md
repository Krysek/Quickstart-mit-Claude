# Tetris – Diagramme

Dokumentation zu `Quickstart mit Claude/Quickstart_mit_Claude.py`.
Die Diagramme sind in [Mermaid](https://mermaid.js.org/) geschrieben und werden
z. B. auf GitHub und in VS Code direkt als Grafik angezeigt.

## Klassendiagramm

```mermaid
classDiagram
    direction LR

    class Quickstart_mit_Claude {
        <<Modul>>
        +int COLS = 10
        +int ROWS = 20
        +int CELL = 30
        +int PANEL = 180
        +str BG = "black"
        +str FG = "white"
        +tuple FONT
        +tuple BIG_FONT
        +list SHAPES
        +list LINE_SCORES
        +list MENU_ITEMS
        +rotate(shape)$ list
        +main()$
    }

    class Tetris {
        +int BLINK_FRAMES = 6$
        +int WIPE_FRAMES = 5$
        +Tk root
        +Canvas canvas
        +list board
        +list shape
        +int x
        +int y
        +list next_shape
        +list bag
        +int score
        +int lines
        +int level
        +bool paused
        +int menu_index
        +bool game_over
        +list clearing
        +bool flash
        +int anim_frame
        +str job
        +str anim_job
        +#95;#95;init#95;#95;(root)
        +new_game()
        +take_from_bag() list
        +spawn()
        +collides(shape, x, y) bool
        +move(dx, dy) bool
        +rotate_piece()
        +hard_drop()
        +lock()
        +start_clear_animation(rows)
        +animate_clear()
        +finish_clear()
        +ghost_y() int
        +schedule()
        +tick()
        +on_key(event)
        +open_menu()
        +close_menu()
        +on_menu_key(key)
        +select_menu_item()
        +cell(c, r, size, ox, oy, ghost)
        +draw()
        +draw_menu()
    }

    class Tk {
        <<tkinter>>
        +after(ms, func) str
        +after_cancel(id)
        +bind(sequence, func)
        +mainloop()
        +destroy()
    }

    class Canvas {
        <<tkinter>>
        +create_rectangle(...)
        +create_text(...)
        +create_line(...)
        +delete(tag)
    }

    Quickstart_mit_Claude ..> Tetris : main() erzeugt
    Tetris ..> Quickstart_mit_Claude : nutzt rotate(), SHAPES, Konstanten
    Tetris --> Tk : root
    Tetris *-- Canvas : canvas
```

Das ganze Spiel steckt in einer Klasse. Ihre Methoden lassen sich in Gruppen
einteilen (wie die Abschnitte im Quelltext):

| Gruppe | Methoden |
|---|---|
| Spiellogik | `new_game`, `take_from_bag`, `spawn`, `collides`, `move`, `rotate_piece`, `hard_drop`, `lock` |
| Lösch-Animation | `start_clear_animation`, `animate_clear`, `finish_clear`, `ghost_y` |
| Zeitsteuerung und Eingabe | `schedule`, `tick`, `on_key` |
| Pausenmenü | `open_menu`, `close_menu`, `on_menu_key`, `select_menu_item` |
| Zeichnen | `cell`, `draw`, `draw_menu` |

`job` und `anim_job` enthalten die IDs der mit `root.after()` geplanten Timer
oder `None`, wenn gerade keiner geplant ist.

## Grober Ablauf

Übersicht: Nach dem Start übernimmt die Tk-Ereignisschleife. Sie ruft drei
Callbacks auf, die sich über Timer (`root.after`) gegenseitig wieder anmelden.

```mermaid
flowchart TD
    start(["Programmstart"]) --> main["main()<br/>root = tk.Tk()"]
    main --> init["Tetris.__init__()<br/>Canvas anlegen, on_key an Tasten binden"]
    init --> ng["new_game()<br/>Zustand zurücksetzen, ersten Stein erzeugen"]
    ng --> sched["schedule()<br/>root.after(delay, tick)"]
    sched --> loop{{"root.mainloop()<br/>Tk wartet auf Ereignisse"}}

    loop -->|"Takt-Timer"| tick["tick()<br/>Stein eine Zeile tiefer oder absetzen"]
    loop -->|"Taste"| key["on_key()<br/>bewegen, drehen, fallen lassen, Menü"]
    loop -->|"Animations-Timer"| anim["animate_clear()<br/>volle Reihen blinken und auflösen"]
    loop -->|"root.destroy()"| stop(["Programmende"])

    tick -->|"nächster Takt"| sched
    tick -->|"volle Reihen"| anim
    anim -->|"nächster Schritt"| loop
    anim -->|"fertig: finish_clear()"| sched
    key --> loop
    key -->|"R / Neustart"| ng
```

### Detail: Spieltakt `tick()`

```mermaid
flowchart TD
    tick["tick()"] --> tickq{"pausiert oder<br/>Game Over?"}
    tickq -->|ja| tnext
    tickq -->|nein| down{"move(0, 1)<br/>Platz darunter?"}
    down -->|ja| tdraw["draw()"]
    down -->|nein| lock["lock()<br/>Stein ins Spielfeld schreiben"]
    lock --> full{"volle Reihen?"}
    full -->|nein| spawn["spawn()<br/>nächster Stein<br/>(kein Platz: game_over)"]
    full -->|ja| sca["start_clear_animation()<br/>Takt-Timer abbrechen,<br/>animate_clear() starten"]
    spawn --> tdraw
    sca --> tdraw
    tdraw --> tnext{"Game Over oder<br/>Animation läuft?"}
    tnext -->|nein| sched["schedule()<br/>nächster tick()"]
    tnext -->|ja| none["kein neuer Takt"]
```

### Detail: Lösch-Animation `animate_clear()`

```mermaid
flowchart TD
    anim["animate_clear()"] --> q{"alle Schritte<br/>fertig?"}
    q -->|"nein, Blinkphase"| blink["Reihen gefüllt / als Umriss<br/>nächster Schritt in 70 ms"]
    q -->|"nein, Auflösephase"| wipe["je eine Spalte links und rechts<br/>der Mitte löschen<br/>nächster Schritt in 40 ms"]
    blink --> again["draw()<br/>root.after(..., animate_clear)"]
    wipe --> again
    q -->|ja| fin["finish_clear()<br/>Reihen entfernen, Punkte und Level,<br/>spawn(), draw()"]
    fin -->|"kein Game Over"| sched["schedule()<br/>Spieltakt läuft wieder"]
```

### Detail: Tastatur `on_key()`

```mermaid
flowchart TD
    key["on_key()"] --> paused{"Pausenmenü<br/>offen?"}
    paused -->|ja| menu["on_menu_key()"]
    menu --> m1["↑ ↓: Auswahl ändern"]
    menu --> m2["Enter / Leer: select_menu_item()<br/>Weiter · Neustart · Beenden"]
    menu --> m3["Esc / P: close_menu()"]
    paused -->|nein| r{"R?"}
    r -->|ja| ng["new_game()"]
    r -->|nein| blocked{"Game Over oder<br/>Animation läuft?"}
    blocked -->|"ja (Esc bei Game Over: destroy())"| ignore["Taste ignorieren"]
    blocked -->|nein| act["← → move()<br/>↑ rotate_piece()<br/>↓ move(0, 1), +1 Punkt<br/>Leer hard_drop() → lock()<br/>Esc / P open_menu()"]
    act --> kdraw["draw()"]
```

### Erläuterung

- **Keine eigene Schleife:** Die Endlosschleife ist `root.mainloop()`. Tk ruft
  von dort aus die Callbacks `tick()`, `on_key()` und `animate_clear()` auf.
- **Spieltakt:** `schedule()` meldet mit `root.after()` den nächsten `tick()`
  an, `tick()` ruft am Ende wieder `schedule()` auf. Die Wartezeit sinkt mit dem
  Level von 500 ms auf minimal 80 ms.
- **Pause:** `tick()` läuft weiter, bewegt aber den Stein nicht.
- **Lösch-Animation:** Solange sie läuft, ist der Spieltakt angehalten.
  `animate_clear()` plant sich selbst neu ein, bis `finish_clear()` den Takt
  wieder startet.
- **Leertaste:** `hard_drop()` lässt den Stein ganz nach unten fallen und ruft
  dann ebenfalls `lock()` auf, mit denselben Folgen wie im Spieltakt
  (nächster Stein oder Lösch-Animation). Einen neuen Takt plant es nicht ein,
  der bestehende Timer läuft einfach weiter.
- **Programmende:** `root.destroy()` (Menüpunkt „Beenden“ oder Esc bei Game
  Over) schließt das Fenster, dadurch kehrt `mainloop()` zurück.
