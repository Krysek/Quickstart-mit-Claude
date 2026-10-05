"""Spiellogik von Tetris, unabhängig von der Oberfläche.

Dieses Modul kennt kein tkinter. Es enthält nur die Regeln: Steine, Spielfeld,
7er-Beutel und den Spielablauf mit Punkten und Level. Dadurch lässt es sich
ohne Fenster testen (siehe `test_tetris.py`).
"""

import random
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

Shape: TypeAlias = tuple[tuple[int, ...], ...]
"""Form eines Steins als quadratische Matrix: 1 = Block, 0 = leer."""

COLS, ROWS = 10, 20          # Größe des Spielfelds in Zellen

# Die sieben Tetrominos als Matrizen: 1 = Block, 0 = leer.
# Die Matrizen sind quadratisch, damit das Drehen um die Mitte funktioniert.
SHAPES: tuple[Shape, ...] = (
    ((0, 0, 0, 0), (1, 1, 1, 1), (0, 0, 0, 0), (0, 0, 0, 0)),  # I
    ((1, 1), (1, 1)),                                          # O
    ((0, 1, 0), (1, 1, 1), (0, 0, 0)),                         # T
    ((0, 1, 1), (1, 1, 0), (0, 0, 0)),                         # S
    ((1, 1, 0), (0, 1, 1), (0, 0, 0)),                         # Z
    ((1, 0, 0), (1, 1, 1), (0, 0, 0)),                         # J
    ((0, 0, 1), (1, 1, 1), (0, 0, 0)),                         # L
)

# Punkte für 0, 1, 2, 3 oder 4 gleichzeitig gelöschte Reihen (mal Level).
LINE_SCORES = (0, 100, 300, 500, 800)

# Versatz in Spalten, der beim Drehen nacheinander ausprobiert wird ("Wall Kick").
KICKS = (0, -1, 1, -2, 2)

SOFT_DROP_POINTS = 1         # Punkte pro Zeile beim schnellen Fallenlassen
HARD_DROP_POINTS = 2         # Punkte pro Zeile beim sofortigen Fallenlassen
LINES_PER_LEVEL = 10         # gelöschte Reihen bis zum nächsten Level

# Spieltakt in ms: wird pro Level kürzer, damit das Spiel schwerer wird,
# aber nie kürzer als MIN_DELAY_MS, damit es spielbar bleibt.
START_DELAY_MS = 500
DELAY_STEP_MS = 45
MIN_DELAY_MS = 80


@dataclass(frozen=True)
class Piece:
    """Ein Stein: eine Form an einer Position im Spielfeld.

    Ein `Piece` ist unveränderlich. [`moved`][model.Piece.moved] und
    [`rotated`][model.Piece.rotated] liefern neue Steine, sodass man eine
    Bewegung erst ausprobieren und dann übernehmen kann.

    Attributes:
        shape: Form des Steins (siehe [`Shape`][model.Shape]).
        x: Spalte der linken oberen Ecke von `shape`.
        y: Zeile der linken oberen Ecke von `shape`.
    """

    shape: Shape
    x: int = 0
    y: int = 0

    def cells(self) -> Iterator[tuple[int, int]]:
        """Liefert die belegten Zellen des Steins im Spielfeld.

        Yields:
            Paare `(spalte, zeile)` für jeden Block des Steins.
        """
        for r, row in enumerate(self.shape):
            for c, filled in enumerate(row):
                if filled:
                    yield self.x + c, self.y + r

    def moved(self, dx: int, dy: int) -> "Piece":
        """Gibt einen um `dx` Spalten und `dy` Zeilen verschobenen Stein zurück.

        Args:
            dx: Verschiebung in Spalten (negativ = nach links).
            dy: Verschiebung in Zeilen (positiv = nach unten).
        """
        return Piece(self.shape, self.x + dx, self.y + dy)

    def rotated(self) -> "Piece":
        """Gibt den um 90° im Uhrzeigersinn gedrehten Stein zurück."""
        return Piece(tuple(zip(*self.shape[::-1])), self.x, self.y)


