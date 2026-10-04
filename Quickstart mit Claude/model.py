"""Spiellogik von Tetris, unabhängig von der Oberfläche.

Dieses Modul kennt kein tkinter. Es enthält nur die Regeln: Steine, Spielfeld,
7er-Beutel und den Spielablauf mit Punkten und Level. Dadurch lässt es sich
ohne Fenster testen (siehe ``test_tetris.py``).
"""

import random
from dataclasses import dataclass
from enum import Enum, auto

COLS, ROWS = 10, 20          # Größe des Spielfelds in Zellen

# Die sieben Tetrominos als Matrizen: 1 = Block, 0 = leer.
# Die Matrizen sind quadratisch, damit das Drehen um die Mitte funktioniert.
SHAPES = (
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


@dataclass(frozen=True)
class Piece:
    """Ein Stein: eine Form an einer Position im Spielfeld.

    Ein ``Piece`` ist unveränderlich. :meth:`moved` und :meth:`rotated`
    liefern neue Steine, sodass man eine Bewegung erst ausprobieren und
    dann übernehmen kann.

    Attributes:
        shape: Form als Tupel von Zeilen (1 = Block, 0 = leer).
        x: Spalte der linken oberen Ecke von ``shape``.
        y: Zeile der linken oberen Ecke von ``shape``.
    """

    shape: tuple
    x: int = 0
    y: int = 0

    def cells(self):
        """Liefert die belegten Zellen des Steins im Spielfeld.

        Yields:
            Paare ``(spalte, zeile)`` für jeden Block des Steins.
        """
        for r, row in enumerate(self.shape):
            for c, filled in enumerate(row):
                if filled:
                    yield self.x + c, self.y + r

    def moved(self, dx, dy):
        """Gibt einen um ``dx`` Spalten und ``dy`` Zeilen verschobenen Stein zurück."""
        return Piece(self.shape, self.x + dx, self.y + dy)

    def rotated(self):
        """Gibt den um 90° im Uhrzeigersinn gedrehten Stein zurück."""
        return Piece(tuple(zip(*self.shape[::-1])), self.x, self.y)


class Board:
    """Das Spielfeld mit den bereits abgesetzten Blöcken.

    Attributes:
        cols, rows: Breite und Höhe in Zellen.
        grid: ``grid[zeile][spalte]``, 1 = belegt, 0 = frei.
    """

    def __init__(self, cols=COLS, rows=ROWS):
        self.cols = cols
        self.rows = rows
        self.grid = [[0] * cols for _ in range(rows)]

    def collides(self, piece):
        """Prüft, ob ein Stein an seiner Position keinen Platz hätte.

        Returns:
            True, wenn ein Block links, rechts oder unten aus dem Spielfeld
            ragt oder ein belegtes Feld überdeckt, sonst False. Oben darf der
            Stein über das Spielfeld hinausragen.
        """
        for c, r in piece.cells():
            if c < 0 or c >= self.cols or r >= self.rows:
                return True
            if r >= 0 and self.grid[r][c]:
                return True
        return False

    def place(self, piece):
        """Trägt einen Stein fest ins Spielfeld ein (Teile oberhalb entfallen)."""
        for c, r in piece.cells():
            if r >= 0:
                self.grid[r][c] = 1

    def full_rows(self):
        """Gibt die Zeilennummern aller vollständig belegten Reihen zurück."""
        return [r for r, row in enumerate(self.grid) if all(row)]

    def remove_rows(self, rows):
        """Entfernt die angegebenen Reihen; darüberliegende rutschen nach.

        Oben kommen entsprechend viele leere Reihen dazu.
        """
        remaining = [row for r, row in enumerate(self.grid) if r not in rows]
        self.grid = [[0] * self.cols for _ in range(len(rows))] + remaining


class Bag:
    """Der 7er-Beutel, aus dem die Steine gezogen werden.

    Jede Form kommt pro Runde genau einmal vor, in zufälliger Reihenfolge.
    So gibt es keine langen Durststrecken ohne einen bestimmten Stein.
    """

    def __init__(self, shapes=SHAPES, rng=None):
        """Erzeugt einen leeren Beutel; er wird beim ersten Ziehen gefüllt.

        Args:
            shapes: Die Formen, die der Beutel enthält.
            rng: Zufallsgenerator (z. B. ``random.Random(42)`` für Tests).
        """
        self.shapes = shapes
        self.rng = rng or random.Random()
        self.items = []

    def take(self):
        """Zieht die nächste Form; ein leerer Beutel wird neu gefüllt und gemischt."""
        if not self.items:
            self.items = list(self.shapes)
            self.rng.shuffle(self.items)
        return self.items.pop()


class GameState(Enum):
    """Zustand des Spiels."""

    PLAYING = auto()    # ein Stein fällt
    CLEARING = auto()   # volle Reihen warten darauf, entfernt zu werden
    GAME_OVER = auto()  # ein neuer Stein hatte keinen Platz mehr


class Game:
    """Ein Tetris-Spiel: Spielfeld, fallender Stein, Punkte und Level.

    Alle Aktionen (:meth:`move`, :meth:`rotate`, :meth:`soft_drop`,
    :meth:`hard_drop`, :meth:`step`) wirken nur im Zustand ``PLAYING``.

    Setzt ein Stein auf und füllt dabei Reihen, wechselt das Spiel in den
    Zustand ``CLEARING`` und merkt sich die Reihen in ``clearing``. Erst
    :meth:`finish_clear` entfernt sie. Dazwischen kann die Oberfläche eine
    Animation abspielen.

    Attributes:
        board: Das Spielfeld.
        bag: Der 7er-Beutel.
        piece: Der aktuell fallende Stein.
        next_shape: Form des nächsten Steins (für die Vorschau).
        score, lines, level: Punktestand, gelöschte Reihen, aktuelles Level.
        state: Der aktuelle :class:`GameState`.
        clearing: Zeilennummern der vollen Reihen im Zustand ``CLEARING``.
    """

    def __init__(self, cols=COLS, rows=ROWS, rng=None):
        self.board = Board(cols, rows)
        self.bag = Bag(rng=rng)
        self.score = 0
        self.lines = 0
        self.level = 1
        self.state = GameState.PLAYING
        self.clearing = []
        self.next_shape = self.bag.take()
        self.spawn()

    @property
    def tick_delay(self):
        """Wartezeit zwischen zwei Spieltakten in ms.

        Beginnt bei 500 ms und sinkt pro Level um 45 ms, aber nie unter 80 ms.
        """
        return max(80, 500 - (self.level - 1) * 45)

    def spawn(self):
        """Lässt den nächsten Stein oben in der Mitte erscheinen.

        Ist dort kein Platz mehr, wechselt das Spiel zu ``GAME_OVER``.
        """
        shape = self.next_shape
        self.next_shape = self.bag.take()
        self.piece = Piece(shape, (self.board.cols - len(shape[0])) // 2, 0)
        if self.board.collides(self.piece):
            self.state = GameState.GAME_OVER

    def _try(self, piece):
        """Übernimmt ``piece`` als fallenden Stein, falls er Platz hat."""
        if self.state is not GameState.PLAYING or self.board.collides(piece):
            return False
        self.piece = piece
        return True

    def move(self, dx, dy):
        """Verschiebt den fallenden Stein, falls dort Platz ist.

        Returns:
            True, wenn der Stein verschoben wurde, sonst False.
        """
        return self._try(self.piece.moved(dx, dy))

    def rotate(self):
        """Dreht den fallenden Stein im Uhrzeigersinn, wenn möglich.

        Passt der gedrehte Stein nicht an seine Stelle (z. B. direkt an der
        Wand), wird er testweise bis zu zwei Spalten nach links oder rechts
        versetzt ("Wall Kick"). Klappt keine Variante, bleibt er unverändert.

        Returns:
            True, wenn der Stein gedreht wurde, sonst False.
        """
        rotated = self.piece.rotated()
        return any(self._try(rotated.moved(dx, 0)) for dx in KICKS)

    def soft_drop(self):
        """Lässt den Stein eine Zeile fallen und gibt dafür 1 Punkt.

        Returns:
            True, wenn der Stein gefallen ist, sonst False.
        """
        if self.move(0, 1):
            self.score += 1
            return True
        return False

    def hard_drop(self):
        """Lässt den Stein sofort ganz nach unten fallen und setzt ihn ab.

        Gibt 2 Punkte pro übersprungener Zeile.
        """
        if self.state is not GameState.PLAYING:
            return
        while self.move(0, 1):
            self.score += 2
        self.lock()

    def step(self):
        """Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt."""
        if self.state is GameState.PLAYING and not self.move(0, 1):
            self.lock()

    def lock(self):
        """Setzt den fallenden Stein fest ins Spielfeld.

        Sind dadurch Reihen voll, wechselt das Spiel zu ``CLEARING``.
        Andernfalls erscheint direkt der nächste Stein.
        """
        self.board.place(self.piece)
        full = self.board.full_rows()
        if full:
            self.clearing = full
            self.state = GameState.CLEARING
        else:
            self.spawn()

    def finish_clear(self):
        """Entfernt die vollen Reihen und setzt das Spiel fort.

        Aktualisiert Punkte, Reihenzahl und Level und lässt den nächsten
        Stein erscheinen.
        """
        if self.state is not GameState.CLEARING:
            return
        cleared = len(self.clearing)
        self.board.remove_rows(self.clearing)
        self.clearing = []
        self.lines += cleared
        self.score += LINE_SCORES[cleared] * self.level
        self.level = self.lines // 10 + 1
        self.state = GameState.PLAYING
        self.spawn()

    def ghost(self):
        """Gibt den Stein an der Position zurück, an der er landen würde.

        Wird für den Umriss ("Ghost") genutzt, der die Landeposition anzeigt.
        """
        piece = self.piece
        while not self.board.collides(piece.moved(0, 1)):
            piece = piece.moved(0, 1)
        return piece
