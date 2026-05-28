from importlib.util import spec_from_file_location, module_from_spec
from arena.board import Board
import sys
import time


def load_agent(path):
    spec = spec_from_file_location("agent_module", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.my_agent


def render_board(board: Board):
    chars = {0: ".", 1: "A", 2: "B"}
    grid_rows = []
    for r in range(board.rows):
        row_str = []
        for c in range(board.cols):
            idx = r * board.cols + c
            row_str.append(chars[board.grid[idx]])
        grid_rows.append(" ".join(row_str))
    print("\n".join(grid_rows))
    print(" ".join(str(c % 10) for c in range(board.cols)))
    print()


def play_match_verbose(agent1_path, agent2_path, delay=0.6):
    agent1 = load_agent(agent1_path)
    agent2 = load_agent(agent2_path)

    board = Board()
    players = [agent1, agent2]
    names = [agent1_path, agent2_path]
    marks = [1, 2]
    current = 0

    print("Partida en vivo")
    render_board(board)

    max_turns = board.rows * board.cols
    for _ in range(max_turns):
        mark = marks[current]
        player = players[current]
        name = names[current]
        obs = board.to_observation(mark)
        config = type("Config", (), {
            "rows": board.rows,
            "columns": board.cols,
            "inarow": board.inarow,
        })()

        col = player(obs, config)
        success = board.drop_piece(col, mark)

        if not success:
            render_board(board)
            winner = names[1] if current == 0 else names[0]
            print(f"Jugador {name} jugó inválido. Pierde.")
            print(f"Ganador: {winner}")
            return

        render_board(board)

        if board.check_win(mark):
            winner = names[current]
            print(f"Ganador: {winner}")
            return

        if board.is_full():
            print("Empate")
            return

        time.sleep(delay)
        current = 1 - current


if __name__ == "__main__":
    if len(sys.argv) == 3:
        a1 = sys.argv[1]
        a2 = sys.argv[2]
    else:
        a1 = "agents/team_template.py"
        a2 = "agents/baseline_agent.py"

    play_match_verbose(a1, a2)