class Board:
    """Das Spielfeld mit den bereits abgesetzten Blöcken.

    Attributes:
        cols: Breite in Zellen.
        rows: Höhe in Zellen.
    """

    def __init__(self, cols: int = COLS, rows: int = ROWS) -> None:
        """Erzeugt ein leeres Spielfeld.

        Args:
            cols: Breite in Zellen.
            rows: Höhe in Zellen.
        """
        self.cols: int = cols
        self.rows: int = rows
        self._grid: list[list[int]] = [[0] * cols for _ in range(rows)]

    @property
    def grid(self) -> tuple[tuple[int, ...], ...]:
        """Schreibgeschützte Kopie des Spielfelds: `grid[zeile][spalte]`, 1 = belegt."""
        return tuple(tuple(row) for row in self._grid)

    def collides(self, piece: Piece) -> bool:
        """Prüft, ob ein Stein an seiner Position keinen Platz hätte.

        Args:
            piece: Der zu prüfende Stein.

        Returns:
            True, wenn ein Block links, rechts oder unten aus dem Spielfeld
                ragt oder ein belegtes Feld überdeckt, sonst False. Oben darf
                der Stein über das Spielfeld hinausragen.
        """
        for c, r in piece.cells():
            if c < 0 or c >= self.cols or r >= self.rows:
                return True
            if r >= 0 and self._grid[r][c]:
                return True
        return False

    def place(self, piece: Piece) -> None:
        """Trägt einen Stein fest ins Spielfeld ein (Teile oberhalb entfallen).

        Args:
            piece: Der abzusetzende Stein.
        """
        for c, r in piece.cells():
            if r >= 0:
                self._grid[r][c] = 1

    def full_rows(self) -> list[int]:
        """Gibt die Zeilennummern aller vollständig belegten Reihen zurück."""
        return [r for r, row in enumerate(self._grid) if all(row)]

    def remove_rows(self, rows: list[int]) -> None:
        """Entfernt die angegebenen Reihen; darüberliegende rutschen nach.

        Oben kommen entsprechend viele leere Reihen dazu.

        Args:
            rows: Zeilennummern der zu entfernenden Reihen.
        """
        remaining = [row for r, row in enumerate(self._grid) if r not in rows]
        self._grid = [[0] * self.cols for _ in range(len(rows))] + remaining


class Bag:
    """Der 7er-Beutel, aus dem die Steine gezogen werden.

    Jede Form kommt pro Runde genau einmal vor, in zufälliger Reihenfolge.
    So gibt es keine langen Durststrecken ohne einen bestimmten Stein.
    """

    def __init__(self, shapes: Sequence[Shape] = SHAPES,
                 rng: random.Random | None = None) -> None:
        """Erzeugt einen leeren Beutel; er wird beim ersten Ziehen gefüllt.

        Args:
            shapes: Die Formen, die der Beutel enthält.
            rng: Zufallsgenerator (z. B. `random.Random(42)` für Tests).
        """
        self._shapes: Sequence[Shape] = shapes
        self._rng: random.Random = rng or random.Random()
        # Die in dieser Runde noch nicht gezogenen Formen.
        self._items: list[Shape] = []

    def take(self) -> Shape:
        """Zieht die nächste Form; ein leerer Beutel wird neu gefüllt und gemischt."""
        if not self._items:
            self._items = list(self._shapes)
            self._rng.shuffle(self._items)
        return self._items.pop()


class GameState(Enum):
    """Zustand des Spiels."""

    PLAYING = auto()
    """Ein Stein fällt."""
    CLEARING = auto()
    """Volle Reihen warten auf [`finish_clear`][model.Game.finish_clear]."""
    GAME_OVER = auto()
    """Ein neuer Stein hatte keinen Platz mehr."""


