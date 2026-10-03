"""Einfaches Tetris in Schwarz/Weiß mit tkinter."""

import random
import tkinter as tk

COLS, ROWS = 10, 20
CELL = 30
PANEL = 180
BG, FG = "black", "white"
FONT = ("Courier", 12, "bold")
BIG_FONT = ("Courier", 20, "bold")

SHAPES = [
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],  # I
    [[1, 1], [1, 1]],                                          # O
    [[0, 1, 0], [1, 1, 1], [0, 0, 0]],                         # T
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],                         # S
    [[1, 1, 0], [0, 1, 1], [0, 0, 0]],                         # Z
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]],                         # J
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]],                         # L
]

LINE_SCORES = [0, 100, 300, 500, 800]


def rotate(shape):
    """Dreht eine Form um 90° im Uhrzeigersinn."""
    return [list(row) for row in zip(*shape[::-1])]


class Tetris:
    def __init__(self, root):
        self.root = root
        root.title("Tetris")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=COLS * CELL + PANEL, height=ROWS * CELL,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()
        root.bind("<Key>", self.on_key)
        self.job = None
        self.new_game()

    # --- Spiellogik -------------------------------------------------------

    def new_game(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.paused = False
        self.game_over = False
        self.bag = []
        self.next_shape = self.take_from_bag()
        self.spawn()
        self.draw()
        self.schedule()

    def take_from_bag(self):
        # 7er-Beutel: jede Form kommt einmal pro Runde, in zufälliger Reihenfolge
        if not self.bag:
            self.bag = [s for s in SHAPES]
            random.shuffle(self.bag)
        return self.bag.pop()

    def spawn(self):
        self.shape = self.next_shape
        self.next_shape = self.take_from_bag()
        self.x = (COLS - len(self.shape[0])) // 2
        self.y = 0
        if self.collides(self.shape, self.x, self.y):
            self.game_over = True

    def collides(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, filled in enumerate(row):
                if not filled:
                    continue
                bx, by = x + c, y + r
                if bx < 0 or bx >= COLS or by >= ROWS:
                    return True
                if by >= 0 and self.board[by][bx]:
                    return True
        return False

    def move(self, dx, dy):
        if self.collides(self.shape, self.x + dx, self.y + dy):
            return False
        self.x += dx
        self.y += dy
        return True

    def rotate_piece(self):
        rotated = rotate(self.shape)
        # Einfache "Wall Kicks": bei Kollision seitlich ausweichen
        for dx in (0, -1, 1, -2, 2):
            if not self.collides(rotated, self.x + dx, self.y):
                self.shape = rotated
                self.x += dx
                return

    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self.lock()

    def lock(self):
        for r, row in enumerate(self.shape):
            for c, filled in enumerate(row):
                if filled and self.y + r >= 0:
                    self.board[self.y + r][self.x + c] = 1
        remaining = [row for row in self.board if not all(row)]
        cleared = ROWS - len(remaining)
        self.board = [[0] * COLS for _ in range(cleared)] + remaining
        self.lines += cleared
        self.score += LINE_SCORES[cleared] * self.level
        self.level = self.lines // 10 + 1
        self.spawn()

    def ghost_y(self):
        y = self.y
        while not self.collides(self.shape, self.x, y + 1):
            y += 1
        return y

    # --- Zeitsteuerung & Eingabe -----------------------------------------

    def schedule(self):
        delay = max(80, 500 - (self.level - 1) * 45)
        self.job = self.root.after(delay, self.tick)

    def tick(self):
        self.job = None
        if not self.paused and not self.game_over:
            if not self.move(0, 1):
                self.lock()
            self.draw()
        if not self.game_over:
            self.schedule()

    def on_key(self, event):
        key = event.keysym.lower()
        if key == "escape":
            self.root.destroy()
            return
        if key == "r":
            self.new_game()
            return
        if self.game_over:
            return
        if key == "p":
            self.paused = not self.paused
        elif self.paused:
            return
        elif key == "left":
            self.move(-1, 0)
        elif key == "right":
            self.move(1, 0)
        elif key == "down":
            if self.move(0, 1):
                self.score += 1
        elif key == "up":
            self.rotate_piece()
        elif key == "space":
            self.hard_drop()
        self.draw()

    # --- Zeichnen ----------------------------------------------------------

    def cell(self, c, r, size=CELL, ox=0, oy=0, ghost=False):
        x0, y0 = ox + c * size, oy + r * size
        self.canvas.create_rectangle(x0 + 1, y0 + 1, x0 + size - 1, y0 + size - 1,
                                     fill="" if ghost else FG,
                                     outline=FG if ghost else BG)

    def draw(self):
        cv = self.canvas
        cv.delete("all")
        width = COLS * CELL

        # Spielfeld
        cv.create_line(width + 1, 0, width + 1, ROWS * CELL, fill=FG, width=2)
        for r, row in enumerate(self.board):
            for c, filled in enumerate(row):
                if filled:
                    self.cell(c, r)

        if not self.game_over:
            gy = self.ghost_y()
            for r, row in enumerate(self.shape):
                for c, filled in enumerate(row):
                    if filled:
                        self.cell(self.x + c, gy + r, ghost=True)
                        self.cell(self.x + c, self.y + r)

        # Seitenleiste
        tx = width + 20
        cv.create_text(tx, 20, anchor="nw", text="NÄCHSTER", fill=FG, font=FONT)
        for r, row in enumerate(self.next_shape):
            for c, filled in enumerate(row):
                if filled:
                    self.cell(c, r, size=20, ox=tx, oy=50)

        info = f"PUNKTE\n{self.score}\n\nREIHEN\n{self.lines}\n\nLEVEL\n{self.level}"
        cv.create_text(tx, 150, anchor="nw", text=info, fill=FG, font=FONT)

        help_text = ("← →  Bewegen\n↑    Drehen\n↓    Schneller\n"
                     "Leer Fallen\nP    Pause\nR    Neustart\nEsc  Beenden")
        cv.create_text(tx, ROWS * CELL - 20, anchor="sw", text=help_text,
                       fill=FG, font=("Courier", 10))

        # Overlay für Pause / Game Over
        if self.paused or self.game_over:
            msg = "GAME OVER\n\nR = Neustart" if self.game_over else "PAUSE"
            cy = ROWS * CELL // 2
            cv.create_rectangle(20, cy - 60, width - 20, cy + 60, fill=BG, outline=FG, width=2)
            cv.create_text(width // 2, cy, text=msg, fill=FG, font=BIG_FONT, justify="center")


def main():
    root = tk.Tk()
    Tetris(root)
    root.mainloop()


if __name__ == "__main__":
    main()
