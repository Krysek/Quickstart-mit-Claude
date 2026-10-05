<!-- Automatisch erzeugt aus doc_templates/api/model.md mit tools/gen_docs.py. Nicht von Hand bearbeiten. -->

# model – Spielregeln

[← Startseite der Dokumentation](../index.md)

Die komplette Spiellogik, ohne tkinter. Ein `Game` durchläuft diese Zustände:

```mermaid
stateDiagram-v2
    [*] --> PLAYING : Game()
    PLAYING --> CLEARING : lock() mit vollen Reihen
    CLEARING --> PLAYING : finish_clear()
    PLAYING --> GAME_OVER : spawn() ohne Platz
    CLEARING --> GAME_OVER : finish_clear() → spawn() ohne Platz
    GAME_OVER --> [*]
```

<a id="model"></a>

## Modul `model`

Spiellogik von Tetris, unabhängig von der Oberfläche.

Dieses Modul kennt kein tkinter. Es enthält nur die Regeln: Steine, Spielfeld,
7er-Beutel und den Spielablauf mit Punkten und Level. Dadurch lässt es sich
ohne Fenster testen (siehe `test_tetris.py`).

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py)

### Übersicht

| Name | Art | Beschreibung |
|---|---|---|
| [`Shape`](#model-shape) | Typ-Alias | Form eines Steins als quadratische Matrix: 1 = Block, 0 = leer. |
| [`Piece`](#model-piece) | Klasse | Ein Stein: eine Form an einer Position im Spielfeld. |
| [`Board`](#model-board) | Klasse | Das Spielfeld mit den bereits abgesetzten Blöcken. |
| [`Bag`](#model-bag) | Klasse | Der 7er-Beutel, aus dem die Steine gezogen werden. |
| [`GameState`](#model-gamestate) | Aufzählung | Zustand des Spiels. |
| [`Game`](#model-game) | Klasse | Ein Tetris-Spiel: Spielfeld, fallender Stein, Punkte und Level. |

<a id="model-shape"></a>

### `Shape`

```python
Shape: TypeAlias = tuple[tuple[int, ...], ...]
```

Form eines Steins als quadratische Matrix: 1 = Block, 0 = leer.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L14-L14)

<a id="model-piece"></a>

### Klasse `Piece`

```python
@dataclass(frozen=True)
class Piece(shape: Shape, x: int = 0, y: int = 0)
```

Ein Stein: eine Form an einer Position im Spielfeld.

Ein `Piece` ist unveränderlich. [`moved`](#model-piece-moved) und
[`rotated`](#model-piece-rotated) liefern neue Steine, sodass man eine
Bewegung erst ausprobieren und dann übernehmen kann.

**Attribute:**

| Name | Typ | Beschreibung |
|---|---|---|
| `shape` | <code>Shape</code> | Form des Steins (siehe [`Shape`](#model-shape)). |
| `x` | <code>int</code> | Spalte der linken oberen Ecke von `shape`. |
| `y` | <code>int</code> | Zeile der linken oberen Ecke von `shape`. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L48-L88)

<a id="model-piece-cells"></a>

#### `cells()`

```python
def cells() -> Iterator[tuple[int, int]]
```

Liefert die belegten Zellen des Steins im Spielfeld.

**Liefert:**

| Typ | Beschreibung |
|---|---|
| <code>tuple[int, int]</code> | Paare `(spalte, zeile)` für jeden Block des Steins. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L66-L75)

<a id="model-piece-moved"></a>

#### `moved()`

```python
def moved(dx: int, dy: int) -> Piece
```

Gibt einen um `dx` Spalten und `dy` Zeilen verschobenen Stein zurück.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `dx` | <code>int</code> | erforderlich | Verschiebung in Spalten (negativ = nach links). |
| `dy` | <code>int</code> | erforderlich | Verschiebung in Zeilen (positiv = nach unten). |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L77-L84)

<a id="model-piece-rotated"></a>

#### `rotated()`

```python
def rotated() -> Piece
```

Gibt den um 90° im Uhrzeigersinn gedrehten Stein zurück.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L86-L88)

<a id="model-board"></a>

### Klasse `Board`

```python
class Board(cols: int = COLS, rows: int = ROWS)
```

Das Spielfeld mit den bereits abgesetzten Blöcken.

**Attribute:**

| Name | Typ | Beschreibung |
|---|---|---|
| `cols` | <code>int</code> | Breite in Zellen. |
| `rows` | <code>int</code> | Höhe in Zellen. |

Erzeugt ein leeres Spielfeld.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `cols` | <code>int</code> | <code>COLS</code> | Breite in Zellen. |
| `rows` | <code>int</code> | <code>ROWS</code> | Höhe in Zellen. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L91-L156)

<a id="model-board-grid"></a>

#### `grid` (Eigenschaft)

```python
grid: tuple[tuple[int, ...], ...]
```

Schreibgeschützte Kopie des Spielfelds: `grid[zeile][spalte]`, 1 = belegt.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L111-L113)

<a id="model-board-collides"></a>

#### `collides()`

```python
def collides(piece: Piece) -> bool
```

Prüft, ob ein Stein an seiner Position keinen Platz hätte.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `piece` | <code>Piece</code> | erforderlich | Der zu prüfende Stein. |

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn ein Block links, rechts oder unten aus dem Spielfeld ragt oder ein belegtes Feld überdeckt, sonst False. Oben darf der Stein über das Spielfeld hinausragen. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L115-L131)

<a id="model-board-place"></a>

#### `place()`

```python
def place(piece: Piece) -> None
```

Trägt einen Stein fest ins Spielfeld ein (Teile oberhalb entfallen).

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `piece` | <code>Piece</code> | erforderlich | Der abzusetzende Stein. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L133-L141)

<a id="model-board-full_rows"></a>

#### `full_rows()`

```python
def full_rows() -> list[int]
```

Gibt die Zeilennummern aller vollständig belegten Reihen zurück.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L143-L145)

