"""Unit-Tests für Spiellogik, Pausenmenü und Lösch-Animation.

Start (im Ordner dieser Datei):
    python -m unittest -v
"""

import random
import unittest

from animation import ClearAnimation
from menu import PauseMenu
from model import COLS, ROWS, SHAPES, Bag, Board, Game, GameState, Piece

I_SHAPE, O_SHAPE, T_SHAPE = SHAPES[0], SHAPES[1], SHAPES[2]


def new_game():
    """Erzeugt ein Spiel mit festem Zufall, damit die Tests reproduzierbar sind."""
    return Game(rng=random.Random(0))


class PieceTest(unittest.TestCase):
    def test_cells_are_offset_by_position(self):
        piece = Piece(O_SHAPE, 3, 5)
        self.assertEqual(sorted(piece.cells()), [(3, 5), (3, 6), (4, 5), (4, 6)])

    def test_moved_returns_new_piece(self):
        piece = Piece(T_SHAPE, 0, 0)
        moved = piece.moved(2, 1)
        self.assertEqual((moved.x, moved.y), (2, 1))
        self.assertEqual((piece.x, piece.y), (0, 0))

    def test_rotated_turns_clockwise(self):
        rotated = Piece(T_SHAPE).rotated()
        self.assertEqual(rotated.shape, ((0, 1, 0), (0, 1, 1), (0, 1, 0)))

    def test_four_rotations_give_original(self):
        piece = Piece(I_SHAPE)
        for _ in range(4):
            piece = piece.rotated()
        self.assertEqual(piece.shape, I_SHAPE)


class BoardTest(unittest.TestCase):
    def test_collides_with_walls_and_floor(self):
        board = Board()
        self.assertTrue(board.collides(Piece(O_SHAPE, -1, 0)))
        self.assertTrue(board.collides(Piece(O_SHAPE, COLS - 1, 0)))
        self.assertTrue(board.collides(Piece(O_SHAPE, 0, ROWS - 1)))
        self.assertFalse(board.collides(Piece(O_SHAPE, 0, ROWS - 2)))

    def test_may_stick_out_at_the_top(self):
        self.assertFalse(Board().collides(Piece(O_SHAPE, 0, -1)))

    def test_collides_with_placed_blocks(self):
        board = Board()
        board.place(Piece(O_SHAPE, 4, 10))
        self.assertTrue(board.collides(Piece(O_SHAPE, 5, 9)))
        self.assertFalse(board.collides(Piece(O_SHAPE, 6, 9)))

    def test_full_rows_and_remove_rows(self):
        board = Board()
        board.grid[ROWS - 1] = [1] * COLS
        board.grid[ROWS - 2] = [1] * (COLS - 1) + [0]
        self.assertEqual(board.full_rows(), [ROWS - 1])

        board.remove_rows([ROWS - 1])
        self.assertEqual(len(board.grid), ROWS)
        self.assertEqual(board.grid[0], [0] * COLS)
        self.assertEqual(board.grid[ROWS - 1], [1] * (COLS - 1) + [0])


class BagTest(unittest.TestCase):
    def test_every_shape_once_per_round(self):
        bag = Bag(rng=random.Random(1))
        for _ in range(3):
            round_ = [bag.take() for _ in SHAPES]
            self.assertCountEqual(round_, SHAPES)


