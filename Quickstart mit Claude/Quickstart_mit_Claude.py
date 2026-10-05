"""Einfaches Tetris in Schwarz/Weiß mit tkinter.

Das Spiel läuft in einem eigenen Fenster. Links liegt das Spielfeld
(10 x 20 Zellen), rechts eine Seitenleiste mit Vorschau auf den nächsten
Stein, Punktestand, gelöschten Reihen, Level und Tastenbelegung.

Aufbau:
    - `model.py`: Spielregeln (`Piece`, `Board`, `Bag`, `Game`), ohne tkinter
    - `menu.py`: Zustand des Pausenmenüs (`PauseMenu`), ohne tkinter
    - `animation.py`: Lösch-Animation (`ClearAnimation`), ohne tkinter
    - `view.py`: Zeichnen auf dem Canvas (`Renderer`)
    - `Quickstart_mit_Claude.py`: verbindet alles, Tastatur und Timer (`TetrisApp`)

Steuerung:
    - Pfeil links/rechts: Stein bewegen
    - Pfeil hoch: Stein drehen
    - Pfeil runter: Stein schneller fallen lassen (+1 Punkt pro Zeile)
    - Leertaste: Stein sofort fallen lassen (+2 Punkte pro Zeile)
    - Esc oder P: Pausenmenü öffnen/schließen
    - Esc bei Game Over: Beenden
    - R: Neues Spiel

Im Pausenmenü:
    - Pfeil hoch/runter: Eintrag wählen (Weiter, Neustart, Beenden)
    - Enter oder Leertaste: Eintrag ausführen

Start:
    `python Quickstart_mit_Claude.py`
"""

import tkinter as tk

from animation import ClearAnimation
from menu import PauseMenu
from model import COLS, ROWS, Board, Game, GameState
from view import Renderer