<a id="model-board-remove_rows"></a>

#### `remove_rows()`

```python
def remove_rows(rows: list[int]) -> None
```

Entfernt die angegebenen Reihen; darüberliegende rutschen nach.

Oben kommen entsprechend viele leere Reihen dazu.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `rows` | <code>list[int]</code> | erforderlich | Zeilennummern der zu entfernenden Reihen. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L147-L156)

<a id="model-bag"></a>

### Klasse `Bag`

```python
class Bag(shapes: Sequence[Shape] = SHAPES, rng: random.Random | None = None)
```

Der 7er-Beutel, aus dem die Steine gezogen werden.

Jede Form kommt pro Runde genau einmal vor, in zufälliger Reihenfolge.
So gibt es keine langen Durststrecken ohne einen bestimmten Stein.

Erzeugt einen leeren Beutel; er wird beim ersten Ziehen gefüllt.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `shapes` | <code>Sequence[Shape]</code> | <code>SHAPES</code> | Die Formen, die der Beutel enthält. |
| `rng` | <code>random.Random &#124; None</code> | <code>None</code> | Zufallsgenerator (z. B. `random.Random(42)` für Tests). |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L159-L184)

<a id="model-bag-take"></a>

#### `take()`

```python
def take() -> Shape
```

Zieht die nächste Form; ein leerer Beutel wird neu gefüllt und gemischt.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L179-L184)

<a id="model-gamestate"></a>

### Klasse `GameState`

```python
class GameState(Enum)
```

Zustand des Spiels.

**Werte:**

| Name | Bedeutung |
|---|---|
| `PLAYING` | Ein Stein fällt. |
| `CLEARING` | Volle Reihen warten auf [`finish_clear`](#model-game-finish_clear). |
| `GAME_OVER` | Ein neuer Stein hatte keinen Platz mehr. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L187-L195)

<a id="model-game"></a>

### Klasse `Game`

```python
class Game(board: Board | None = None, bag: Bag | None = None)
```

Ein Tetris-Spiel: Spielfeld, fallender Stein, Punkte und Level.

Alle Aktionen ([`move`](#model-game-move), [`rotate`](#model-game-rotate),
[`soft_drop`](#model-game-soft_drop), [`hard_drop`](#model-game-hard_drop),
[`step`](#model-game-step)) wirken nur im Zustand `PLAYING`.

Setzt ein Stein auf und füllt dabei Reihen, wechselt das Spiel in den
Zustand `CLEARING` und merkt sich die Reihen in `clearing`. Erst
[`finish_clear`](#model-game-finish_clear) entfernt sie. Dazwischen kann
die Oberfläche eine Animation abspielen.

Der Spielzustand ist nur lesbar (Properties); ändern lässt er sich
ausschließlich über die Aktionen, damit die Regeln immer gelten.

Startet ein neues Spiel mit dem ersten Stein.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `board` | <code>Board &#124; None</code> | <code>None</code> | Das Spielfeld; ohne Angabe ein leeres mit `COLS` x `ROWS` Zellen. |
| `bag` | <code>Bag &#124; None</code> | <code>None</code> | Der 7er-Beutel; ohne Angabe einer mit zufälliger Reihenfolge (für Tests z. B. `Bag(rng=random.Random(0))`). |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L198-L411)

<a id="model-game-board"></a>

#### `board` (Eigenschaft)

```python
board: Board
```

Das Spielfeld.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L233-L235)

<a id="model-game-piece"></a>

#### `piece` (Eigenschaft)

```python
piece: Piece
```

Der aktuell fallende Stein.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L238-L240)

<a id="model-game-next_shape"></a>

#### `next_shape` (Eigenschaft)

```python
next_shape: Shape
```

Form des nächsten Steins (für die Vorschau).

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L243-L245)

<a id="model-game-score"></a>

#### `score` (Eigenschaft)

```python
score: int
```

Punktestand.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L248-L250)

<a id="model-game-lines"></a>

#### `lines` (Eigenschaft)

```python
lines: int
```

Anzahl der bisher gelöschten Reihen.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L253-L255)

