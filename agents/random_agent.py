from random import choice


def my_agent(observation, configuration):
    """Agente aleatorio que elige una columna válido al azar."""
    moves = [c for c in range(configuration.columns) if observation.board[c] == 0]
    return choice(moves)
