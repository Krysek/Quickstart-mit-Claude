<!-- Automatisch erzeugt aus doc_templates/api/menu.md mit tools/gen_docs.py. Nicht von Hand bearbeiten. -->

# menu – Pausenmenü

[← Startseite der Dokumentation](../index.md)

<a id="menu"></a>

## Modul `menu`

Das Pausenmenü: welche Einträge es gibt und welcher ausgewählt ist.

Das Menü weiß nur, ob es offen ist und welcher Eintrag gewählt ist.
Gezeichnet wird es vom [`Renderer`](view.md#view-renderer), ausgeführt wird der
Eintrag von der [`TetrisApp`](app.md#quickstart_mit_claude-tetrisapp).

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py)

### Übersicht

| Name | Art | Beschreibung |
|---|---|---|
| [`PauseMenu`](#menu-pausemenu) | Klasse | Zustand des Pausenmenüs. |

<a id="menu-pausemenu"></a>

### Klasse `PauseMenu`

```python
class PauseMenu()
```

Zustand des Pausenmenüs.

**Attribute:**

| Name | Typ | Beschreibung |
|---|---|---|
| `ITEMS` | <code>tuple[str, ...]</code> | Die Einträge in der angezeigten Reihenfolge. |
| `is_open` | <code>bool</code> | True, solange das Menü angezeigt wird (das Spiel ist pausiert). |
| `index` | <code>int</code> | Index des ausgewählten Eintrags in `ITEMS`. |

Erzeugt ein geschlossenes Menü mit "Weiter" ausgewählt.

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py#L11-L47)

<a id="menu-pausemenu-selected"></a>

#### `selected` (Eigenschaft)

```python
selected: str
```

Der Text des ausgewählten Eintrags.

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py#L28-L30)

<a id="menu-pausemenu-open"></a>

#### `open()`

```python
def open() -> None
```

Öffnet das Menü mit "Weiter" ausgewählt.

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py#L32-L35)

<a id="menu-pausemenu-close"></a>

#### `close()`

```python
def close() -> None
```

Schließt das Menü.

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py#L37-L39)

<a id="menu-pausemenu-up"></a>

#### `up()`

```python
def up() -> None
```

Wählt den vorherigen Eintrag (vom ersten geht es zum letzten).

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py#L41-L43)

<a id="menu-pausemenu-down"></a>

#### `down()`

```python
def down() -> None
```

Wählt den nächsten Eintrag (vom letzten geht es zum ersten).

[Quelltext: `menu.py`](https://github.com/Krysek/Quickstart-mit-Claude/blob/main/Quickstart%20mit%20Claude/menu.py#L45-L47)
