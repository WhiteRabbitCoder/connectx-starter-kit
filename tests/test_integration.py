import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from arena.board import Board


AGENTS_DIR = Path(__file__).parent.parent / "agents"


def load_agent(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.my_agent


def play_game(agent1_fn, agent2_fn):
    """Returns (winner_mark, turns). winner_mark is 1, 2, or 0 for draw."""
    board = Board()
    players = [agent1_fn, agent2_fn]
    marks = [1, 2]
    current = 0

    for turn in range(board.rows * board.cols):
        mark = marks[current]
        obs = board.to_observation(mark)
        cfg = type("Config", (), {
            "rows": board.rows, "columns": board.cols, "inarow": board.inarow,
        })()

        col = players[current](obs, cfg)

        if col not in board.valid_moves():
            return (marks[1 - current], turn + 1)

        board.drop_piece(col, mark)

        if board.check_win(mark):
            return (mark, turn + 1)

        if board.is_full():
            return (0, turn + 1)

        current = 1 - current

    return (0, board.rows * board.cols)


class TestFullGame(unittest.TestCase):
    def _assert_valid_result(self, result):
        winner, turns = result
        self.assertIn(winner, [0, 1, 2], "Winner must be 0 (draw), 1, or 2")
        self.assertGreater(turns, 0, "Game must last at least one turn")
        self.assertLessEqual(turns, 42, "Game cannot exceed 42 turns")

    def test_random_vs_random(self):
        a = load_agent(AGENTS_DIR / "random_agent.py")
        result = play_game(a, a)
        self._assert_valid_result(result)

    def test_baseline_vs_random(self):
        baseline = load_agent(AGENTS_DIR / "baseline_agent.py")
        random = load_agent(AGENTS_DIR / "random_agent.py")
        result = play_game(baseline, random)
        self._assert_valid_result(result)

    def test_default_vs_baseline(self):
        default = load_agent(AGENTS_DIR / "default_agent.py")
        baseline = load_agent(AGENTS_DIR / "baseline_agent.py")
        result = play_game(default, baseline)
        self._assert_valid_result(result)

    def test_all_pairs(self):
        agents = {p.stem: load_agent(p) for p in AGENTS_DIR.glob("*.py") if p.stem != "__init__"}
        names = sorted(agents)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                with self.subTest(match=f"{a} vs {b}"):
                    result = play_game(agents[a], agents[b])
                    self._assert_valid_result(result)

    def test_baseline_beats_random_consistently(self):
        """Baseline should beat random agent in most games (at least 7 out of 10)."""
        baseline = load_agent(AGENTS_DIR / "baseline_agent.py")
        random = load_agent(AGENTS_DIR / "random_agent.py")
        wins = sum(
            1 for _ in range(10)
            if play_game(baseline, random)[0] == 1
        )
        self.assertGreaterEqual(wins, 7, "Baseline should beat random at least 70% of the time")

    def test_game_ends_in_at_most_42_turns(self):
        """A Connect Four game can have at most 42 moves."""
        a = load_agent(AGENTS_DIR / "random_agent.py")
        for _ in range(5):
            _, turns = play_game(a, a)
            self.assertLessEqual(turns, 42)


class TestTournament(unittest.TestCase):
    def test_tournament_produces_valid_scores(self):
        """Round-robin: scores are non-negative and top agent has at least one win."""
        agents = {p.stem: load_agent(p) for p in AGENTS_DIR.glob("*.py") if p.stem != "__init__"}
        scores = {name: 0 for name in agents}
        names = sorted(agents)

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                winner, _ = play_game(agents[a], agents[b])
                if winner == 1:
                    scores[a] += 3
                elif winner == 2:
                    scores[b] += 3
                else:
                    scores[a] += 1
                    scores[b] += 1

        for name, pts in scores.items():
            self.assertGreaterEqual(pts, 0, f"{name} has negative score")

        top_score = max(scores.values())
        self.assertGreater(top_score, 0, "At least one agent should have points")

    def test_baseline_finishes_top_or_tied(self):
        """Baseline should be among the top scorers."""
        agents = {p.stem: load_agent(p) for p in AGENTS_DIR.glob("*.py") if p.stem != "__init__"}
        scores = {name: 0 for name in agents}
        names = sorted(agents)

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                winner, _ = play_game(agents[a], agents[b])
                if winner == 1:
                    scores[a] += 3
                elif winner == 2:
                    scores[b] += 3
                else:
                    scores[a] += 1
                    scores[b] += 1

        top_score = max(scores.values())
        self.assertEqual(scores["baseline_agent"], top_score,
                         f"Baseline should be at the top. Scores: {scores}")


if __name__ == "__main__":
    unittest.main()