class TetrisApp:
    """Verbindet Spiel, Menü und Darstellung mit tkinter.

    Es gibt keine eigene Spielschleife: `root.mainloop()` ruft `on_key()`
    bei Tastendrücken auf, und über `root.after` laufen zwei Timer: `tick()`
    für den Spieltakt und `animate_clear()` für die Lösch-Animation.
    Während der Animation ist der Spieltakt angehalten.

    Attributes:
        root: Das tkinter-Hauptfenster.
        cols: Breite des Spielfelds in Zellen, für Spiel und Darstellung.
        rows: Höhe des Spielfelds in Zellen, für Spiel und Darstellung.
        renderer: Zeichnet den Zustand auf den Canvas.
        menu: Das Pausenmenü.
    """

    def __init__(self, root: tk.Tk, cols: int = COLS, rows: int = ROWS,
                 renderer: Renderer | None = None,
                 menu: PauseMenu | None = None) -> None:
        """Baut das Fenster auf und startet das erste Spiel.

        Args:
            root: Das tkinter-Hauptfenster, in dem das Spiel läuft.
            cols: Breite des Spielfelds in Zellen.
            rows: Höhe des Spielfelds in Zellen.
            renderer: Zeichnet den Zustand; ohne Angabe einer für `root` mit
                `cols` x `rows` Zellen.
            menu: Das Pausenmenü; ohne Angabe ein neues, geschlossenes.
        """
        self.root: tk.Tk = root
        self.cols: int = cols
        self.rows: int = rows
        root.title("Tetris")
        root.resizable(False, False)
        self.renderer: Renderer = renderer or Renderer(root, cols, rows)
        self.menu: PauseMenu = menu or PauseMenu()
        root.bind("<Key>", self.on_key)
        # IDs der mit root.after() geplanten Timer, None = keiner geplant.
        self._job: str | None = None
        self._anim_job: str | None = None
        self._anim: ClearAnimation | None = None
        self._game: Game
        self.new_game()

    def new_game(self) -> None:
        """Startet ein neues Spiel.

        Bricht dabei einen laufenden Spieltakt und eine laufende
        Lösch-Animation ab, damit nach einem Neustart keine alten
        Zeitgeber weiterlaufen.
        """
        self.cancel_timers()
        self._game = Game(Board(self.cols, self.rows))
        self._anim = None
        self.menu.close()
        self.draw()
        self.schedule()

    def cancel_tick(self) -> None:
        """Bricht den geplanten Spieltakt ab, falls es einen gibt."""
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None

    def cancel_timers(self) -> None:
        """Bricht Spieltakt und Animationsschritt ab, falls geplant."""
        self.cancel_tick()
        if self._anim_job:
            self.root.after_cancel(self._anim_job)
            self._anim_job = None

    def draw(self) -> None:
        """Zeichnet den aktuellen Zustand neu."""
        self.renderer.draw(self._game, self.menu, self._anim)

    # --- Spieltakt ---------------------------------------------------------

    def schedule(self) -> None:
        """Plant den nächsten Spieltakt ein (Wartezeit je nach Level)."""
        self._job = self.root.after(self._game.tick_delay, self.tick)

    def tick(self) -> None:
        """Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt.

        Während einer Pause passiert nichts, der Takt läuft aber weiter.
        Bei Game Over oder während der Lösch-Animation wird kein neuer Takt
        geplant.
        """
        self._job = None
        if not self.menu.is_open:
            if self._game.step():
                self.start_clear_animation()
            else:
                self.draw()
        if self._game.state is GameState.PLAYING:
            self.schedule()

    # --- Lösch-Animation ---------------------------------------------------

    def start_clear_animation(self) -> None:
        """Hält den Spieltakt an und startet die Animation für volle Reihen.

        Wird aufgerufen, wenn [`Game.step`][model.Game.step] oder
        [`Game.hard_drop`][model.Game.hard_drop] meldet, dass Reihen voll sind.
        """
        self.cancel_tick()
        self._anim = ClearAnimation(self._game.clearing, self._game.board.cols)
        self.animate_clear()

    def animate_clear(self) -> None:
        """Zeigt einen Schritt der Lösch-Animation und plant den nächsten.

        Ist die Animation vorbei, werden die Reihen entfernt und der
        Spieltakt läuft wieder an.
        """
        assert self._anim is not None
        delay = self._anim.step()
        if delay is None:
            self._anim = None
            self._anim_job = None
            self._game.finish_clear()
            self.draw()
            if self._game.state is GameState.PLAYING:
                self.schedule()
            return
        self.draw()
        self._anim_job = self.root.after(delay, self.animate_clear)

    # --- Eingabe -----------------------------------------------------------

    def on_key(self, event: tk.Event) -> None:
        """Reagiert auf Tastendrücke (Belegung siehe Modul-Docstring).

        Ist das Pausenmenü offen, gehen alle Tasten an `on_menu_key()`, im
        laufenden Spiel an `on_game_key()`. R funktioniert immer, bei Game
        Over beendet Esc das Programm. Während der Lösch-Animation sind alle
        Tasten außer R gesperrt.

        Args:
            event: Das tkinter-Tastaturereignis.
        """
        key = event.keysym.lower()
        if self.menu.is_open:
            self.on_menu_key(key)
            return
        if key == "r":
            self.new_game()
            return
        if key == "escape" and self._game.state is GameState.GAME_OVER:
            self.root.destroy()
            return
        if self._game.state is GameState.PLAYING:
            self.on_game_key(key)

    def on_game_key(self, key: str) -> None:
        """Verarbeitet Tastendrücke im laufenden Spiel.

        Esc und P öffnen das Pausenmenü, die Pfeiltasten bewegen und drehen
        den Stein, die Leertaste lässt ihn sofort fallen.

        Args:
            key: Name der gedrückten Taste in Kleinbuchstaben (tkinter-keysym).
        """
        if key in ("escape", "p"):
            self.menu.open()
            self.draw()
            return
        if key == "left":
            self._game.move(-1, 0)
        elif key == "right":
            self._game.move(1, 0)
        elif key == "down":
            self._game.soft_drop()
        elif key == "up":
            self._game.rotate()
        elif key == "space" and self._game.hard_drop():
            self.start_clear_animation()
            return
        self.draw()

    def on_menu_key(self, key: str) -> None:
        """Verarbeitet Tastendrücke, solange das Pausenmenü offen ist.

        Pfeil hoch/runter wechseln den Eintrag (am Ende geht es oben weiter),
        Enter oder Leertaste führen ihn aus. Esc und P schließen das Menü,
        R startet direkt neu.

        Args:
            key: Name der gedrückten Taste in Kleinbuchstaben (tkinter-keysym).
        """
        if key in ("escape", "p"):
            self.menu.close()
        elif key == "r":
            self.new_game()
            return
        elif key == "up":
            self.menu.up()
        elif key == "down":
            self.menu.down()
        elif key in ("return", "kp_enter", "space"):
            self.select_menu_item()
            return
        else:
            return
        self.draw()

    def select_menu_item(self) -> None:
        """Führt den ausgewählten Menüeintrag aus: Weiter, Neustart oder Beenden."""
        item = self.menu.selected
        if item == "Weiter":
            self.menu.close()
            self.draw()
        elif item == "Neustart":
            self.new_game()
        elif item == "Beenden":
            self.root.destroy()


def main() -> None:
    """Öffnet das Spielfenster und startet die tkinter-Ereignisschleife."""
    root = tk.Tk()
    TetrisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
