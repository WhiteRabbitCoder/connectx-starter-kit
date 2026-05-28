from random import choice


def my_agent(observation, configuration):
    """
    Plantilla para tu agente ConnectX.

    observation.board: lista de 42 enteros (0=vacío, 1=jugador1, 2=jugador2)
    observation.mark: tu ficha (1 o 2)
    configuration.rows: 6
    configuration.columns: 7
    configuration.inarow: 4

    Debes retornar un entero entre 0 y 6 (columna donde jugar).

    Opcional: puedes importar y usar herramientas desde arena.tools:
        from arena.tools import apply_tools, TOOLS

    Ejemplo con 3 herramientas:
        from arena.tools import apply_tools
        obs_dict = {"board": list(observation.board), "mark": observation.mark}
        cfg_dict = {"rows": configuration.rows, "cols": configuration.columns, "inarow": configuration.inarow}
        return apply_tools(obs_dict, cfg_dict, ["win_now", "block_now", "prefer_center"])
    """
    moves = [c for c in range(configuration.columns) if observation.board[c] == 0]
    return choice(moves)
