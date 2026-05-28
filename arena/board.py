from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Board:
    rows: int = 6
    cols: int = 7
    inarow: int = 4
    grid: Optional[List[int]] = None

    def __post_init__(self):
        if self.grid is None:
            self.grid = [0] * (self.rows * self.cols)

    def copy(self):
        return Board(self.rows, self.cols, self.inarow, self.grid[:])

    def drop_piece(self, col: int, mark: int) -> bool:
        if col < 0 or col >= self.cols:
            return False
        for row in range(self.rows - 1, -1, -1):
            idx = row * self.cols + col
            if self.grid[idx] == 0:
                self.grid[idx] = mark
                return True
        return False

    def is_column_full(self, col: int) -> bool:
        return self.grid[col] != 0

    def valid_moves(self) -> List[int]:
        return [c for c in range(self.cols) if not self.is_column_full(c)]

    def check_win(self, mark: int) -> bool:
        def cell(r, c):
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return None
            return self.grid[r * self.cols + c]

        for r in range(self.rows):
            for c in range(self.cols):
                if cell(r, c) != mark:
                    continue
                for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    count = 0
                    rr, cc = r, c
                    while cell(rr, cc) == mark:
                        count += 1
                        if count >= self.inarow:
                            return True
                        rr += dr
                        cc += dc
                        if rr < 0 or rr >= self.rows or cc < 0 or cc >= self.cols:
                            break
        return False

    def is_full(self) -> bool:
        return all(self.grid[c] != 0 for c in range(self.cols))

    def to_observation(self, mark: int):
        class Observation:
            def __init__(self, board, mark):
                self.board = board
                self.mark = mark
        return Observation(self.grid.copy(), mark)
