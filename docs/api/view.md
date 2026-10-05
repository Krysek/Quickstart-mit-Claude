<!-- Automatisch erzeugt aus doc_templates/api/view.md mit tools/gen_docs.py. Nicht von Hand bearbeiten. -->

# view – Zeichnen

[← Startseite der Dokumentation](../index.md)

<a id="view"></a>

## Modul `view`

Darstellung: Zeichnen auf dem tkinter-Canvas.

Der [`Renderer`](#view-renderer) liest nur den Zustand von
[`Game`](model.md#model-game), [`PauseMenu`](menu.md#menu-pausemenu) und
[`ClearAnimation`](animation.md#animation-clearanimation) und verändert ihn nie.

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py)

### Übersicht

| Name | Art | Beschreibung |
|---|---|---|
| [`Renderer`](#view-renderer) | Klasse | Zeichnet Spielfeld, Seitenleiste und Overlays auf einen Canvas. |

<a id="view-renderer"></a>

### Klasse `Renderer`

```python
class Renderer(root: tk.Misc, cols: int, rows: int)
```

Zeichnet Spielfeld, Seitenleiste und Overlays auf einen Canvas.

**Attribute:**

| Name | Typ | Beschreibung |
|---|---|---|
| `canvas` | <code>tk.Canvas</code> | Die tkinter-Zeichenfläche. |
| `width` | <code>int</code> | Breite des Spielfelds in Pixeln (ohne Seitenleiste). |
| `height` | <code>int</code> | Höhe des Spielfelds in Pixeln. |

Legt den Canvas passend zur Spielfeldgröße an.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `root` | <code>tk.Misc</code> | erforderlich | Das tkinter-Fenster, in das der Canvas kommt. |
| `cols` | <code>int</code> | erforderlich | Breite des Spielfelds in Zellen. |
| `rows` | <code>int</code> | erforderlich | Höhe des Spielfelds in Zellen. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L41-L195)

<a id="view-renderer-cell"></a>

#### `cell()`

```python
def cell(
    c: int,
    r: int,
    size: int = CELL,
    ox: int = 0,
    oy: int = 0,
    ghost: bool = False,
) -> None
```

Zeichnet eine einzelne Zelle.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `c` | <code>int</code> | erforderlich | Spalte der Zelle. |
| `r` | <code>int</code> | erforderlich | Zeile der Zelle. |
| `size` | <code>int</code> | <code>CELL</code> | Kantenlänge der Zelle in Pixeln. |
| `ox` | <code>int</code> | <code>0</code> | Horizontaler Versatz in Pixeln (z. B. für die Vorschau). |
| `oy` | <code>int</code> | <code>0</code> | Vertikaler Versatz in Pixeln. |
| `ghost` | <code>bool</code> | <code>False</code> | True zeichnet nur einen Umriss statt eines gefüllten Blocks. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L64-L80)

<a id="view-renderer-draw"></a>

#### `draw()`

```python
def draw(
    game: Game,
    menu: PauseMenu,
    anim: ClearAnimation | None = None,
) -> None
```

Zeichnet das komplette Fenster neu.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `game` | <code>Game</code> | erforderlich | Das Spiel, dessen Zustand gezeigt wird. |
| `menu` | <code>PauseMenu</code> | erforderlich | Das Pausenmenü; ist es offen, wird es darübergelegt. |
| `anim` | <code>ClearAnimation &#124; None</code> | <code>None</code> | Die laufende Lösch-Animation oder None. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L82-L97)

<a id="view-renderer-draw_board"></a>

#### `draw_board()`

```python
def draw_board(game: Game, anim: ClearAnimation | None) -> None
```

Zeichnet abgesetzte Blöcke, fallenden Stein und dessen Landeposition.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `game` | <code>Game</code> | erforderlich | Das Spiel, dessen Spielfeld gezeigt wird. |
| `anim` | <code>ClearAnimation &#124; None</code> | erforderlich | Die laufende Lösch-Animation oder None. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L99-L123)

<a id="view-renderer-draw_panel"></a>

#### `draw_panel()`

```python
def draw_panel(game: Game) -> None
```

Zeichnet die Seitenleiste: Vorschau, Punkte und Tastenbelegung.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `game` | <code>Game</code> | erforderlich | Das Spiel, dessen Werte gezeigt werden. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L125-L145)

<a id="view-renderer-draw_game_over"></a>

#### `draw_game_over()`

```python
def draw_game_over() -> None
```

Zeichnet den Game-Over-Hinweis mittig über das Spielfeld.

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L147-L155)

<a id="view-renderer-draw_menu"></a>

#### `draw_menu()`

```python
def draw_menu(menu: PauseMenu) -> None
```

Zeichnet das Pausenmenü mittig über das Spielfeld.

Der ausgewählte Eintrag wird invertiert dargestellt (schwarze Schrift
auf weißem Balken), die übrigen weiß auf schwarz.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `menu` | <code>PauseMenu</code> | erforderlich | Das Pausenmenü mit dem ausgewählten Eintrag. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L157-L181)

<a id="view-renderer-draw_overlay_box"></a>

#### `draw_overlay_box()`

```python
def draw_overlay_box(half_height: int) -> None
```

Zeichnet einen gerahmten Kasten mittig über das Spielfeld.

Der Kasten verdeckt das Spielfeld darunter; Game Over und Pausenmenü
schreiben ihren Text hinein.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `half_height` | <code>int</code> | erforderlich | Halbe Höhe des Kastens in Pixeln. |

[Quelltext: `view.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/view.py#L183-L195)
