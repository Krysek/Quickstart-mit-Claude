# 🧱 Tetris in Schwarz/Weiß

[![CI](https://github.com/Krysek/Quickstart-mit-Claude/actions/workflows/ci.yml/badge.svg)](https://github.com/Krysek/Quickstart-mit-Claude/actions/workflows/ci.yml)

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
- Vollständig mit **Type Hints** versehen (geprüft mit `mypy --strict`)
- **Dokumentations-Website** mit Diagrammen und API-Referenz (MkDocs)

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

## 📚 Dokumentation

Die Dokumentation ist eine Website, die aus den Docstrings, den Type Hints und
den Mermaid-Diagrammen in `docs/` erzeugt wird. Die Werkzeuge dafür kommen in
eine eigene virtuelle Umgebung:

```bash
python -m venv .venv
.venv\Scriptsctivate              # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt

mkdocs serve                         # Vorschau unter http://127.0.0.1:8000
mkdocs build --strict                # fertige Website im Ordner site/
```

Typprüfung (im Ordner `Quickstart mit Claude`):

```bash
mypy --strict model.py menu.py animation.py view.py Quickstart_mit_Claude.py
```

Die Diagramme werden nur in [`docs/Diagramme.md`](docs/Diagramme.md) gepflegt.
Die Website bindet sie zusätzlich auf den passenden API-Seiten ein.

> **Hinweis:** Die Dateien in `docs/api/` und `docs/index.md` sind Vorlagen für
> MkDocs. Zeilen wie `--8<-- "docs/Diagramme.md:ablauf"` (Diagramm einfügen)
> oder `::: model` (API-Doku aus dem Quelltext erzeugen) werden erst beim Bauen
> ausgeführt. Auf GitHub erscheinen sie daher als roher Text. Die fertige
> Website gibt es lokal (siehe oben) oder als Download: Im Tab **Actions** den
> letzten Lauf öffnen, unter *Artifacts* `dokumentation` herunterladen,
> entpacken und `index.html` öffnen. Die Suche funktioniert nur über
> `mkdocs serve` oder einen Webserver, nicht beim Öffnen per Doppelklick.

## ✅ Automatische Prüfungen (GitHub Actions)

Bei jedem Push prüft [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
auf GitHub automatisch:

- die Unit-Tests und `mypy --strict` mit Python 3.11, 3.12 und 3.13
- ob sich die Dokumentations-Website fehlerfrei bauen lässt; sie liegt danach
  im Lauf unter *Artifacts* als ZIP `dokumentation` zum Herunterladen bereit

Das Ergebnis steht im Tab **Actions** und als Abzeichen oben in dieser Datei.

Die Website kann zusätzlich auf **GitHub Pages** veröffentlicht werden. Dieser
Schritt ist ausgeschaltet, denn Pages-Seiten sind öffentlich, auch bei einem
privaten Repository. Zum Einschalten unter *Settings → Pages* die Quelle
„GitHub Actions“ wählen und unter *Settings → Secrets and variables → Actions →
Variables* die Variable `PAGES_ENABLED` mit dem Wert `true` anlegen.

## 🎮 Steuerung

<!-- --8<-- [start:steuerung] -->
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
<!-- --8<-- [end:steuerung] -->

## 🏆 Punkte

<!-- --8<-- [start:punkte] -->
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
<!-- --8<-- [end:punkte] -->

## 📁 Projektstruktur

```
.
├── Quickstart mit Claude/
│   ├── Quickstart_mit_Claude.py    # Startpunkt: TetrisApp (Tastatur, Timer)
│   ├── model.py                    # Spielregeln: Piece, Board, Bag, Game
│   ├── menu.py                     # Pausenmenü: PauseMenu
│   ├── animation.py                # Lösch-Animation: ClearAnimation
│   ├── view.py                     # Zeichnen: Renderer
│   ├── test_tetris.py              # Unit-Tests
│   └── Quickstart mit Claude.pyproj
├── .github/workflows/ci.yml       # automatische Prüfungen auf GitHub
├── docs/
│   ├── Diagramme.md                # alle Diagramme (Mermaid), einzige Quelle
│   ├── index.md                    # Startseite der Dokumentations-Website
│   └── api/                        # Seiten der API-Referenz
├── overrides/                      # deutsche Beschriftungen für die API-Referenz
├── mkdocs.yml                      # Konfiguration der Dokumentations-Website
├── requirements-dev.txt            # Werkzeuge: MkDocs, mypy
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
| `ClearAnimation` | `animation.py` | Fortschritt der Lösch-Animation |
| `Renderer` | `view.py` | Zeichnet alles auf den tkinter-Canvas |
| `TetrisApp` | `Quickstart_mit_Claude.py` | Verbindet alles: Tastatur und Timer |

Nur `view.py` und `Quickstart_mit_Claude.py` nutzen tkinter. Alles andere
lässt sich ohne Fenster testen, sogar auf einem Rechner ganz ohne tkinter.

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
