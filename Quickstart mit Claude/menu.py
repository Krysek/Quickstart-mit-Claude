"""Das Pausenmenü: welche Einträge es gibt und welcher ausgewählt ist.

Das Menü weiß nur, ob es offen ist und welcher Eintrag gewählt ist.
Gezeichnet wird es vom [`Renderer`][view.Renderer], ausgeführt wird der
Eintrag von der [`TetrisApp`][Quickstart_mit_Claude.TetrisApp].
"""

from typing import ClassVar


class PauseMenu:
    """Zustand des Pausenmenüs.

    Attributes:
        ITEMS: Die Einträge in der angezeigten Reihenfolge.
        is_open: True, solange das Menü angezeigt wird (das Spiel ist pausiert).
        index: Index des ausgewählten Eintrags in `ITEMS`.
    """

    ITEMS: ClassVar[tuple[str, ...]] = ("Weiter", "Neustart", "Beenden")

    def __init__(self) -> None:
        """Erzeugt ein geschlossenes Menü mit "Weiter" ausgewählt."""
        self.is_open: bool = False
        self.index: int = 0

    @property
    def selected(self) -> str:
        """Der Text des ausgewählten Eintrags."""
        return self.ITEMS[self.index]

    def open(self) -> None:
        """Öffnet das Menü mit "Weiter" ausgewählt."""
        self.is_open = True
        self.index = 0

    def close(self) -> None:
        """Schließt das Menü."""
        self.is_open = False

    def up(self) -> None:
        """Wählt den vorherigen Eintrag (vom ersten geht es zum letzten)."""
        self.index = (self.index - 1) % len(self.ITEMS)

    def down(self) -> None:
        """Wählt den nächsten Eintrag (vom letzten geht es zum ersten)."""
        self.index = (self.index + 1) % len(self.ITEMS)
