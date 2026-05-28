from random import choice


def valid_moves(board, columns):
    return [c for c in range(columns) if board[c] == 0]


def drop_piece(grid, col, mark, config):
    rows, cols = config.rows, config.columns
    next_grid = grid[:]
    for row in range(rows - 1, -1, -1):
        idx = row * cols + col
        if next_grid[idx] == 0:
            next_grid[idx] = mark
            return next_grid
    return next_grid


def is_win(board, col, mark, config):
    rows, cols, inarow = config.rows, config.columns, config.inarow
    board = drop_piece(board, col, mark, config)

    def cell(r, c):
        return board[r * cols + c]

    for r in range(rows):
        for c in range(cols):
            if cell(r, c) != mark:
                continue
            for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                count = 0
                rr, cc = r, c
                while 0 <= rr < rows and 0 <= cc < cols and cell(rr, cc) == mark:
                    count += 1
                    if count >= inarow:
                        return True
                    rr += dr
                    cc += dc
    return False


def my_agent(observation, configuration):
    board = observation.board
    mark = observation.mark
    opponent = 1 if mark == 2 else 2
    moves = valid_moves(board, configuration.columns)

    # 1) Ganar si se puede
    for col in moves:
        if is_win(board, col, mark, configuration):
            return col

    # 2) Bloquear al rival si gana en la siguiente
    for col in moves:
        if is_win(board, col, opponent, configuration):
            return col

    # 3) Preferir el centro
    center = configuration.columns // 2
    ordered = sorted(moves, key=lambda c: abs(c - center))
    return ordered[0] if ordered else choice(moves)
