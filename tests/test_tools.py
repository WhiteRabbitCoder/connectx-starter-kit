import unittest
from arena.board import Board
from arena.tools import (
    TOOLS, apply_tools,
    _win_now, _block_now, _prefer_center, _random_valid,
)

COLS = 7
ROWS = 6
INAROW = 4


def empty_state(mark=1):
    return (
        {"board": [0] * 42, "mark": mark},
        {"rows": ROWS, "cols": COLS, "inarow": INAROW},
    )


def state_from_board(board: Board, mark: int):
    return (
        {"board": board.grid[:], "mark": mark},
        {"rows": board.rows, "cols": board.cols, "inarow": board.inarow},
    )


class TestWinNow(unittest.TestCase):
    def test_detects_horizontal_winning_move(self):
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 1)
        obs, cfg = state_from_board(b, 1)
        self.assertEqual(_win_now(obs, cfg), 3)

    def test_detects_vertical_winning_move(self):
        b = Board()
        for _ in range(3):
            b.drop_piece(4, 1)
        obs, cfg = state_from_board(b, 1)
        self.assertEqual(_win_now(obs, cfg), 4)

    def test_returns_none_when_no_win_available(self):
        obs, cfg = empty_state(1)
        self.assertIsNone(_win_now(obs, cfg))

    def test_does_not_play_for_opponent(self):
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 2)
        obs, cfg = state_from_board(b, 1)
        # mark=1 has no winning move
        self.assertIsNone(_win_now(obs, cfg))


class TestBlockNow(unittest.TestCase):
    def test_blocks_horizontal_threat(self):
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 2)
        obs, cfg = state_from_board(b, 1)
        self.assertEqual(_block_now(obs, cfg), 3)

    def test_blocks_vertical_threat(self):
        b = Board()
        for _ in range(3):
            b.drop_piece(2, 2)
        obs, cfg = state_from_board(b, 1)
        self.assertEqual(_block_now(obs, cfg), 2)

    def test_returns_none_when_no_threat(self):
        obs, cfg = empty_state(1)
        self.assertIsNone(_block_now(obs, cfg))

    def test_prioritizes_block_over_own_non_win(self):
        # Opponent has 3 in a row at cols 0,1,2 — only col 3 blocks
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 2)
        for col in [4, 5]:
            b.drop_piece(col, 1)
        obs, cfg = state_from_board(b, 1)
        self.assertEqual(_block_now(obs, cfg), 3)


class TestPreferCenter(unittest.TestCase):
    def test_empty_board_returns_center(self):
        obs, cfg = empty_state(1)
        result = _prefer_center(obs, cfg)
        self.assertEqual(result, 3)

    def test_always_returns_a_valid_column(self):
        obs, cfg = empty_state(1)
        result = _prefer_center(obs, cfg)
        self.assertIn(result, range(7))

    def test_avoids_full_center_and_picks_nearest(self):
        b = Board()
        for _ in range(6):
            b.drop_piece(3, 1)  # fill center
        obs, cfg = state_from_board(b, 1)
        result = _prefer_center(obs, cfg)
        self.assertNotEqual(result, 3)
        self.assertIn(result, [2, 4])  # nearest to center


class TestRandomValid(unittest.TestCase):
    def test_returns_valid_column(self):
        obs, cfg = empty_state(1)
        for _ in range(20):
            result = _random_valid(obs, cfg)
            self.assertIn(result, range(7))

    def test_does_not_return_full_column(self):
        b = Board()
        for _ in range(6):
            b.drop_piece(0, 1)
        obs, cfg = state_from_board(b, 1)
        for _ in range(20):
            result = _random_valid(obs, cfg)
            self.assertNotEqual(result, 0)


class TestApplyTools(unittest.TestCase):
    def test_win_now_takes_priority(self):
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 1)
        obs, cfg = state_from_board(b, 1)
        result = apply_tools(obs, cfg, ["win_now", "block_now", "prefer_center"])
        self.assertEqual(result, 3)

    def test_falls_back_through_chain(self):
        obs, cfg = empty_state(1)
        # win_now and block_now both return None on an empty board
        result = apply_tools(obs, cfg, ["win_now", "block_now", "prefer_center"])
        self.assertEqual(result, 3)

    def test_fallback_to_random_valid_when_all_none(self):
        # avoid_dead always returns None; pass only that tool
        obs, cfg = empty_state(1)
        result = apply_tools(obs, cfg, ["avoid_dead"])
        self.assertIn(result, range(7))

    def test_unknown_tool_name_is_ignored(self):
        obs, cfg = empty_state(1)
        result = apply_tools(obs, cfg, ["nonexistent_tool", "prefer_center"])
        self.assertEqual(result, 3)

    def test_more_than_three_tools_raises(self):
        obs, cfg = empty_state(1)
        with self.assertRaises(ValueError):
            apply_tools(obs, cfg, ["win_now", "block_now", "prefer_center", "random_valid"])

    def test_exactly_three_tools_is_allowed(self):
        obs, cfg = empty_state(1)
        result = apply_tools(obs, cfg, ["win_now", "block_now", "prefer_center"])
        self.assertIsNotNone(result)

    def test_tools_list_is_exhaustive(self):
        tool_names = {t.name for t in TOOLS}
        self.assertIn("win_now", tool_names)
        self.assertIn("block_now", tool_names)
        self.assertIn("prefer_center", tool_names)
        self.assertIn("avoid_dead", tool_names)
        self.assertIn("random_valid", tool_names)


if __name__ == "__main__":
    unittest.main()
