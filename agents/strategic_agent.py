from arena.tools import apply_tools
from arena.board import Board


def _count_open_windows(board: Board, mark: int) -> dict:
    """Cuenta ventanas de 4 celdas sin piezas del rival (donde mark aún puede ganar)."""
    opponent = 3 - mark
    scores = {col: 0 for col in board.valid_moves()}
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for col in scores:
        test = board.copy()
        test.drop_piece(col, mark)
        for r in range(board.rows):
            for c in range(board.cols):
                for dr, dc in directions:
                    window = []
                    for i in range(board.inarow):
                        rr, cc = r + dr * i, c + dc * i
                        if 0 <= rr < board.rows and 0 <= cc < board.cols:
                            window.append(test.grid[rr * board.cols + cc])
                    if len(window) == board.inarow and opponent not in window:
                        scores[col] += window.count(mark)
    return scores


def my_agent(observation, configuration):
    obs_dict = {
        "board": list(observation.board),
        "mark": observation.mark,
    }
    cfg_dict = {
        "rows": configuration.rows,
        "cols": configuration.columns,
        "inarow": configuration.inarow,
    }

    # Herramienta 1: ganar si es posible
    # Herramienta 2: bloquear si el rival gana en la siguiente
    # Herramienta 3: preferir el centro como posición base
    tool_result = apply_tools(obs_dict, cfg_dict, ["win_now", "block_now", "prefer_center"])

    # Si prefer_center ya decidió, evalúa si hay una columna con más amenazas propias
    board = Board(configuration.rows, configuration.columns,
                  configuration.inarow, list(observation.board))

    # Solo sustituimos prefer_center si encontramos una jugada claramente mejor
    window_scores = _count_open_windows(board, observation.mark)
    if not window_scores:
        return tool_result

    best_col = max(window_scores, key=window_scores.get)
    best_score = window_scores[best_col]
    center_score = window_scores.get(tool_result, 0)

    # Preferimos la jugada con más ventanas abiertas solo si supera al centro por margen claro
    if best_score > center_score + 2:
        return best_col

    return tool_result