class Game:
    """Ein Tetris-Spiel: Spielfeld, fallender Stein, Punkte und Level.

    Alle Aktionen ([`move`][model.Game.move], [`rotate`][model.Game.rotate],
    [`soft_drop`][model.Game.soft_drop], [`hard_drop`][model.Game.hard_drop],
    [`step`][model.Game.step]) wirken nur im Zustand `PLAYING`.

    Setzt ein Stein auf und füllt dabei Reihen, wechselt das Spiel in den
    Zustand `CLEARING` und merkt sich die Reihen in `clearing`. Erst
    [`finish_clear`][model.Game.finish_clear] entfernt sie. Dazwischen kann
    die Oberfläche eine Animation abspielen.

    Der Spielzustand ist nur lesbar (Properties); ändern lässt er sich
    ausschließlich über die Aktionen, damit die Regeln immer gelten.
    """

    def __init__(self, board: Board | None = None, bag: Bag | None = None) -> None:
        """Startet ein neues Spiel mit dem ersten Stein.

        Args:
            board: Das Spielfeld; ohne Angabe ein leeres mit `COLS` x `ROWS` Zellen.
            bag: Der 7er-Beutel; ohne Angabe einer mit zufälliger Reihenfolge
                (für Tests z. B. `Bag(rng=random.Random(0))`).
        """
        self._board: Board = board or Board()
        self._bag: Bag = bag or Bag()
        self._score: int = 0
        self._lines: int = 0
        self._level: int = 1
        self._state: GameState = GameState.PLAYING
        self._clearing: list[int] = []
        self._next_shape: Shape = self._bag.take()
        self._piece: Piece = self._spawn_piece()

    @property
    def board(self) -> Board:
        """Das Spielfeld."""
        return self._board

    @property
    def piece(self) -> Piece:
        """Der aktuell fallende Stein."""
        return self._piece

    @property
    def next_shape(self) -> Shape:
        """Form des nächsten Steins (für die Vorschau)."""
        return self._next_shape

    @property
    def score(self) -> int:
        """Punktestand."""
        return self._score

    @property
    def lines(self) -> int:
        """Anzahl der bisher gelöschten Reihen."""
        return self._lines

    @property
    def level(self) -> int:
        """Aktuelles Level (steigt alle `LINES_PER_LEVEL` Reihen)."""
        return self._level

    @property
    def state(self) -> GameState:
        """Der aktuelle [`GameState`][model.GameState]."""
        return self._state

    @property
    def clearing(self) -> list[int]:
        """Zeilennummern der vollen Reihen im Zustand `CLEARING` (als Kopie)."""
        return list(self._clearing)

    @property
    def tick_delay(self) -> int:
        """Wartezeit zwischen zwei Spieltakten in ms.

        Beginnt bei 500 ms und sinkt pro Level um 45 ms, aber nie unter 80 ms.
        """
        return max(MIN_DELAY_MS, START_DELAY_MS - (self._level - 1) * DELAY_STEP_MS)

    def _spawn_piece(self) -> Piece:
        """Erzeugt den nächsten Stein oben in der Mitte und zieht einen neuen."""
        shape = self._next_shape
        self._next_shape = self._bag.take()
        return Piece(shape, (self._board.cols - len(shape[0])) // 2, 0)

    def spawn(self) -> None:
        """Lässt den nächsten Stein oben in der Mitte erscheinen.

        Ist dort kein Platz mehr, wechselt das Spiel zu `GAME_OVER`.
        """
        self._piece = self._spawn_piece()
        if self._board.collides(self._piece):
            self._state = GameState.GAME_OVER

    def _try(self, piece: Piece) -> bool:
        """Übernimmt `piece` als fallenden Stein, falls er Platz hat."""
        if self._state is not GameState.PLAYING or self._board.collides(piece):
            return False
        self._piece = piece
        return True

    def move(self, dx: int, dy: int) -> bool:
        """Verschiebt den fallenden Stein, falls dort Platz ist.

        Args:
            dx: Verschiebung in Spalten (-1 = links, 1 = rechts).
            dy: Verschiebung in Zeilen (1 = nach unten).

        Returns:
            True, wenn der Stein verschoben wurde, sonst False.
        """
        return self._try(self._piece.moved(dx, dy))

    def rotate(self) -> bool:
        """Dreht den fallenden Stein im Uhrzeigersinn, wenn möglich.

        Passt der gedrehte Stein nicht an seine Stelle (z. B. direkt an der
        Wand), wird er testweise bis zu zwei Spalten nach links oder rechts
        versetzt ("Wall Kick"). Klappt keine Variante, bleibt er unverändert.

        Returns:
            True, wenn der Stein gedreht wurde, sonst False.
        """
        rotated = self._piece.rotated()
        for dx in KICKS:
            if self._try(rotated.moved(dx, 0)):
                return True
        return False

    def soft_drop(self) -> bool:
        """Lässt den Stein eine Zeile fallen und gibt dafür 1 Punkt.

        Returns:
            True, wenn der Stein gefallen ist, sonst False.
        """
        if self.move(0, 1):
            self._score += SOFT_DROP_POINTS
            return True
        return False

    def hard_drop(self) -> bool:
        """Lässt den Stein sofort ganz nach unten fallen und setzt ihn ab.

        Gibt 2 Punkte pro übersprungener Zeile.

        Returns:
            True, wenn dadurch Reihen voll sind (siehe [`lock`][model.Game.lock]).
        """
        if self._state is not GameState.PLAYING:
            return False
        target = self.ghost()
        self._score += HARD_DROP_POINTS * (target.y - self._piece.y)
        self._piece = target
        return self.lock()

    def step(self) -> bool:
        """Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt.

        Returns:
            True, wenn der Stein abgesetzt wurde und dadurch Reihen voll sind
                (siehe [`lock`][model.Game.lock]).
        """
        if self._state is GameState.PLAYING and not self.move(0, 1):
            return self.lock()
        return False

    def lock(self) -> bool:
        """Setzt den fallenden Stein fest ins Spielfeld.

        Sind dadurch Reihen voll, wechselt das Spiel zu `CLEARING`.
        Andernfalls erscheint direkt der nächste Stein.

        Returns:
            True, wenn Reihen voll sind und auf
                [`finish_clear`][model.Game.finish_clear] warten.
        """
        self._board.place(self._piece)
        full = self._board.full_rows()
        if full:
            self._clearing = full
            self._state = GameState.CLEARING
            return True
        self.spawn()
        return False

    def finish_clear(self) -> None:
        """Entfernt die vollen Reihen und setzt das Spiel fort.

        Aktualisiert Punkte, Reihenzahl und Level und lässt den nächsten
        Stein erscheinen.
        """
        if self._state is not GameState.CLEARING:
            return
        cleared = len(self._clearing)
        self._board.remove_rows(self._clearing)
        self._clearing = []
        self._lines += cleared
        self._score += LINE_SCORES[cleared] * self._level
        self._level = self._lines // LINES_PER_LEVEL + 1
        self._state = GameState.PLAYING
        self.spawn()

    def ghost(self) -> Piece:
        """Gibt den Stein an der Position zurück, an der er landen würde.

        Wird für den Umriss ("Ghost") genutzt, der die Landeposition anzeigt.
        """
        piece = self._piece
        while not self._board.collides(piece.moved(0, 1)):
            piece = piece.moved(0, 1)
        return piece
