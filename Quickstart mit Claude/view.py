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

# Abstände und Größen in Pixeln. Die Overlay-Werte sind relativ zur Mitte des
# Spielfelds, damit Menü und Game Over bei jeder Spielfeldgröße zentriert sind.
CELL_GAP = 1                 # Abstand zwischen zwei Blöcken (je Seite)
LINE_WIDTH = 2               # Trennlinie zur Seitenleiste und Overlay-Rahmen
MARGIN = 20                  # Rand der Seitenleiste und der Overlays
PREVIEW_CELL = 20            # Kantenlänge einer Zelle in der Vorschau
PREVIEW_TOP = 50             # Oberkante der Vorschau
INFO_TOP = 150               # Oberkante von Punkten, Reihen und Level
GAME_OVER_HALF_HEIGHT = 60   # halbe Höhe des Game-Over-Kastens
GAME_OVER_TITLE_DY = -15
GAME_OVER_HINT_DY = 30
MENU_HALF_HEIGHT = 120       # halbe Höhe des Pausenmenüs
MENU_TITLE_DY = -80
MENU_FIRST_ITEM_DY = -25
MENU_ITEM_SPACING = 45       # Abstand zwischen zwei Menüeinträgen
MENU_BAR_INSET = 50          # seitlicher Rand des Auswahlbalkens
MENU_BAR_HALF_HEIGHT = 17    # halbe Höhe des Auswahlbalkens
MENU_HINT_DY = 100


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
        self.canvas.create_rectangle(x0 + CELL_GAP, y0 + CELL_GAP,
                                     x0 + size - CELL_GAP, y0 + size - CELL_GAP,
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
                                fill=FG, width=LINE_WIDTH)
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
        tx = self.width + MARGIN
        cv.create_text(tx, MARGIN, anchor="nw", text="NÄCHSTER", fill=FG, font=FONT)
        for r, row in enumerate(game.next_shape):
            for c, filled in enumerate(row):
                if filled:
                    self.cell(c, r, size=PREVIEW_CELL, ox=tx, oy=PREVIEW_TOP)

        info = f"PUNKTE\n{game.score}\n\nREIHEN\n{game.lines}\n\nLEVEL\n{game.level}"
        cv.create_text(tx, INFO_TOP, anchor="nw", text=info, fill=FG, font=FONT)

        help_text = ("← →  Bewegen\n↑    Drehen\n↓    Schneller\n"
                     "Leer Fallen\nEsc  Pausenmenü\nR    Neustart")
        cv.create_text(tx, self.height - MARGIN, anchor="sw", text=help_text,
                       fill=FG, font=SMALL_FONT)

    def draw_game_over(self) -> None:
        """Zeichnet den Game-Over-Hinweis mittig über das Spielfeld."""
        cv = self.canvas
        cx, cy = self.width // 2, self.height // 2
        self.draw_overlay_box(GAME_OVER_HALF_HEIGHT)
        cv.create_text(cx, cy + GAME_OVER_TITLE_DY, text="GAME OVER", fill=FG,
                       font=BIG_FONT)
        cv.create_text(cx, cy + GAME_OVER_HINT_DY, text="R = Neustart   Esc = Beenden",
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
        self.draw_overlay_box(MENU_HALF_HEIGHT)
        cv.create_text(cx, cy + MENU_TITLE_DY, text="PAUSE", fill=FG, font=BIG_FONT)

        for i, item in enumerate(menu.ITEMS):
            iy = cy + MENU_FIRST_ITEM_DY + i * MENU_ITEM_SPACING
            selected = i == menu.index
            if selected:
                cv.create_rectangle(MENU_BAR_INSET, iy - MENU_BAR_HALF_HEIGHT,
                                    self.width - MENU_BAR_INSET,
                                    iy + MENU_BAR_HALF_HEIGHT, fill=FG, outline=FG)
            cv.create_text(cx, iy, text=item, fill=BG if selected else FG, font=FONT)

        cv.create_text(cx, cy + MENU_HINT_DY, text="↑ ↓ Wählen   Enter OK", fill=FG,
                       font=SMALL_FONT)

    def draw_overlay_box(self, half_height: int) -> None:
        """Zeichnet einen gerahmten Kasten mittig über das Spielfeld.

        Der Kasten verdeckt das Spielfeld darunter; Game Over und Pausenmenü
        schreiben ihren Text hinein.

        Args:
            half_height: Halbe Höhe des Kastens in Pixeln.
        """
        cy = self.height // 2
        self.canvas.create_rectangle(MARGIN, cy - half_height,
                                     self.width - MARGIN, cy + half_height,
                                     fill=BG, outline=FG, width=LINE_WIDTH)
