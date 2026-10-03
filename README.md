# 🧱 Tetris in Schwarz/Weiß

Ein schlichtes, vollständig spielbares **Tetris** in Python – in einer einzigen
Datei, ohne externe Abhängigkeiten. Gezeichnet wird mit `tkinter`, das bei
Python schon dabei ist.

Entstanden als Quickstart-Projekt zum Programmieren mit
[Claude](https://claude.com/claude-code).

```
┌──────────────────────────────┬──────────────────┐
│                              │ NÄCHSTER         │
│            ██                │  ██              │
│          ██████              │ ██████           │
│                              │                  │
│                              │ PUNKTE           │
│            ┌┐                │ 1240             │
│          ┌┐┌┐┌┐              │                  │
│  ██    ██████████    ██  ██  │ REIHEN           │
│  ████████████████  ██████████│ 7                │
│  ████████████████████  ██████│                  │
│  ██████████████████████████  │ LEVEL            │
│                              │ 1                │
└──────────────────────────────┴──────────────────┘
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
│   ├── Quickstart_mit_Claude.py    # das komplette Spiel
│   └── Quickstart mit Claude.pyproj
├── docs/
│   └── Diagramme.md                # Klassen- und Ablaufdiagramme (Mermaid)
└── Quickstart mit Claude.sln       # Visual-Studio-Projektmappe
```

## 🔍 Wie es funktioniert

Das ganze Spiel steckt in der Klasse `Tetris`. Es gibt keine eigene
Spielschleife: `root.mainloop()` von tkinter wartet auf Ereignisse und ruft drei
Callbacks auf, die sich über Timer (`root.after`) immer wieder selbst anmelden:

- `tick()` – der Spieltakt, lässt den Stein eine Zeile fallen
- `on_key()` – verarbeitet die Tastatureingaben
- `animate_clear()` – spielt die Animation beim Löschen von Reihen ab

Ausführliche Klassen- und Ablaufdiagramme gibt es in
[`docs/Diagramme.md`](docs/Diagramme.md).

## ⚙️ Anpassen

Größe und Aussehen lassen sich über die Konstanten am Anfang der Datei ändern:

```python
COLS, ROWS = 10, 20          # Größe des Spielfelds in Zellen
CELL = 30                    # Kantenlänge einer Zelle in Pixeln
PANEL = 180                  # Breite der Seitenleiste in Pixeln
BG, FG = "black", "white"    # Hintergrund- und Vordergrundfarbe
```

Wer es bunt mag, setzt z. B. `BG, FG = "navy", "gold"`.
