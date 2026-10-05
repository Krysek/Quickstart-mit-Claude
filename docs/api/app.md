<!-- Automatisch erzeugt aus doc_templates/api/app.md mit tools/gen_docs.py. Nicht von Hand bearbeiten. -->

# TetrisApp – Steuerung

[← Startseite der Dokumentation](../index.md)

Die `TetrisApp` hat keine eigene Spielschleife. Die Ereignisschleife von
tkinter ruft ihre Callbacks auf:

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

## Spieltakt

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

So arbeiten die Objekte zusammen, wenn ein Stein Reihen füllt:

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

## Tastatur

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

<a id="quickstart_mit_claude"></a>

## Modul `Quickstart_mit_Claude`

Einfaches Tetris in Schwarz/Weiß mit tkinter.

Das Spiel läuft in einem eigenen Fenster. Links liegt das Spielfeld
(10 x 20 Zellen), rechts eine Seitenleiste mit Vorschau auf den nächsten
Stein, Punktestand, gelöschten Reihen, Level und Tastenbelegung.

> **Aufbau**
>
> - `model.py`: Spielregeln (`Piece`, `Board`, `Bag`, `Game`), ohne tkinter
> - `menu.py`: Zustand des Pausenmenüs (`PauseMenu`), ohne tkinter
> - `animation.py`: Lösch-Animation (`ClearAnimation`), ohne tkinter
> - `view.py`: Zeichnen auf dem Canvas (`Renderer`)
> - `Quickstart_mit_Claude.py`: verbindet alles, Tastatur und Timer (`TetrisApp`)

> **Steuerung**
>
> - Pfeil links/rechts: Stein bewegen
> - Pfeil hoch: Stein drehen
> - Pfeil runter: Stein schneller fallen lassen (+1 Punkt pro Zeile)
> - Leertaste: Stein sofort fallen lassen (+2 Punkte pro Zeile)
> - Esc oder P: Pausenmenü öffnen/schließen
> - Esc bei Game Over: Beenden
> - R: Neues Spiel

> **Im Pausenmenü**
>
> - Pfeil hoch/runter: Eintrag wählen (Weiter, Neustart, Beenden)
> - Enter oder Leertaste: Eintrag ausführen

> **Start**
>
> `python Quickstart_mit_Claude.py`

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py)

### Übersicht

| Name | Art | Beschreibung |
|---|---|---|
| [`TetrisApp`](#quickstart_mit_claude-tetrisapp) | Klasse | Verbindet Spiel, Menü und Darstellung mit tkinter. |
| [`main`](#quickstart_mit_claude-main) | Funktion | Öffnet das Spielfenster und startet die tkinter-Ereignisschleife. |

<a id="quickstart_mit_claude-tetrisapp"></a>

### Klasse `TetrisApp`

```python
class TetrisApp(
    root: tk.Tk,
    cols: int = COLS,
    rows: int = ROWS,
    renderer: Renderer | None = None,
    menu: PauseMenu | None = None,
)
```

Verbindet Spiel, Menü und Darstellung mit tkinter.

Es gibt keine eigene Spielschleife: `root.mainloop()` ruft `on_key()`
bei Tastendrücken auf, und über `root.after` laufen zwei Timer: `tick()`
für den Spieltakt und `animate_clear()` für die Lösch-Animation.
Während der Animation ist der Spieltakt angehalten.

**Attribute:**

| Name | Typ | Beschreibung |
|---|---|---|
| `root` | <code>tk.Tk</code> | Das tkinter-Hauptfenster. |
| `cols` | <code>int</code> | Breite des Spielfelds in Zellen, für Spiel und Darstellung. |
| `rows` | <code>int</code> | Höhe des Spielfelds in Zellen, für Spiel und Darstellung. |
| `renderer` | <code>Renderer</code> | Zeichnet den Zustand auf den Canvas. |
| `menu` | <code>PauseMenu</code> | Das Pausenmenü. |

Baut das Fenster auf und startet das erste Spiel.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `root` | <code>tk.Tk</code> | erforderlich | Das tkinter-Hauptfenster, in dem das Spiel läuft. |
| `cols` | <code>int</code> | <code>COLS</code> | Breite des Spielfelds in Zellen. |
| `rows` | <code>int</code> | <code>ROWS</code> | Höhe des Spielfelds in Zellen. |
| `renderer` | <code>Renderer &#124; None</code> | <code>None</code> | Zeichnet den Zustand; ohne Angabe einer für `root` mit `cols` x `rows` Zellen. |
| `menu` | <code>PauseMenu &#124; None</code> | <code>None</code> | Das Pausenmenü; ohne Angabe ein neues, geschlossenes. |

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L39-L254)

<a id="quickstart_mit_claude-tetrisapp-new_game"></a>

#### `new_game()`

```python
def new_game() -> None
```

Startet ein neues Spiel.

Bricht dabei einen laufenden Spieltakt und eine laufende
Lösch-Animation ab, damit nach einem Neustart keine alten
Zeitgeber weiterlaufen.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L83-L95)

