import unittest
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from arena.board import Board


def load_agent(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.my_agent


def make_config(board):
    return type("Config", (), {
        "rows": board.rows,
        "columns": board.cols,
        "inarow": board.inarow,
    })()


AGENTS_DIR = Path(__file__).parent.parent / "agents"
AGENT_FILES = [
    AGENTS_DIR / "random_agent.py",
    AGENTS_DIR / "baseline_agent.py",
    AGENTS_DIR / "default_agent.py",
    AGENTS_DIR / "team_template.py",
]


class TestAgentContract(unittest.TestCase):
    """Every agent must return a valid, non-full column on every call."""

    def _run_agent(self, agent_fn, board=None):
        if board is None:
            board = Board()
        obs = board.to_observation(1)
        cfg = make_config(board)
        return agent_fn(obs, cfg)

    def _assert_valid(self, agent_fn, board=None):
        if board is None:
            board = Board()
        col = self._run_agent(agent_fn, board)
        self.assertIsInstance(col, int, "Agent must return an int")
        self.assertIn(col, range(board.cols), f"Column {col} is out of range")
        self.assertIn(col, board.valid_moves(), f"Column {col} is full")

    def test_random_agent_on_empty_board(self):
        self._assert_valid(load_agent(AGENTS_DIR / "random_agent.py"))

    def test_baseline_agent_on_empty_board(self):
        self._assert_valid(load_agent(AGENTS_DIR / "baseline_agent.py"))

    def test_default_agent_on_empty_board(self):
        self._assert_valid(load_agent(AGENTS_DIR / "default_agent.py"))

    def test_team_template_on_empty_board(self):
        self._assert_valid(load_agent(AGENTS_DIR / "team_template.py"))

    def test_agents_on_near_full_board(self):
        """Agents must still return valid moves when the board is nearly full."""
        # Fill all columns except column 6
        b = Board()
        mark = 1
        for col in range(6):
            for _ in range(6):
                b.drop_piece(col, mark)
                mark = 3 - mark

        for path in AGENT_FILES:
            agent = load_agent(path)
            obs = b.to_observation(1)
            cfg = make_config(b)
            col = agent(obs, cfg)
            with self.subTest(agent=path.stem):
                self.assertEqual(col, 6, f"{path.stem} should play column 6 (the only valid one)")

    def test_baseline_wins_when_possible(self):
        """Baseline must take the winning move if available."""
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 1)
        agent = load_agent(AGENTS_DIR / "baseline_agent.py")
        obs = b.to_observation(1)
        cfg = make_config(b)
        col = agent(obs, cfg)
        self.assertEqual(col, 3)

    def test_baseline_blocks_opponent(self):
        """Baseline must block opponent winning move."""
        # Opponent has 3 in a row at cols 0,1,2 — only col 3 blocks
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 2)
        agent = load_agent(AGENTS_DIR / "baseline_agent.py")
        obs = b.to_observation(1)
        cfg = make_config(b)
        col = agent(obs, cfg)
        self.assertEqual(col, 3)

    def test_default_agent_wins_when_possible(self):
        """Default agent (uses win_now tool) must take a winning move."""
        b = Board()
        for col in [0, 1, 2]:
            b.drop_piece(col, 1)
        agent = load_agent(AGENTS_DIR / "default_agent.py")
        obs = b.to_observation(1)
        cfg = make_config(b)
        col = agent(obs, cfg)
        self.assertEqual(col, 3)

    def test_all_agents_return_int_over_many_turns(self):
        """Simulate 20 random turns for each agent."""
        from random import seed, randint
        seed(42)
        for path in AGENT_FILES:
            agent = load_agent(path)
            b = Board()
            for _ in range(20):
                if not b.valid_moves():
                    break
                mark = randint(1, 2)
                obs = b.to_observation(mark)
                cfg = make_config(b)
                col = agent(obs, cfg)
                with self.subTest(agent=path.stem):
                    self.assertIsInstance(col, int)
                    self.assertIn(col, b.valid_moves())
                b.drop_piece(col, mark)


if __name__ == "__main__":
    unittest.main()
