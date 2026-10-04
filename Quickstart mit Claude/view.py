"""Darstellung: Zeichnen auf dem tkinter-Canvas.

Der [`Renderer`][view.Renderer] liest nur den Zustand von
[`Game`][model.Game], [`PauseMenu`][menu.PauseMenu] und
[`ClearAnimation`][animation.ClearAnimation] und verändert ihn nie.
"""

import tkinter as tk

from animation import ClearAnimation
from menu import PauseMenu
from model import Game, GameState

CELL = 30                    # Kantenlänge einer Zelle in Pixeln
PANEL = 180                  # Breite der Seitenleiste in Pixeln
BG, FG = "black", "white"    # Hintergrund- und Vordergrundfarbe
FONT = ("Courier", 12, "bold")
BIG_FONT = ("Courier", 20, "bold")
SMALL_FONT = ("Courier", 10)


class Renderer:
    """Zeichnet Spielfeld, Seitenleiste und Overlays auf einen Canvas.

    Attributes:
        canvas: Die tkinter-Zeichenfläche.
        width: Breite des Spielfelds in Pixeln (ohne Seitenleiste).
        height: Höhe des Spielfelds in Pixeln.
    """

    def __init__(self, root: tk.Misc, cols: int, rows: int) -> None:
        """Legt den Canvas passend zur Spielfeldgröße an.

        Args:
            root: Das tkinter-Fenster, in das der Canvas kommt.
            cols: Breite des Spielfelds in Zellen.
            rows: Höhe des Spielfelds in Zellen.
        """
        self.width: int = cols * CELL
        self.height: int = rows * CELL
        self.canvas: tk.Canvas = tk.Canvas(root, width=self.width + PANEL, height=self.height,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

    def cell(self, c: int, r: int, size: int = CELL, ox: int = 0, oy: int = 0,
             ghost: bool = False) -> None:
        """Zeichnet eine einzelne Zelle.

        Args:
            c: Spalte der Zelle.
            r: Zeile der Zelle.
            size: Kantenlänge der Zelle in Pixeln.
            ox: Horizontaler Versatz in Pixeln (z. B. für die Vorschau).
            oy: Vertikaler Versatz in Pixeln.
            ghost: True zeichnet nur einen Umriss statt eines gefüllten Blocks.
        """
        x0, y0 = ox + c * size, oy + r * size
        self.canvas.create_rectangle(x0 + 1, y0 + 1, x0 + size - 1, y0 + size - 1,
                                     fill="" if ghost else FG,
                                     outline=FG if ghost else BG)

    def draw(self, game: Game, menu: PauseMenu,
             anim: ClearAnimation | None = None) -> None:
        """Zeichnet das komplette Fenster neu.

        Args:
            game: Das Spiel, dessen Zustand gezeigt wird.
            menu: Das Pausenmenü; ist es offen, wird es darübergelegt.
            anim: Die laufende Lösch-Animation oder None.
        """
        self.canvas.delete("all")
        self.draw_board(game, anim)
        self.draw_panel(game)
        if menu.is_open:
            self.draw_menu(menu)
        elif game.state is GameState.GAME_OVER:
            self.draw_game_over()

    def draw_board(self, game: Game, anim: ClearAnimation | None) -> None:
        """Zeichnet abgesetzte Blöcke, fallenden Stein und dessen Landeposition.

        Args:
            game: Das Spiel, dessen Spielfeld gezeigt wird.
            anim: Die laufende Lösch-Animation oder None.
        """
        self.canvas.create_line(self.width + 1, 0, self.width + 1, self.height,
                                fill=FG, width=2)
        for r, row in enumerate(game.board.grid):
            for c, filled in enumerate(row):
                if not filled:
                    continue
                if anim and r in anim.rows:
                    # volle Reihen blinken und lösen sich dann auf
                    if not anim.hides(c):
                        self.cell(c, r, ghost=anim.flash)
                else:
                    self.cell(c, r)

        if game.state is GameState.PLAYING:
            for c, r in game.ghost().cells():
                self.cell(c, r, ghost=True)
            for c, r in game.piece.cells():
                self.cell(c, r)

    def draw_panel(self, game: Game) -> None:
        """Zeichnet die Seitenleiste: Vorschau, Punkte und Tastenbelegung.

        Args:
            game: Das Spiel, dessen Werte gezeigt werden.
        """
        cv = self.canvas
        tx = self.width + 20
        cv.create_text(tx, 20, anchor="nw", text="NÄCHSTER", fill=FG, font=FONT)
        for r, row in enumerate(game.next_shape):
            for c, filled in enumerate(row):
                if filled:
                    self.cell(c, r, size=20, ox=tx, oy=50)

        info = f"PUNKTE\n{game.score}\n\nREIHEN\n{game.lines}\n\nLEVEL\n{game.level}"
        cv.create_text(tx, 150, anchor="nw", text=info, fill=FG, font=FONT)

        help_text = ("← →  Bewegen\n↑    Drehen\n↓    Schneller\n"
                     "Leer Fallen\nEsc  Pausenmenü\nR    Neustart")
        cv.create_text(tx, self.height - 20, anchor="sw", text=help_text,
                       fill=FG, font=SMALL_FONT)

    def draw_game_over(self) -> None:
        """Zeichnet den Game-Over-Hinweis mittig über das Spielfeld."""
        cv = self.canvas
        cx, cy = self.width // 2, self.height // 2
        cv.create_rectangle(20, cy - 60, self.width - 20, cy + 60, fill=BG, outline=FG, width=2)
        cv.create_text(cx, cy - 15, text="GAME OVER", fill=FG, font=BIG_FONT)
        cv.create_text(cx, cy + 30, text="R = Neustart   Esc = Beenden",
                       fill=FG, font=SMALL_FONT)

    def draw_menu(self, menu: PauseMenu) -> None:
        """Zeichnet das Pausenmenü mittig über das Spielfeld.

        Der ausgewählte Eintrag wird invertiert dargestellt (schwarze Schrift
        auf weißem Balken), die übrigen weiß auf schwarz.

        Args:
            menu: Das Pausenmenü mit dem ausgewählten Eintrag.
        """
        cv = self.canvas
        cx, cy = self.width // 2, self.height // 2
        cv.create_rectangle(20, cy - 120, self.width - 20, cy + 120, fill=BG, outline=FG, width=2)
        cv.create_text(cx, cy - 80, text="PAUSE", fill=FG, font=BIG_FONT)

        for i, item in enumerate(menu.ITEMS):
            iy = cy - 25 + i * 45
            selected = i == menu.index
            if selected:
                cv.create_rectangle(50, iy - 17, self.width - 50, iy + 17, fill=FG, outline=FG)
            cv.create_text(cx, iy, text=item, fill=BG if selected else FG, font=FONT)

        cv.create_text(cx, cy + 100, text="↑ ↓ Wählen   Enter OK", fill=FG, font=SMALL_FONT)