<a id="model-game-level"></a>

#### `level` (Eigenschaft)

```python
level: int
```

Aktuelles Level (steigt alle `LINES_PER_LEVEL` Reihen).

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L258-L260)

<a id="model-game-state"></a>

#### `state` (Eigenschaft)

```python
state: GameState
```

Der aktuelle [`GameState`](#model-gamestate).

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L263-L265)

<a id="model-game-clearing"></a>

#### `clearing` (Eigenschaft)

```python
clearing: list[int]
```

Zeilennummern der vollen Reihen im Zustand `CLEARING` (als Kopie).

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L268-L270)

<a id="model-game-tick_delay"></a>

#### `tick_delay` (Eigenschaft)

```python
tick_delay: int
```

Wartezeit zwischen zwei Spieltakten in ms.

Beginnt bei 500 ms und sinkt pro Level um 45 ms, aber nie unter 80 ms.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L273-L278)

<a id="model-game-spawn"></a>

#### `spawn()`

```python
def spawn() -> None
```

Lässt den nächsten Stein oben in der Mitte erscheinen.

Ist dort kein Platz mehr, wechselt das Spiel zu `GAME_OVER`.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L286-L293)

<a id="model-game-move"></a>

#### `move()`

```python
def move(dx: int, dy: int) -> bool
```

Verschiebt den fallenden Stein, falls dort Platz ist.

**Parameter:**

| Name | Typ | Standard | Beschreibung |
|---|---|---|---|
| `dx` | <code>int</code> | erforderlich | Verschiebung in Spalten (-1 = links, 1 = rechts). |
| `dy` | <code>int</code> | erforderlich | Verschiebung in Zeilen (1 = nach unten). |

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn der Stein verschoben wurde, sonst False. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L302-L312)

<a id="model-game-rotate"></a>

#### `rotate()`

```python
def rotate() -> bool
```

Dreht den fallenden Stein im Uhrzeigersinn, wenn möglich.

Passt der gedrehte Stein nicht an seine Stelle (z. B. direkt an der
Wand), wird er testweise bis zu zwei Spalten nach links oder rechts
versetzt ("Wall Kick"). Klappt keine Variante, bleibt er unverändert.

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn der Stein gedreht wurde, sonst False. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L314-L328)

<a id="model-game-soft_drop"></a>

#### `soft_drop()`

```python
def soft_drop() -> bool
```

Lässt den Stein eine Zeile fallen und gibt dafür 1 Punkt.

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn der Stein gefallen ist, sonst False. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L330-L339)

<a id="model-game-hard_drop"></a>

#### `hard_drop()`

```python
def hard_drop() -> bool
```

Lässt den Stein sofort ganz nach unten fallen und setzt ihn ab.

Gibt 2 Punkte pro übersprungener Zeile.

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn dadurch Reihen voll sind (siehe [`lock`](#model-game-lock)). |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L341-L354)

<a id="model-game-step"></a>

#### `step()`

```python
def step() -> bool
```

Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt.

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn der Stein abgesetzt wurde und dadurch Reihen voll sind (siehe [`lock`](#model-game-lock)). |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L356-L365)

<a id="model-game-lock"></a>

#### `lock()`

```python
def lock() -> bool
```

Setzt den fallenden Stein fest ins Spielfeld.

Sind dadurch Reihen voll, wechselt das Spiel zu `CLEARING`.
Andernfalls erscheint direkt der nächste Stein.

**Rückgabe:**

| Typ | Beschreibung |
|---|---|
| <code>bool</code> | True, wenn Reihen voll sind und auf [`finish_clear`](#model-game-finish_clear) warten. |

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L367-L384)

<a id="model-game-finish_clear"></a>

#### `finish_clear()`

```python
def finish_clear() -> None
```

Entfernt die vollen Reihen und setzt das Spiel fort.

Aktualisiert Punkte, Reihenzahl und Level und lässt den nächsten
Stein erscheinen.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L386-L401)

<a id="model-game-ghost"></a>

#### `ghost()`

```python
def ghost() -> Piece
```

Gibt den Stein an der Position zurück, an der er landen würde.

Wird für den Umriss ("Ghost") genutzt, der die Landeposition anzeigt.

[Quelltext: `model.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/model.py#L403-L411)
