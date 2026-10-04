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
- **Dokumentation** mit Diagrammen und API-Referenz, direkt auf GitHub lesbar
  und zusätzlich als Website (MkDocs)

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

**Direkt auf GitHub lesen:** [`docs/index.md`](docs/index.md) ist die Startseite.
Von dort führen Links zu den Diagrammen und zur API-Referenz mit allen Klassen
und Methoden.

Die Dateien in `docs/` sind normales Markdown mit Mermaid-Diagrammen, das
GitHub direkt darstellt. Sie entstehen so:

| Datei | Herkunft |
|---|---|
| [`docs/Diagramme.md`](docs/Diagramme.md) | von Hand gepflegt, einzige Quelle aller Diagramme |
| `docs/index.md`, `docs/api/*.md` | **erzeugt** mit `tools/gen_docs.py` aus den Vorlagen in `doc_templates/` |

Der Generator liest die Docstrings und Type Hints aus dem Quelltext und fügt die
Diagramme aus `docs/Diagramme.md` sowie die Tabellen zu Steuerung und Punkten
aus dieser README ein. Erzeugte Dateien also nie von Hand ändern, sondern
Quelltext oder Vorlage anpassen und neu erzeugen.

Die Werkzeuge kommen in eine eigene virtuelle Umgebung:

```bash
python -m venv .venv
.venv\Scripts\activate               # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
```

Nach Änderungen am Quelltext oder an den Vorlagen:

```bash
python tools/gen_docs.py             # docs/ neu erzeugen, danach committen
```

Die CI meldet einen Fehler, wenn das vergessen wurde.

Aus denselben Dateien baut MkDocs zusätzlich eine Website mit Suche und
Navigation:

```bash
mkdocs serve                         # Vorschau unter http://127.0.0.1:8000
mkdocs build --strict                # fertige Website im Ordner site/
```

Die Website gibt es auch als Download aus der CI: Im Tab **Actions** den letzten
Lauf öffnen, unter *Artifacts* `dokumentation` herunterladen, entpacken und
`index.html` öffnen. Die Suche funktioniert dabei nur über `mkdocs serve` oder
einen Webserver, nicht beim Öffnen per Doppelklick.

Typprüfung (im Ordner `Quickstart mit Claude`):

```bash
mypy --strict model.py menu.py animation.py view.py Quickstart_mit_Claude.py
```

## ✅ Automatische Prüfungen (GitHub Actions)

Bei jedem Push prüft [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
auf GitHub automatisch:

- die Unit-Tests und `mypy --strict` mit Python 3.11, 3.12 und 3.13
- ob die erzeugte Dokumentation in `docs/` zum aktuellen Quelltext passt
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
├── .github/workflows/ci.yml        # automatische Prüfungen auf GitHub
├── docs/                           # Dokumentation, direkt auf GitHub lesbar
│   ├── index.md                    # Startseite (erzeugt)
│   ├── Diagramme.md                # alle Diagramme (Mermaid), von Hand gepflegt
│   └── api/                        # API-Referenz pro Modul (erzeugt)
├── doc_templates/                  # Vorlagen für die erzeugten Seiten in docs/
├── tools/gen_docs.py               # erzeugt docs/ aus Vorlagen und Quelltext
├── mkdocs.yml                      # Konfiguration der Dokumentations-Website
├── requirements-dev.txt            # Werkzeuge: griffe, MkDocs, mypy
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
[`docs/Diagramme.md`](docs/Diagramme.md), alle Klassen und Methoden in der
API-Referenz, die über [`docs/index.md`](docs/index.md) erreichbar ist.

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
