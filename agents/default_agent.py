from arena.tools import apply_tools


def my_agent(observation, configuration):
    """
    Agente de ejemplo que usa 3 de las 5 herramientas disponibles:
    1. win_now
    2. block_now
    3. prefer_center

    Si ninguna decide, usa random_valid como fallback.
    """
    obs_dict = {
        "board": list(observation.board),
        "mark": observation.mark,
    }
    cfg_dict = {
        "rows": configuration.rows,
        "cols": configuration.columns,
        "inarow": configuration.inarow,
    }

    selected_tools = ["win_now", "block_now", "prefer_center"]

    return apply_tools(obs_dict, cfg_dict, selected_tools, fallback_name="random_valid")
