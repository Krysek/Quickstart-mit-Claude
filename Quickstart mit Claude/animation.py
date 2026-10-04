"""Fortschritt der Animation beim Löschen voller Reihen.

Dieses Modul kennt kein tkinter. Es zählt nur die Schritte der Animation
mit; gezeichnet wird sie vom ``Renderer``, die Timer plant die ``TetrisApp``.
"""


class ClearAnimation:
    """Fortschritt der Animation beim Löschen voller Reihen.

    Die Animation hat zwei Phasen:

    1. Blinken (``BLINK_FRAMES`` Schritte à ``BLINK_DELAY`` ms): Die Reihen
       wechseln zwischen gefüllt und nur Umriss.
    2. Auflösen (ein Schritt pro Spaltenpaar à ``WIPE_DELAY`` ms): Pro
       Schritt verschwindet links und rechts der Mitte je eine Spalte. Bei
       ungerader Spaltenzahl verschwindet zuerst die mittlere Spalte.

    Attributes:
        rows: Zeilennummern der vollen Reihen.
        cols: Breite des Spielfelds.
        frame: Nummer des nächsten Schritts.
        flash: True, wenn die Reihen gerade als Umriss gezeichnet werden.
        wiped: Wie viele Spalten links und rechts der Mitte schon aufgelöst sind.
    """

    BLINK_FRAMES = 6    # 3x blinken
    BLINK_DELAY = 70
    WIPE_DELAY = 40

    def __init__(self, rows, cols):
        """Bereitet die Animation vor; der erste Schritt folgt mit :meth:`step`.

        Args:
            rows: Zeilennummern der vollen Reihen.
            cols: Breite des Spielfelds in Zellen.
        """
        self.rows = rows
        self.cols = cols
        self.frame = 0
        self.flash = False
        self.wiped = 0

    def step(self):
        """Geht einen Schritt weiter.

        Returns:
            Die Wartezeit bis zum nächsten Schritt in ms, oder None, wenn die
            Animation vorbei ist.
        """
        wipe_frames = (self.cols + 1) // 2
        if self.frame < self.BLINK_FRAMES:
            self.flash = self.frame % 2 == 0
            delay = self.BLINK_DELAY
        elif self.frame < self.BLINK_FRAMES + wipe_frames:
            self.flash = False
            self.wiped += 1
            delay = self.WIPE_DELAY
        else:
            return None
        self.frame += 1
        return delay

    def hides(self, col):
        """Gibt True zurück, wenn die Spalte schon aufgelöst ist."""
        left = (self.cols - 1) // 2 - col
        right = col - self.cols // 2
        return max(left, right) < self.wiped
