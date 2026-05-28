from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from arena.board import Board


def load_agent(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.my_agent


def play_single(agent1_fn, agent2_fn):
    board = Board()
    players = [agent1_fn, agent2_fn]
    marks = [1, 2]
    current = 0
    max_turns = board.rows * board.cols

    for _ in range(max_turns):
        mark = marks[current]
        player = players[current]
        obs = board.to_observation(mark)
        config = type("Config", (), {
            "rows": board.rows,
            "columns": board.cols,
            "inarow": board.inarow,
        })()

        col = player(obs, config)
        success = board.drop_piece(col, mark)
        if not success:
            return 1 if current == 1 else 2

        if board.check_win(mark):
            return marks[current]

        if board.is_full():
            return 0

        current = 1 - current

    return 0


def main():
    agents_dir = Path("agents")
    files = sorted([f for f in agents_dir.glob("*.py") if f.stem not in ["__init__", "team_template"]])
    agents = {f.stem: load_agent(f) for f in files}
    scores = {name: 0 for name in agents}

    names = list(agents.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            winner_mark = play_single(agents[a], agents[b])
            if winner_mark == 1:
                scores[a] += 3
            elif winner_mark == 2:
                scores[b] += 3
            else:
                scores[a] += 1
                scores[b] += 1
            print(f"{a} vs {b} -> gana {a} si winner_mark==1 else {b} si winner_mark==2 else Empate")

    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print("\nTabla final")
    for pos, (name, pts) in enumerate(ranking, 1):
        print(f"{pos}. {name}: {pts} pts")


if __name__ == "__main__":
    main()
