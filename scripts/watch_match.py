import sys
import time
from importlib.util import spec_from_file_location, module_from_spec
from arena.board import Board


def load_agent(path):
    spec = spec_from_file_location("agent_module", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.my_agent


def find_landing_row(board: Board, col: int) -> int:
    for row in range(board.rows - 1, -1, -1):
        if board.grid[row * board.cols + col] == 0:
            return row
    return -1


def render_board(board: Board, falling_col: int = -1, falling_row: int = -1, falling_mark: int = 0) -> str:
    chars = {0: ".", 1: "A", 2: "B"}
    lines = []
    for r in range(board.rows):
        row_str = []
        for c in range(board.cols):
            if r == falling_row and c == falling_col:
                row_str.append(chars[falling_mark])
            else:
                row_str.append(chars[board.grid[r * board.cols + c]])
        lines.append(" ".join(row_str))
    lines.append(" ".join(str(c) for c in range(board.cols)))
    lines.append("")
    return "\n".join(lines)


# 6 filas + fila de índices + línea vacía
BOARD_LINES = 8


def print_board(board: Board, falling_col=-1, falling_row=-1, falling_mark=0):
    print(render_board(board, falling_col, falling_row, falling_mark), end="")
    sys.stdout.flush()


def clear_board():
    print(f"\033[{BOARD_LINES}A\033[J", end="")
    sys.stdout.flush()


def animate_drop(board: Board, col: int, mark: int, drop_delay: float = 0.06):
    landing_row = find_landing_row(board, col)
    if landing_row == -1:
        return

    for row in range(landing_row + 1):
        clear_board()
        print_board(board, falling_col=col, falling_row=row, falling_mark=mark)
        if row < landing_row:
            time.sleep(drop_delay)


def play_match_verbose(agent1_path, agent2_path, turn_delay=0.4, drop_delay=0.06):
    agent1 = load_agent(agent1_path)
    agent2 = load_agent(agent2_path)

    board = Board()
    players = [agent1, agent2]
    names = [agent1_path, agent2_path]
    marks = [1, 2]
    current = 0

    print("Partida en vivo  (A vs B)\n")
    print_board(board)

    for _ in range(board.rows * board.cols):
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

        if col not in board.valid_moves():
            winner = names[1 - current]
            print(f"\nJugador {name} jugó inválido (col {col}). Pierde.")
            print(f"Ganador: {winner}")
            return

        animate_drop(board, col, mark, drop_delay)
        board.drop_piece(col, mark)

        if board.check_win(mark):
            clear_board()
            print_board(board)
            print(f"Ganador: {names[current]}")
            return

        if board.is_full():
            clear_board()
            print_board(board)
            print("Empate")
            return

        time.sleep(turn_delay)
        current = 1 - current


if __name__ == "__main__":
    if len(sys.argv) == 3:
        a1 = sys.argv[1]
        a2 = sys.argv[2]
    else:
        a1 = "agents/team_template.py"
        a2 = "agents/baseline_agent.py"

    play_match_verbose(a1, a2)
