from typing import List, Callable, Dict, Any
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable


TOOLS = [
    Tool(
        name="win_now",
        description="Si puedo ganar en esta jugada, lo hago.",
        fn=lambda obs, cfg: _win_now(obs, cfg)
    ),
    Tool(
        name="block_now",
        description="Si el rival gana en la siguiente, lo bloqueo.",
        fn=lambda obs, cfg: _block_now(obs, cfg)
    ),
    Tool(
        name="prefer_center",
        description="Prefiero columnas cerca del centro del tablero.",
        fn=lambda obs, cfg: _prefer_center(obs, cfg)
    ),
    Tool(
        name="avoid_dead",
        description="Evito columnas que están casi llenas y no miran a ninguna parte.",
        fn=lambda obs, cfg: _avoid_dead(obs, cfg)
    ),
    Tool(
        name="random_valid",
        description="Elige una columna válida al azar.",
        fn=lambda obs, cfg: _random_valid(obs, cfg)
    ),
]


def _win_now(obs: dict, cfg: dict):
    from arena.board import Board
    board_obj = Board(cfg["rows"], cfg["cols"], cfg["inarow"], obs["board"])
    mark = obs["mark"]
    for col in board_obj.valid_moves():
        test_board = board_obj.copy()
        if test_board.drop_piece(col, mark):
            if test_board.check_win(mark):
                return col
    return None


def _block_now(obs: dict, cfg: dict):
    from arena.board import Board
    board_obj = Board(cfg["rows"], cfg["cols"], cfg["inarow"], obs["board"])
    mark = obs["mark"]
    opponent = 1 if mark == 2 else 2
    for col in board_obj.valid_moves():
        test_board = board_obj.copy()
        if test_board.drop_piece(col, opponent):
            if test_board.check_win(opponent):
                return col
    return None


def _prefer_center(obs: dict, cfg: dict):
    from arena.board import Board
    board_obj = Board(cfg["rows"], cfg["cols"], cfg["inarow"], obs["board"])
    moves = board_obj.valid_moves()
    if not moves:
        return 0
    center = cfg["cols"] / 2.0
    return min(moves, key=lambda c: abs(c - center))


def _avoid_dead(obs: dict, cfg: dict):
    return None


def _random_valid(obs: dict, cfg: dict):
    from random import choice
    from arena.board import Board
    board_obj = Board(cfg["rows"], cfg["cols"], cfg["inarow"], obs["board"])
    moves = board_obj.valid_moves()
    return choice(moves) if moves else 0


def apply_tools(obs: dict, cfg: dict, tool_names: List[str], fallback_name: str = "random_valid"):
    if len(tool_names) > 3:
        raise ValueError(
            f"Límite de herramientas superado: se declararon {len(tool_names)}, máximo permitido es 3."
        )
    tool_map = {t.name: t for t in TOOLS}
    tools_used = [tool_map[name] for name in tool_names if name in tool_map]

    for tool in tools_used:
        result = tool.fn(obs, cfg)
        if result is not None:
            return result

    fallback = tool_map.get(fallback_name, tool_map["random_valid"])
    return fallback.fn(obs, cfg)
