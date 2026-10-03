"""Einfaches Tetris in Schwarz/Weiß mit tkinter.

Das Spiel läuft in einem eigenen Fenster. Links liegt das Spielfeld
(10 x 20 Zellen), rechts eine Seitenleiste mit Vorschau auf den nächsten
Stein, Punktestand, gelöschten Reihen, Level und Tastenbelegung.

Steuerung:
    Pfeil links/rechts  Stein bewegen
    Pfeil hoch          Stein drehen
    Pfeil runter        Stein schneller fallen lassen (+1 Punkt pro Zeile)
    Leertaste           Stein sofort fallen lassen (+2 Punkte pro Zeile)
    Esc oder P          Pausenmenü öffnen/schließen (bei Game Over: Beenden)
    R                   Neues Spiel

Im Pausenmenü:
    Pfeil hoch/runter   Eintrag wählen (Weiter, Neustart, Beenden)
    Enter oder Leertaste  Eintrag ausführen

Start:
    python Quickstart_mit_Claude.py
"""

import random
import tkinter as tk

COLS, ROWS = 10, 20          # Größe des Spielfelds in Zellen
CELL = 30                    # Kantenlänge einer Zelle in Pixeln
PANEL = 180                  # Breite der Seitenleiste in Pixeln
BG, FG = "black", "white"    # Hintergrund- und Vordergrundfarbe
FONT = ("Courier", 12, "bold")
BIG_FONT = ("Courier", 20, "bold")

# Die sieben Tetrominos als Matrizen: 1 = Block, 0 = leer.
# Die Matrizen sind quadratisch, damit das Drehen um die Mitte funktioniert.
SHAPES = [
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],  # I
    [[1, 1], [1, 1]],                                          # O
    [[0, 1, 0], [1, 1, 1], [0, 0, 0]],                         # T
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],                         # S
    [[1, 1, 0], [0, 1, 1], [0, 0, 0]],                         # Z
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]],                         # J
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]],                         # L
]

# Punkte für 0, 1, 2, 3 oder 4 gleichzeitig gelöschte Reihen (mal Level).
LINE_SCORES = [0, 100, 300, 500, 800]

# Einträge des Pausenmenüs, in der angezeigten Reihenfolge.
MENU_ITEMS = ["Weiter", "Neustart", "Beenden"]


def rotate(shape):
    """Dreht eine Form um 90° im Uhrzeigersinn.

    Args:
        shape: Form als Liste von Zeilen, z. B. ``[[0, 1, 0], [1, 1, 1], [0, 0, 0]]``.

    Returns:
        Eine neue, gedrehte Form. Die ursprüngliche Form bleibt unverändert.
    """
    return [list(row) for row in zip(*shape[::-1])]