<a id="quickstart_mit_claude-tetrisapp-cancel_tick"></a>

#### `cancel_tick()`

```python
def cancel_tick() -> None
```

Bricht den geplanten Spieltakt ab, falls es einen gibt.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L97-L101)

<a id="quickstart_mit_claude-tetrisapp-cancel_timers"></a>

#### `cancel_timers()`

```python
def cancel_timers() -> None
```

Bricht Spieltakt und Animationsschritt ab, falls geplant.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L103-L108)

<a id="quickstart_mit_claude-tetrisapp-draw"></a>

#### `draw()`

```python
def draw() -> None
```

Zeichnet den aktuellen Zustand neu.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L110-L112)

<a id="quickstart_mit_claude-tetrisapp-schedule"></a>

#### `schedule()`

```python
def schedule() -> None
```

Plant den nächsten Spieltakt ein (Wartezeit je nach Level).

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L116-L118)

<a id="quickstart_mit_claude-tetrisapp-tick"></a>

#### `tick()`

```python
def tick() -> None
```

Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt.

Während einer Pause passiert nichts, der Takt läuft aber weiter.
Bei Game Over oder während der Lösch-Animation wird kein neuer Takt
geplant.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L120-L134)

<a id="quickstart_mit_claude-tetrisapp-start_clear_animation"></a>

#### `start_clear_animation()`

```python
def start_clear_animation() -> None
```

Hält den Spieltakt an und startet die Animation für volle Reihen.

Wird aufgerufen, wenn [`Game.step`](model.md#model-game-step) oder
[`Game.hard_drop`](model.md#model-game-hard_drop) meldet, dass Reihen voll sind.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L138-L146)

<a id="quickstart_mit_claude-tetrisapp-animate_clear"></a>

#### `animate_clear()`

```python
def animate_clear() -> None
```

Zeigt einen Schritt der Lösch-Animation und plant den nächsten.

Ist die Animation vorbei, werden die Reihen entfernt und der
Spieltakt läuft wieder an.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L148-L165)

<a id="quickstart_mit_claude-tetrisapp-on_key"></a>

#### `on_key()`

```python
def on_key(event: tk.Event) -> None
```

Reagiert auf Tastendrücke (Belegung siehe Modul-Docstring).

Ist das Pausenmenü offen, gehen alle Tasten an `on_menu_key()`, im
laufenden Spiel an `on_game_key()`. R funktioniert immer, bei Game
Over beendet Esc das Programm. Während der Lösch-Animation sind alle
Tasten außer R gesperrt.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `event` | <code>tk.Event</code> | erforderlich | Das tkinter-Tastaturereignis. |

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L169-L191)

<a id="quickstart_mit_claude-tetrisapp-on_game_key"></a>

#### `on_game_key()`

```python
def on_game_key(key: str) -> None
```

Verarbeitet Tastendrücke im laufenden Spiel.

Esc und P öffnen das Pausenmenü, die Pfeiltasten bewegen und drehen
den Stein, die Leertaste lässt ihn sofort fallen.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `key` | <code>str</code> | erforderlich | Name der gedrückten Taste in Kleinbuchstaben (tkinter-keysym). |

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L193-L217)

<a id="quickstart_mit_claude-tetrisapp-on_menu_key"></a>

#### `on_menu_key()`

```python
def on_menu_key(key: str) -> None
```

Verarbeitet Tastendrücke, solange das Pausenmenü offen ist.

Pfeil hoch/runter wechseln den Eintrag (am Ende geht es oben weiter),
Enter oder Leertaste führen ihn aus. Esc und P schließen das Menü,
R startet direkt neu.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `key` | <code>str</code> | erforderlich | Name der gedrückten Taste in Kleinbuchstaben (tkinter-keysym). |

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L219-L243)

<a id="quickstart_mit_claude-tetrisapp-select_menu_item"></a>

#### `select_menu_item()`

```python
def select_menu_item() -> None
```

Führt den ausgewählten Menüeintrag aus: Weiter, Neustart oder Beenden.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L245-L254)

<a id="quickstart_mit_claude-main"></a>

### `main()`

```python
def main() -> None
```

Öffnet das Spielfenster und startet die tkinter-Ereignisschleife.

[Quelltext: `Quickstart_mit_Claude.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/Quickstart_mit_Claude.py#L257-L261)
