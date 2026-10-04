# 🧱 Tetris in Schwarz/Weiß

Ein schlichtes, vollständig spielbares **Tetris** in Python – ohne externe
Abhängigkeiten. Gezeichnet wird mit `tkinter`, das bei
Python schon dabei ist.

Entstanden als Quickstart-Projekt zum Programmieren mit
[Claude](https://claude.com/claude-code).

```
┌────────────────────┬────────────────┐
│                    │ NÄCHSTER       │
│          ██        │     ██         │
│        ██████      │ ██████         │
│                    │                │
│                    │ PUNKTE         │
│          ┌┐        │ 1240           │
│        ┌┐┌┐┌┐      │                │
│██    ████████  ██  │ REIHEN  7      │
│██████████████  ████│                │
│██  ████████████████│ LEVEL   1      │
└────────────────────┴────────────────┘
```

## ✨ Features

- Klassisches Spielfeld mit **10 × 20** Zellen und allen **sieben Tetrominos**
- **Ghost-Stein**: Ein Umriss zeigt, wo der aktuelle Stein landen wird
- **Vorschau** auf den nächsten Stein
- **7er-Beutel**: Jeder Stein kommt pro Runde genau einmal vor – keine
  endlosen Durststrecken ohne den langen I-Stein
- **Wall Kick**: Steine lassen sich auch direkt an der Wand drehen
- **Animation** beim Löschen voller Reihen (Blinken, dann Auflösen von der Mitte
  nach außen)
- **Level-System**: Alle 10 Reihen steigt das Level, und die Steine fallen schneller
- **Pausenmenü** mit *Weiter*, *Neustart* und *Beenden*
- Komplett auf Deutsch, durchgehend mit Docstrings kommentiert
- Spiellogik getrennt von der Oberfläche und mit **Unit-Tests** abgesichert

## 🚀 Starten

Voraussetzung ist **Python 3** mit `tkinter`.

```bash
git clone https://github.com/Krysek/Quickstart-mit-Claude.git
cd Quickstart-mit-Claude
python "Quickstart mit Claude/Quickstart_mit_Claude.py"
```

> **Hinweis:** Unter Windows und macOS ist `tkinter` in der Regel schon
> installiert. Unter Linux muss es eventuell nachinstalliert werden, z. B. mit
> `sudo apt install python3-tk`.

Alternativ lässt sich die Projektmappe `Quickstart mit Claude.sln` in
**Visual Studio** öffnen und dort mit <kbd>F5</kbd> starten.

## 🧪 Tests

Die Tests nutzen nur `unittest` aus der Standardbibliothek:

```bash
cd "Quickstart mit Claude"
python -m unittest -v
```

## 🎮 Steuerung

| Taste | Aktion |
|---|---|
| <kbd>←</kbd> <kbd>→</kbd> | Stein bewegen |
| <kbd>↑</kbd> | Stein drehen |
| <kbd>↓</kbd> | Schneller fallen lassen |
| <kbd>Leertaste</kbd> | Sofort fallen lassen |
| <kbd>Esc</kbd> / <kbd>P</kbd> | Pausenmenü öffnen/schließen |
| <kbd>R</kbd> | Neues Spiel |
| <kbd>Esc</kbd> bei Game Over | Beenden |

**Im Pausenmenü:** <kbd>↑</kbd> <kbd>↓</kbd> wählen einen Eintrag,
<kbd>Enter</kbd> oder <kbd>Leertaste</kbd> führen ihn aus.

## 🏆 Punkte

| Aktion | Punkte |
|---|---|
| 1 Reihe | 100 × Level |
| 2 Reihen | 300 × Level |
| 3 Reihen | 500 × Level |
| 4 Reihen (Tetris!) | 800 × Level |
| Schnell fallen lassen (<kbd>↓</kbd>) | 1 pro Zeile |
| Sofort fallen lassen (<kbd>Leertaste</kbd>) | 2 pro Zeile |

Das Spiel startet mit 500 ms pro Zeile. Mit jedem Level wird es 45 ms schneller,
bis zum Minimum von 80 ms.

## 📁 Projektstruktur

```
.
├── Quickstart mit Claude/
│   ├── Quickstart_mit_Claude.py    # Startpunkt: TetrisApp (Tastatur, Timer)
│   ├── model.py                    # Spielregeln: Piece, Board, Bag, Game
│   ├── menu.py                     # Pausenmenü: PauseMenu
│   ├── view.py                     # Zeichnen: Renderer, ClearAnimation
│   ├── test_tetris.py              # Unit-Tests
│   └── Quickstart mit Claude.pyproj
├── docs/
│   └── Diagramme.md                # Klassen- und Ablaufdiagramme (Mermaid)
└── Quickstart mit Claude.sln       # Visual-Studio-Projektmappe
```

## 🔍 Wie es funktioniert

Das Spiel ist in Logik und Oberfläche aufgeteilt:

| Klasse | Modul | Aufgabe |
|---|---|---|
| `Piece` | `model.py` | Ein Stein: Form und Position, verschieben und drehen |
| `Board` | `model.py` | Das Spielfeld: Kollisionen, Steine absetzen, volle Reihen |
| `Bag` | `model.py` | Der 7er-Beutel für die nächsten Steine |
| `Game` | `model.py` | Die Regeln: Punkte, Level, Zustand (`GameState`) |
| `PauseMenu` | `menu.py` | Einträge und Auswahl des Pausenmenüs |
| `ClearAnimation` | `view.py` | Fortschritt der Lösch-Animation |
| `Renderer` | `view.py` | Zeichnet alles auf den tkinter-Canvas |
| `TetrisApp` | `Quickstart_mit_Claude.py` | Verbindet alles: Tastatur und Timer |

`model.py` und `menu.py` kennen kein tkinter. Deshalb lassen sie sich ohne
Fenster testen.

Es gibt keine eigene Spielschleife: `root.mainloop()` von tkinter wartet auf
Ereignisse und ruft in der `TetrisApp` drei Callbacks auf:

- `tick()` – der Spieltakt, lässt den Stein eine Zeile fallen
- `on_key()` – verarbeitet die Tastatureingaben
- `animate_clear()` – spielt die Animation beim Löschen von Reihen ab

Ausführliche Klassen- und Ablaufdiagramme gibt es in
[`docs/Diagramme.md`](docs/Diagramme.md).

## ⚙️ Anpassen

Größe und Aussehen lassen sich über Konstanten ändern, die Spielfeldgröße in
`model.py` und das Aussehen in `view.py`:

```python
COLS, ROWS = 10, 20          # model.py: Größe des Spielfelds in Zellen

CELL = 30                    # view.py: Kantenlänge einer Zelle in Pixeln
PANEL = 180                  # Breite der Seitenleiste in Pixeln
BG, FG = "black", "white"    # Hintergrund- und Vordergrundfarbe
```

Wer es bunt mag, setzt z. B. `BG, FG = "navy", "gold"`.
