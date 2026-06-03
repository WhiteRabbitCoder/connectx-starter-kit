import unittest
from arena.board import Board


def make_board(grid, rows=6, cols=7, inarow=4):
    return Board(rows, cols, inarow, list(grid))


class TestBoardInit(unittest.TestCase):
    def test_default_board_is_empty(self):
        b = Board()
        self.assertEqual(b.grid, [0] * 42)
        self.assertEqual(b.rows, 6)
        self.assertEqual(b.cols, 7)
        self.assertEqual(b.inarow, 4)

    def test_all_columns_valid_on_empty_board(self):
        b = Board()
        self.assertEqual(b.valid_moves(), list(range(7)))


class TestDropPiece(unittest.TestCase):
    def test_piece_lands_at_bottom(self):
        b = Board()
        b.drop_piece(3, 1)
        self.assertEqual(b.grid[5 * 7 + 3], 1)

    def test_pieces_stack(self):
        b = Board()
        b.drop_piece(0, 1)
        b.drop_piece(0, 2)
        self.assertEqual(b.grid[5 * 7 + 0], 1)
        self.assertEqual(b.grid[4 * 7 + 0], 2)

    def test_full_column_returns_false(self):
        b = Board()
        for _ in range(6):
            b.drop_piece(0, 1)
        result = b.drop_piece(0, 2)
        self.assertFalse(result)

    def test_out_of_bounds_column_returns_false(self):
        b = Board()
        self.assertFalse(b.drop_piece(-1, 1))
        self.assertFalse(b.drop_piece(7, 1))

    def test_full_column_excluded_from_valid_moves(self):
        b = Board()
        for _ in range(6):
            b.drop_piece(0, 1)
        self.assertNotIn(0, b.valid_moves())


class TestCheckWin(unittest.TestCase):
    def _board_with_pieces(self, positions, mark):
        b = Board()
        for col in positions:
            b.drop_piece(col, mark)
        return b

    def test_horizontal_win(self):
        b = Board()
        for col in [0, 1, 2, 3]:
            b.drop_piece(col, 1)
        self.assertTrue(b.check_win(1))

    def test_horizontal_no_win_with_gap(self):
        b = Board()
        for col in [0, 1, 3, 4]:
            b.drop_piece(col, 1)
        self.assertFalse(b.check_win(1))

    def test_vertical_win(self):
        b = Board()
        for _ in range(4):
            b.drop_piece(3, 1)
        self.assertTrue(b.check_win(1))

    def test_vertical_no_win_three_in_col(self):
        b = Board()
        for _ in range(3):
            b.drop_piece(3, 1)
        self.assertFalse(b.check_win(1))

    def test_diagonal_down_right_win(self):
        # Build diagonal: (row5,col0), (row4,col1), (row3,col2), (row2,col3)
        b = Board()
        b.drop_piece(0, 1)                      # row5, col0
        b.drop_piece(1, 2); b.drop_piece(1, 1)  # row5, col1 filler; row4, col1
        b.drop_piece(2, 2); b.drop_piece(2, 2); b.drop_piece(2, 1)  # two fillers; row3, col2
        b.drop_piece(3, 2); b.drop_piece(3, 2); b.drop_piece(3, 2); b.drop_piece(3, 1)  # row2, col3
        self.assertTrue(b.check_win(1))

    def test_diagonal_down_left_win(self):
        # (row5,col3), (row4,col2), (row3,col1), (row2,col0)
        b = Board()
        b.drop_piece(3, 1)
        b.drop_piece(2, 2); b.drop_piece(2, 1)
        b.drop_piece(1, 2); b.drop_piece(1, 2); b.drop_piece(1, 1)
        b.drop_piece(0, 2); b.drop_piece(0, 2); b.drop_piece(0, 2); b.drop_piece(0, 1)
        self.assertTrue(b.check_win(1))

    def test_no_win_on_empty_board(self):
        b = Board()
        self.assertFalse(b.check_win(1))
        self.assertFalse(b.check_win(2))

    def test_win_does_not_bleed_to_opponent(self):
        b = Board()
        for col in [0, 1, 2, 3]:
            b.drop_piece(col, 1)
        self.assertFalse(b.check_win(2))


class TestIsFull(unittest.TestCase):
    def test_empty_board_not_full(self):
        self.assertFalse(Board().is_full())

    def test_full_board(self):
        b = Board()
        mark = 1
        for col in range(7):
            for _ in range(6):
                b.drop_piece(col, mark)
                mark = 3 - mark
        self.assertTrue(b.is_full())


class TestCopy(unittest.TestCase):
    def test_copy_is_independent(self):
        b = Board()
        b.drop_piece(0, 1)
        c = b.copy()
        c.drop_piece(1, 2)
        self.assertEqual(b.grid[5 * 7 + 1], 0)
        self.assertEqual(c.grid[5 * 7 + 1], 2)

    def test_copy_has_same_state(self):
        b = Board()
        b.drop_piece(3, 1)
        c = b.copy()
        self.assertEqual(b.grid, c.grid)


class TestToObservation(unittest.TestCase):
    def test_observation_board_matches_grid(self):
        b = Board()
        b.drop_piece(0, 1)
        obs = b.to_observation(1)
        self.assertEqual(obs.board, b.grid)

    def test_observation_mark_is_set(self):
        b = Board()
        obs1 = b.to_observation(1)
        obs2 = b.to_observation(2)
        self.assertEqual(obs1.mark, 1)
        self.assertEqual(obs2.mark, 2)

    def test_observation_board_is_a_copy(self):
        b = Board()
        obs = b.to_observation(1)
        obs.board[0] = 99
        self.assertEqual(b.grid[0], 0)


if __name__ == "__main__":
    unittest.main()