class GameTest(unittest.TestCase):
    def test_spawns_in_the_middle(self):
        game = new_game()
        width = len(game.piece.shape[0])
        self.assertEqual(game.piece.x, (COLS - width) // 2)
        self.assertEqual(game.piece.y, 0)
        self.assertIs(game.state, GameState.PLAYING)

    def test_cannot_move_through_wall(self):
        game = new_game()
        while game.move(-1, 0):
            pass
        self.assertEqual(min(c for c, _ in game.piece.cells()), 0)

    def test_wall_kick(self):
        game = new_game()
        vertical = Piece(I_SHAPE).rotated()        # Blöcke in Spalte 2 der Matrix
        game.piece = vertical.moved(-2, 5)         # also direkt an der linken Wand
        self.assertTrue(game.rotate())
        self.assertEqual(sorted(c for c, _ in game.piece.cells()), [0, 1, 2, 3])

    def test_soft_drop_gives_one_point(self):
        game = new_game()
        self.assertTrue(game.soft_drop())
        self.assertEqual(game.score, 1)

    def test_hard_drop_and_line_clear(self):
        game = new_game()
        # Unterste Reihe bis auf eine Lücke für den waagrechten I-Stein füllen.
        game.board.grid[ROWS - 1] = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1]
        game.piece = Piece(I_SHAPE, 3, 0)          # Blöcke in Zeile 1 der Matrix

        self.assertTrue(game.hard_drop())
        self.assertIs(game.state, GameState.CLEARING)
        self.assertEqual(game.clearing, [ROWS - 1])
        self.assertEqual(game.score, (ROWS - 2) * 2)

        game.finish_clear()
        self.assertIs(game.state, GameState.PLAYING)
        self.assertEqual(game.lines, 1)
        self.assertEqual(game.score, (ROWS - 2) * 2 + 100)
        self.assertTrue(all(cell == 0 for row in game.board.grid for cell in row))

    def test_hard_drop_without_full_row(self):
        game = new_game()
        landing = game.ghost()
        self.assertFalse(game.hard_drop())
        self.assertIs(game.state, GameState.PLAYING)
        self.assertEqual(game.score, 2 * landing.y)
        for c, r in landing.cells():
            self.assertEqual(game.board.grid[r][c], 1)

    def test_step_reports_full_rows(self):
        game = new_game()
        self.assertFalse(game.step())               # Stein fällt nur eine Zeile
        game.board.grid[ROWS - 1] = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1]
        game.piece = Piece(I_SHAPE, 3, ROWS - 2)   # liegt schon in der Lücke
        self.assertTrue(game.step())
        self.assertIs(game.state, GameState.CLEARING)

    def test_actions_ignored_while_clearing(self):
        game = new_game()
        game.state = GameState.CLEARING
        piece = game.piece
        self.assertFalse(game.move(1, 0))
        self.assertFalse(game.rotate())
        self.assertFalse(game.hard_drop())
        self.assertFalse(game.step())
        self.assertEqual(game.piece, piece)

    def test_level_and_speed(self):
        game = new_game()
        self.assertEqual(game.tick_delay, 500)
        game.lines = 9
        game.board.grid[ROWS - 1] = [1] * COLS
        game.clearing = [ROWS - 1]
        game.state = GameState.CLEARING
        game.finish_clear()
        self.assertEqual(game.level, 2)
        self.assertEqual(game.tick_delay, 455)
        game.level = 50
        self.assertEqual(game.tick_delay, 80)

    def test_game_over_when_no_room(self):
        game = new_game()
        game.board.grid[0] = [1] * COLS
        game.board.grid[1] = [1] * COLS
        game.spawn()
        self.assertIs(game.state, GameState.GAME_OVER)

    def test_ghost_lands_on_floor(self):
        game = new_game()
        ghost = game.ghost()
        self.assertEqual(max(r for _, r in ghost.cells()), ROWS - 1)


class PauseMenuTest(unittest.TestCase):
    def test_navigation_wraps_around(self):
        menu = PauseMenu()
        menu.open()
        self.assertEqual(menu.selected, "Weiter")
        menu.up()
        self.assertEqual(menu.selected, "Beenden")
        menu.down()
        menu.down()
        self.assertEqual(menu.selected, "Neustart")

    def test_open_resets_selection(self):
        menu = PauseMenu()
        menu.open()
        menu.down()
        menu.close()
        menu.open()
        self.assertEqual(menu.selected, "Weiter")


class ClearAnimationTest(unittest.TestCase):
    def test_blinks_then_wipes_from_the_middle(self):
        anim = ClearAnimation([ROWS - 1], 10)
        delays = []
        while (delay := anim.step()) is not None:
            delays.append(delay)
            if len(delays) == 7:                    # erster Auflöseschritt
                hidden = [c for c in range(10) if anim.hides(c)]
                self.assertEqual(hidden, [4, 5])
        self.assertEqual(delays, [70] * 6 + [40] * 5)
        self.assertTrue(all(anim.hides(c) for c in range(10)))

    def test_odd_width_starts_with_middle_column(self):
        anim = ClearAnimation([0], 9)
        for _ in range(ClearAnimation.BLINK_FRAMES + 1):
            anim.step()
        self.assertEqual([c for c in range(9) if anim.hides(c)], [4])


if __name__ == "__main__":
    unittest.main()
