"""Fortschritt der Animation beim Löschen voller Reihen.

Dieses Modul kennt kein tkinter. Es zählt nur die Schritte der Animation
mit; gezeichnet wird sie vom [`Renderer`][view.Renderer], die Timer plant
die [`TetrisApp`][Quickstart_mit_Claude.TetrisApp].
"""

from typing import ClassVar


class ClearAnimation:
    """Fortschritt der Animation beim Löschen voller Reihen.

    Die Animation hat zwei Phasen:

    1. Blinken (`BLINK_FRAMES` Schritte à `BLINK_DELAY` ms): Die Reihen
       wechseln zwischen gefüllt und nur Umriss.
    2. Auflösen (ein Schritt pro Spaltenpaar à `WIPE_DELAY` ms): Pro
       Schritt verschwindet links und rechts der Mitte je eine Spalte. Bei
       ungerader Spaltenzahl verschwindet zuerst die mittlere Spalte.

    Attributes:
        BLINK_FRAMES: Anzahl der Schritte in der Blinkphase (3x blinken).
        BLINK_DELAY: Dauer eines Blinkschritts in ms.
        WIPE_DELAY: Dauer eines Auflöseschritts in ms.
        rows: Zeilennummern der vollen Reihen.
        cols: Breite des Spielfelds.
    """

    BLINK_FRAMES: ClassVar[int] = 6
    BLINK_DELAY: ClassVar[int] = 70
    WIPE_DELAY: ClassVar[int] = 40

    def __init__(self, rows: list[int], cols: int) -> None:
        """Bereitet die Animation vor; den ersten Schritt macht `step()`.

        Args:
            rows: Zeilennummern der vollen Reihen.
            cols: Breite des Spielfelds in Zellen.
        """
        self.rows: list[int] = rows
        self.cols: int = cols
        self._frame: int = 0                 # Nummer des nächsten Schritts
        self._flash: bool = False
        self._wiped: int = 0                 # aufgelöste Spalten je Seite der Mitte

    @property
    def flash(self) -> bool:
        """True, wenn die Reihen gerade als Umriss gezeichnet werden."""
        return self._flash

    def step(self) -> int | None:
        """Geht einen Schritt weiter.

        Returns:
            Die Wartezeit bis zum nächsten Schritt in ms, oder None, wenn die
            Animation vorbei ist.
        """
        wipe_frames = (self.cols + 1) // 2
        if self._frame < self.BLINK_FRAMES:
            self._flash = self._frame % 2 == 0
            delay = self.BLINK_DELAY
        elif self._frame < self.BLINK_FRAMES + wipe_frames:
            self._flash = False
            self._wiped += 1
            delay = self.WIPE_DELAY
        else:
            return None
        self._frame += 1
        return delay

    def hides(self, col: int) -> bool:
        """Gibt True zurück, wenn die Spalte schon aufgelöst ist.

        Args:
            col: Spalte im Spielfeld.
        """
        left = (self.cols - 1) // 2 - col
        right = col - self.cols // 2
        return max(left, right) < self._wiped