class Tetris:
    """Das komplette Spiel: Zustand, Regeln, Zeitsteuerung, Eingabe und Grafik.

    Das Spielfeld ist eine Liste von ``ROWS`` Zeilen mit je ``COLS`` Werten
    (1 = belegt, 0 = frei). Der fallende Stein wird nicht ins Spielfeld
    geschrieben, sondern separat über ``shape``, ``x`` und ``y`` verwaltet und
    erst beim Aufsetzen (:meth:`lock`) fest eingetragen.

    Der Spieltakt läuft über ``root.after``: :meth:`tick` lässt den Stein
    regelmäßig eine Zeile fallen. Während volle Reihen animiert gelöscht
    werden, ist der Takt angehalten.

    Attributes:
        root: Das tkinter-Hauptfenster.
        canvas: Zeichenfläche für Spielfeld und Seitenleiste.
        board: Das Spielfeld, ``board[zeile][spalte]``.
        shape: Form des aktuell fallenden Steins.
        x, y: Position der linken oberen Ecke von ``shape`` im Spielfeld.
        next_shape: Form des nächsten Steins (für die Vorschau).
        bag: Noch nicht verteilte Formen der aktuellen 7er-Runde.
        score, lines, level: Punktestand, gelöschte Reihen, aktuelles Level.
        paused: True, solange das Spiel pausiert ist und das Pausenmenü zeigt.
        menu_index: Index des im Pausenmenü ausgewählten Eintrags.
        game_over: True, sobald ein neuer Stein keinen Platz mehr hat.
        clearing: Zeilennummern der Reihen, die gerade animiert gelöscht werden.
        flash: True, wenn die zu löschenden Reihen gerade als Umriss blinken.
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
        self.canvas = tk.Canvas(root, width=COLS * CELL + PANEL, height=ROWS * CELL,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()
        root.bind("<Key>", self.on_key)
        self.job = None
        self.anim_job = None
        self.new_game()

    # --- Spiellogik -------------------------------------------------------

    def new_game(self):
        """Setzt alles zurück und startet ein neues Spiel.

        Bricht dabei einen laufenden Spieltakt und eine laufende
        Lösch-Animation ab, damit nach einem Neustart keine alten
        Zeitgeber weiterlaufen.
        """
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None
        self.clearing = []
        self.flash = False
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.paused = False
        self.menu_index = 0
        self.game_over = False
        self.bag = []
        self.next_shape = self.take_from_bag()
        self.spawn()
        self.draw()
        self.schedule()

    def take_from_bag(self):
        """Zieht die nächste Form aus dem 7er-Beutel.

        Jede der sieben Formen kommt pro Runde genau einmal vor, in zufälliger
        Reihenfolge. Ist der Beutel leer, wird er neu gefüllt und gemischt.
        So gibt es keine langen Durststrecken ohne einen bestimmten Stein.

        Returns:
            Die gezogene Form.
        """
        if not self.bag:
            self.bag = [s for s in SHAPES]
            random.shuffle(self.bag)
        return self.bag.pop()

    def spawn(self):
        """Lässt den nächsten Stein oben in der Mitte erscheinen.

        Ist dort kein Platz mehr, ist das Spiel verloren und ``game_over``
        wird gesetzt.
        """
        self.shape = self.next_shape
        self.next_shape = self.take_from_bag()
        self.x = (COLS - len(self.shape[0])) // 2
        self.y = 0
        if self.collides(self.shape, self.x, self.y):
            self.game_over = True

    def collides(self, shape, x, y):
        """Prüft, ob eine Form an einer Position keinen Platz hätte.

        Args:
            shape: Die zu prüfende Form.
            x: Spalte der linken oberen Ecke der Form.
            y: Zeile der linken oberen Ecke der Form.

        Returns:
            True, wenn ein Block der Form links, rechts oder unten aus dem
            Spielfeld ragt oder ein belegtes Feld überdeckt, sonst False.
            Oben darf die Form über das Spielfeld hinausragen.
        """
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
        """Verschiebt den fallenden Stein, falls dort Platz ist.

        Args:
            dx: Verschiebung in Spalten (-1 = links, 1 = rechts).
            dy: Verschiebung in Zeilen (1 = nach unten).

        Returns:
            True, wenn der Stein verschoben wurde, False, wenn er blockiert ist.
        """
        if self.collides(self.shape, self.x + dx, self.y + dy):
            return False
        self.x += dx
        self.y += dy
        return True

    def rotate_piece(self):
        """Dreht den fallenden Stein im Uhrzeigersinn, wenn möglich.

        Passt der gedrehte Stein nicht an seine Stelle (z. B. direkt an der
        Wand), wird er testweise bis zu zwei Spalten nach links oder rechts
        versetzt ("Wall Kick"). Klappt keine Variante, bleibt er unverändert.
        """
        rotated = rotate(self.shape)
        for dx in (0, -1, 1, -2, 2):
            if not self.collides(rotated, self.x + dx, self.y):
                self.shape = rotated
                self.x += dx
                return

    def hard_drop(self):
        """Lässt den Stein sofort bis ganz nach unten fallen und setzt ihn ab.

        Gibt 2 Punkte pro übersprungener Zeile.
        """
        while self.move(0, 1):
            self.score += 2
        self.lock()

    def lock(self):
        """Setzt den fallenden Stein fest ins Spielfeld.

        Sind dadurch Reihen voll, startet die Lösch-Animation. Andernfalls
        erscheint direkt der nächste Stein.
        """
        for r, row in enumerate(self.shape):
            for c, filled in enumerate(row):
                if filled and self.y + r >= 0:
                    self.board[self.y + r][self.x + c] = 1
        full = [r for r, row in enumerate(self.board) if all(row)]
        if full:
            self.start_clear_animation(full)
        else:
            self.spawn()

    # --- Animation beim Löschen voller Reihen ------------------------------

    BLINK_FRAMES = 6    # 3x blinken
    WIPE_FRAMES = COLS // 2   # danach von der Mitte nach außen auflösen

    def start_clear_animation(self, rows):
        """Startet die Animation für volle Reihen und hält das Spiel an.

        Args:
            rows: Zeilennummern der vollen Reihen.
        """
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        self.clearing = rows
        self.anim_frame = 0
        self.animate_clear()

    def animate_clear(self):
        """Zeichnet einen Schritt der Lösch-Animation und plant den nächsten.

        Die Animation hat zwei Phasen:

        1. Blinken (``BLINK_FRAMES`` Schritte à 70 ms): Die Reihen wechseln
           zwischen gefüllt und nur Umriss.
        2. Auflösen (``WIPE_FRAMES`` Schritte à 40 ms): Pro Schritt
           verschwindet links und rechts der Mitte je eine Spalte.

        Danach ruft sie :meth:`finish_clear` auf.
        """
        frame = self.anim_frame
        if frame < self.BLINK_FRAMES:
            self.flash = frame % 2 == 0
            delay = 70
        elif frame < self.BLINK_FRAMES + self.WIPE_FRAMES:
            self.flash = False
            k = frame - self.BLINK_FRAMES
            for r in self.clearing:
                self.board[r][COLS // 2 - 1 - k] = 0
                self.board[r][COLS // 2 + k] = 0
            delay = 40
        else:
            self.anim_job = None
            self.finish_clear()
            return
        self.anim_frame += 1
        self.draw()
        self.anim_job = self.root.after(delay, self.animate_clear)

    def finish_clear(self):
        """Entfernt die animierten Reihen und setzt das Spiel fort.

        Die Reihen darüber rutschen nach, oben kommen leere Reihen dazu.
        Danach werden Punkte, Reihenzahl und Level aktualisiert, der nächste
        Stein erscheint und der Spieltakt läuft wieder an.
        """
        cleared = len(self.clearing)
        remaining = [row for r, row in enumerate(self.board) if r not in self.clearing]
        self.board = [[0] * COLS for _ in range(cleared)] + remaining
        self.clearing = []
        self.lines += cleared
        self.score += LINE_SCORES[cleared] * self.level
        self.level = self.lines // 10 + 1
        self.spawn()
        self.draw()
        if not self.game_over:
            self.schedule()

    def ghost_y(self):
        """Berechnet, in welcher Zeile der fallende Stein landen würde.

        Wird für den Umriss ("Ghost") genutzt, der die Landeposition anzeigt.

        Returns:
            Die tiefste Zeile, in die der Stein ohne Kollision fallen kann.
        """
        y = self.y
        while not self.collides(self.shape, self.x, y + 1):
            y += 1
        return y

    # --- Zeitsteuerung & Eingabe -----------------------------------------

    def schedule(self):
        """Plant den nächsten Spieltakt ein.

        Die Wartezeit beginnt bei 500 ms und sinkt pro Level um 45 ms,
        aber nie unter 80 ms.
        """
        delay = max(80, 500 - (self.level - 1) * 45)
        self.job = self.root.after(delay, self.tick)

    def tick(self):
        """Ein Spieltakt: Der Stein fällt eine Zeile oder wird abgesetzt.

        Während einer Pause passiert nichts, der Takt läuft aber weiter.
        Bei Game Over oder während der Lösch-Animation wird kein neuer Takt
        geplant.
        """
        self.job = None
        if not self.paused and not self.game_over:
            if not self.move(0, 1):
                self.lock()
            self.draw()
        if not self.game_over and not self.clearing:
            self.schedule()

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
        if self.paused:
            self.on_menu_key(key)
            return
        if key == "r":
            self.new_game()
            return
        if key == "escape" and self.game_over:
            self.root.destroy()
            return
        if self.game_over or self.clearing:
            return
        if key in ("escape", "p"):
            self.open_menu()
            return
        if key == "left":
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

    # --- Pausenmenü --------------------------------------------------------

    def open_menu(self):
        """Pausiert das Spiel und zeigt das Pausenmenü mit "Weiter" ausgewählt."""
        self.paused = True
        self.menu_index = 0
        self.draw()

    def close_menu(self):
        """Schließt das Pausenmenü und setzt das Spiel fort."""
        self.paused = False
        self.draw()

    def on_menu_key(self, key):
        """Verarbeitet Tastendrücke, solange das Pausenmenü offen ist.

        Pfeil hoch/runter wechseln den Eintrag (am Ende geht es oben weiter),
        Enter oder Leertaste führen ihn aus. Esc und P schließen das Menü,
        R startet direkt neu.

        Args:
            key: Name der gedrückten Taste in Kleinbuchstaben (tkinter-keysym).
        """
        if key in ("escape", "p"):
            self.close_menu()
        elif key == "r":
            self.new_game()
        elif key == "up":
            self.menu_index = (self.menu_index - 1) % len(MENU_ITEMS)
            self.draw()
        elif key == "down":
            self.menu_index = (self.menu_index + 1) % len(MENU_ITEMS)
            self.draw()
        elif key in ("return", "kp_enter", "space"):
            self.select_menu_item()

    def select_menu_item(self):
        """Führt den ausgewählten Menüeintrag aus: Weiter, Neustart oder Beenden."""
        item = MENU_ITEMS[self.menu_index]
        if item == "Weiter":
            self.close_menu()
        elif item == "Neustart":
            self.new_game()
        elif item == "Beenden":
            self.root.destroy()

    # --- Zeichnen ----------------------------------------------------------

    def cell(self, c, r, size=CELL, ox=0, oy=0, ghost=False):
        """Zeichnet eine einzelne Zelle.

        Args:
            c: Spalte der Zelle.
            r: Zeile der Zelle.
            size: Kantenlänge der Zelle in Pixeln.
            ox: Horizontaler Versatz in Pixeln (z. B. für die Vorschau).
            oy: Vertikaler Versatz in Pixeln.
            ghost: True zeichnet nur einen weißen Umriss statt eines
                gefüllten Blocks.
        """
        x0, y0 = ox + c * size, oy + r * size
        self.canvas.create_rectangle(x0 + 1, y0 + 1, x0 + size - 1, y0 + size - 1,
                                     fill="" if ghost else FG,
                                     outline=FG if ghost else BG)

    def draw(self):
        """Zeichnet das komplette Fenster neu.

        Dazu gehören das Spielfeld mit den abgesetzten Steinen, der fallende
        Stein samt Umriss an seiner Landeposition, die Seitenleiste und bei
        Bedarf der Hinweis für Pause oder Game Over.
        """
        cv = self.canvas
        cv.delete("all")
        width = COLS * CELL

        # Spielfeld
        cv.create_line(width + 1, 0, width + 1, ROWS * CELL, fill=FG, width=2)
        for r, row in enumerate(self.board):
            for c, filled in enumerate(row):
                if filled:
                    # volle Reihen blinken zwischen gefüllt und Umriss
                    self.cell(c, r, ghost=self.flash and r in self.clearing)

        if not self.game_over and not self.clearing:
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
                     "Leer Fallen\nEsc  Pausenmenü\nR    Neustart")
        cv.create_text(tx, ROWS * CELL - 20, anchor="sw", text=help_text,
                       fill=FG, font=("Courier", 10))

        # Overlay für Pausenmenü / Game Over
        cy = ROWS * CELL // 2
        if self.paused:
            self.draw_menu()
        elif self.game_over:
            cv.create_rectangle(20, cy - 60, width - 20, cy + 60, fill=BG, outline=FG, width=2)
            cv.create_text(width // 2, cy - 15, text="GAME OVER", fill=FG, font=BIG_FONT)
            cv.create_text(width // 2, cy + 30, text="R = Neustart   Esc = Beenden",
                           fill=FG, font=("Courier", 10))

    def draw_menu(self):
        """Zeichnet das Pausenmenü mittig über das Spielfeld.

        Der ausgewählte Eintrag wird invertiert dargestellt (schwarze Schrift
        auf weißem Balken), die übrigen weiß auf schwarz.
        """
        cv = self.canvas
        width = COLS * CELL
        cx, cy = width // 2, ROWS * CELL // 2
        cv.create_rectangle(20, cy - 120, width - 20, cy + 120, fill=BG, outline=FG, width=2)
        cv.create_text(cx, cy - 80, text="PAUSE", fill=FG, font=BIG_FONT)

        for i, item in enumerate(MENU_ITEMS):
            iy = cy - 25 + i * 45
            selected = i == self.menu_index
            if selected:
                cv.create_rectangle(50, iy - 17, width - 50, iy + 17, fill=FG, outline=FG)
            cv.create_text(cx, iy, text=item, fill=BG if selected else FG, font=FONT)

        cv.create_text(cx, cy + 100, text="↑ ↓ Wählen   Enter OK", fill=FG,
                       font=("Courier", 10))


def main():
    """Öffnet das Spielfenster und startet die tkinter-Ereignisschleife."""
    root = tk.Tk()
    Tetris(root)
    root.mainloop()


if __name__ == "__main__":
    main()
