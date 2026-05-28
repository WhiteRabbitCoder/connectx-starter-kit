from importlib.util import spec_from_file_location, module_from_spec
from arena.board import Board
import sys


def load_agent(path):
    spec = spec_from_file_location("agent_module", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.my_agent


def play_match(agent1_path, agent2_path, verbose=True):
    agent1 = load_agent(agent1_path)
    agent2 = load_agent(agent2_path)

    board = Board()
    players = [agent1, agent2]
    marks = [1, 2]
    current = 0

    if verbose:
        print("Juego inicia. 1=Team A, 2=Team B")
        print(board.grid)

    while True:
        mark = marks[current]
        player = players[current]
        obs = board.to_observation(mark)
        config = type("Config", (), {
            "rows": board.rows,
            "columns": board.cols,
            "inarow": board.inarow,
        })()

        col = player(obs, config)

        if verbose:
            print(f"Turno jugador {mark}, juega columna {col}")

        success = board.drop_piece(col, mark)
        if not success:
            print(f"Jugador {mark} jugó inválido: columna {col}. Pierde automáticamente.")
            return 1 if current == 1 else 2
        if verbose:
            print(board.grid)

        if board.check_win(mark):
            winner = "Team A" if current == 0 else "Team B"
            print(f"Ganador: {winner}")
            return marks[current]

        if board.is_full():
            print("Empate (tablero lleno)")
            return 0

        current = 1 - current


if __name__ == "__main__":
    if len(sys.argv) == 2:
        team_agent = sys.argv[1]
        baseline = "agents/baseline_agent.py"
        print(f"Jugando {team_agent} vs baseline")
    elif len(sys.argv) == 3:
        team_agent = sys.argv[1]
        baseline = sys.argv[2]
        print(f"Jugando {team_agent} vs {baseline}")
    else:
        team_agent = "agents/team_template.py"
        baseline = "agents/baseline_agent.py"
        print(f"Jugando {team_agent} vs baseline por defecto")

    winner_mark = play_match(team_agent, baseline)
    print(f"Equipo ganador: {'Team A' if winner_mark == 1 else 'Team B' if winner_mark == 2 else 'Empate'}")
