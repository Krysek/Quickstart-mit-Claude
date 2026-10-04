# Tetris in Schwarz/Weiß

Ein schlichtes, vollständig spielbares **Tetris** in Python, ohne externe
Abhängigkeiten. Gezeichnet wird mit `tkinter`, das bei Python schon dabei ist.

```bash
python "Quickstart mit Claude/Quickstart_mit_Claude.py"
```

## Aufbau

Das Spiel ist in Logik und Oberfläche aufgeteilt:

--8<-- "docs/Diagramme.md:module"

| Klasse | Modul | Aufgabe |
|---|---|---|
| [`Piece`][model.Piece] | `model.py` | Ein Stein: Form und Position, verschieben und drehen |
| [`Board`][model.Board] | `model.py` | Das Spielfeld: Kollisionen, Steine absetzen, volle Reihen |
| [`Bag`][model.Bag] | `model.py` | Der 7er-Beutel für die nächsten Steine |
| [`Game`][model.Game] | `model.py` | Die Regeln: Punkte, Level, Zustand ([`GameState`][model.GameState]) |
| [`PauseMenu`][menu.PauseMenu] | `menu.py` | Einträge und Auswahl des Pausenmenüs |
| [`ClearAnimation`][animation.ClearAnimation] | `animation.py` | Fortschritt der Lösch-Animation |
| [`Renderer`][view.Renderer] | `view.py` | Zeichnet alles auf den tkinter-Canvas |
| [`TetrisApp`][Quickstart_mit_Claude.TetrisApp] | `Quickstart_mit_Claude.py` | Verbindet alles: Tastatur und Timer |

## Weiterlesen

- [Architektur und Abläufe](Diagramme.md): Klassendiagramm, Spielzustände und
  die Abläufe von Spieltakt, Animation und Tastatur
- **API-Referenz**: alle Klassen und Methoden, erzeugt aus den Docstrings und
  Type Hints im Quelltext
    - [`model` – Spielregeln](api/model.md)
    - [`menu` – Pausenmenü](api/menu.md)
    - [`animation` – Lösch-Animation](api/animation.md)
    - [`view` – Zeichnen](api/view.md)
    - [`TetrisApp` – Steuerung](api/app.md)

## Steuerung

--8<-- "README.md:steuerung"

## Punkte

--8<-- "README.md:punkte"
