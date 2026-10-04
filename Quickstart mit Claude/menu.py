"""Das Pausenmenü: welche Einträge es gibt und welcher ausgewählt ist.

Das Menü weiß nur, ob es offen ist und welcher Eintrag gewählt ist.
Gezeichnet wird es vom ``Renderer``, ausgeführt wird der Eintrag von der
``TetrisApp``.
"""


class PauseMenu:
    """Zustand des Pausenmenüs.

    Attributes:
        is_open: True, solange das Menü angezeigt wird (das Spiel ist pausiert).
        index: Index des ausgewählten Eintrags in ``ITEMS``.
    """

    ITEMS = ("Weiter", "Neustart", "Beenden")

    def __init__(self):
        """Erzeugt ein geschlossenes Menü mit "Weiter" ausgewählt."""
        self.is_open = False
        self.index = 0

    @property
    def selected(self):
        """Der Text des ausgewählten Eintrags."""
        return self.ITEMS[self.index]

    def open(self):
        """Öffnet das Menü mit "Weiter" ausgewählt."""
        self.is_open = True
        self.index = 0

    def close(self):
        """Schließt das Menü."""
        self.is_open = False

    def up(self):
        """Wählt den vorherigen Eintrag (vom ersten geht es zum letzten)."""
        self.index = (self.index - 1) % len(self.ITEMS)

    def down(self):
        """Wählt den nächsten Eintrag (vom letzten geht es zum ersten)."""
        self.index = (self.index + 1) % len(self.ITEMS)
