"""Einfaches Tetris in Schwarz/Weiß mit tkinter.

Das Spiel läuft in einem eigenen Fenster. Links liegt das Spielfeld
(10 x 20 Zellen), rechts eine Seitenleiste mit Vorschau auf den nächsten
Stein, Punktestand, gelöschten Reihen, Level und Tastenbelegung.

Aufbau:
    model.py                Spielregeln (Piece, Board, Bag, Game), ohne tkinter
    menu.py                 Zustand des Pausenmenüs (PauseMenu)
    view.py                 Zeichnen (Renderer) und Lösch-Animation (ClearAnimation)
    Quickstart_mit_Claude.py  verbindet alles: Tastatur und Timer (TetrisApp)

Steuerung:
    Pfeil links/rechts  Stein bewegen
    Pfeil hoch          Stein drehen
    Pfeil runter        Stein schneller fallen lassen (+1 Punkt pro Zeile)
    Leertaste           Stein sofort fallen lassen (+2 Punkte pro Zeile)
    Esc oder P          Pausenmenü öffnen/schließen
    Esc bei Game Over   Beenden
    R                   Neues Spiel

Im Pausenmenü:
    Pfeil hoch/runter   Eintrag wählen (Weiter, Neustart, Beenden)
    Enter oder Leertaste  Eintrag ausführen

Start:
    python Quickstart_mit_Claude.py
"""

import tkinter as tk

from menu import PauseMenu
from model import COLS, ROWS, Game, GameState
from view import ClearAnimation, Renderer


class TetrisApp:
    """Verbindet Spiel, Menü und Darstellung mit tkinter.

    Es gibt keine eigene Spielschleife: ``root.mainloop()`` ruft
    :meth:`on_key` bei Tastendrücken auf, und über ``root.after`` laufen
    zwei Timer, :meth:`tick` für den Spieltakt und :meth:`animate_clear` für
    die Lösch-Animation. Während der Animation ist der Spieltakt angehalten.

    Attributes:
        root: Das tkinter-Hauptfenster.
        renderer: Zeichnet den Zustand auf den Canvas.
        menu: Das Pausenmenü.
        game: Das laufende Spiel.
        anim: Die laufende Lösch-Animation oder None.
        job: ID des geplanten nächsten :meth:`tick` (oder None).
        anim_job: ID des geplanten nächsten Animationsschritts (oder None).
    """

    def __init__(self, root):
        """Baut das Fenster auf und startet das erste Spiel.

        Args:
            root: Das tkinter-Hauptfenster, in dem das Spiel läuft.
        """
        self.root = root
        root.title("Tetris")
        root.resizable(False, False)
        self.renderer = Renderer(root, COLS, ROWS)
        self.menu = PauseMenu()
        root.bind("<Key>", self.on_key)
        self.job = None
        self.anim_job = None
        self.new_game()

    def new_game(self):
        """Startet ein neues Spiel.

        Bricht dabei einen laufenden Spieltakt und eine laufende
        Lösch-Animation ab, damit nach einem Neustart keine alten
        Zeitgeber weiterlaufen.
        """
        self.cancel_timers()
        self.game = Game(COLS, ROWS)
        self.anim = None
        self.menu.close()
        self.draw()
        self.schedule()

    def cancel_timers(self):
        """Bricht Spieltakt und Animationsschritt ab, falls geplant."""
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None

    def draw(self):
        """Zeichnet den aktuellen Zustand neu."""
        self.renderer.draw(self.game, self.menu, self.anim)

    def update(self):
        """Startet bei Bedarf die Lösch-Animation und zeichnet neu.

        Wird nach jeder Aktion aufgerufen, die einen Stein absetzen kann.
        """
        if self.game.state is GameState.CLEARING and self.anim is None:
            self.start_clear_animation()
        else:
            self.draw()

    # --- Spieltakt ---------------------------------------------------------

    def schedule(self):
        """Plant den nächsten Spieltakt ein (Wartezeit je nach Level)."""
        self.job = self.root.after(self.game.tick_delay, self.tick)

    def tick(self):
        """Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt.

        Während einer Pause passiert nichts, der Takt läuft aber weiter.
        Bei Game Over oder während der Lösch-Animation wird kein neuer Takt
        geplant.
        """
        self.job = None
        if not self.menu.is_open:
            self.game.step()
            self.update()
        if self.game.state is GameState.PLAYING:
            self.schedule()

    # --- Lösch-Animation ---------------------------------------------------

    def start_clear_animation(self):
        """Hält den Spieltakt an und startet die Animation für volle Reihen."""
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        self.anim = ClearAnimation(self.game.clearing, self.game.board.cols)
        self.animate_clear()

    def animate_clear(self):
        """Zeigt einen Schritt der Lösch-Animation und plant den nächsten.

        Ist die Animation vorbei, werden die Reihen entfernt und der
        Spieltakt läuft wieder an.
        """
        delay = self.anim.step()
        if delay is None:
            self.anim = None
            self.anim_job = None
            self.game.finish_clear()
            self.draw()
            if self.game.state is GameState.PLAYING:
                self.schedule()
            return
        self.draw()
        self.anim_job = self.root.after(delay, self.animate_clear)

    # --- Eingabe -----------------------------------------------------------

    def on_key(self, event):
        """Reagiert auf Tastendrücke (Belegung siehe Modul-Docstring).

        Ist das Pausenmenü offen, gehen alle Tasten an :meth:`on_menu_key`.
        R funktioniert immer. Esc und P öffnen im laufenden Spiel das
        Pausenmenü, bei Game Over beendet Esc das Programm. Während der
        Lösch-Animation sind alle Tasten außer R gesperrt.

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
        if key == "escape" and self.game.state is GameState.GAME_OVER:
            self.root.destroy()
            return
        if self.game.state is not GameState.PLAYING:
            return
        if key in ("escape", "p"):
            self.menu.open()
            self.draw()
            return
        if key == "left":
            self.game.move(-1, 0)
        elif key == "right":
            self.game.move(1, 0)
        elif key == "down":
            self.game.soft_drop()
        elif key == "up":
            self.game.rotate()
        elif key == "space":
            self.game.hard_drop()
        self.update()

    def on_menu_key(self, key):
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
        self.draw()

    def select_menu_item(self):
        """Führt den ausgewählten Menüeintrag aus: Weiter, Neustart oder Beenden."""
        item = self.menu.selected
        if item == "Weiter":
            self.menu.close()
            self.draw()
        elif item == "Neustart":
            self.new_game()
        elif item == "Beenden":
            self.root.destroy()


def main():
    """Öffnet das Spielfenster und startet die tkinter-Ereignisschleife."""
    root = tk.Tk()
    TetrisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
