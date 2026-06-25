from __future__ import annotations

import random
from dataclasses import dataclass, field


BOARD_SIZE = 4
TARGET_TILE = 2048


def _merge_line(values: list[int]) -> tuple[list[int], int]:
    compacted = [value for value in values if value != 0]
    merged: list[int] = []
    score_gain = 0
    index = 0

    while index < len(compacted):
        current = compacted[index]
        next_value = compacted[index + 1] if index + 1 < len(compacted) else None
        if next_value == current:
            doubled = current * 2
            merged.append(doubled)
            score_gain += doubled
            index += 2
        else:
            merged.append(current)
            index += 1

    merged.extend([0] * (BOARD_SIZE - len(merged)))
    return merged, score_gain


@dataclass
class Game2048:
    board: list[list[int]] = field(default_factory=lambda: [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)])
    score: int = 0
    won: bool = False
    over: bool = False

    def __post_init__(self) -> None:
        if self.is_empty():
            self.reset()

    def reset(self) -> None:
        self.board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.score = 0
        self.won = False
        self.over = False
        self._spawn_tile()
        self._spawn_tile()

    def is_empty(self) -> bool:
        return all(value == 0 for row in self.board for value in row)

    def _empty_cells(self) -> list[tuple[int, int]]:
        return [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE) if self.board[row][col] == 0]

    def _spawn_tile(self) -> bool:
        empty_cells = self._empty_cells()
        if not empty_cells:
            return False
        row, col = random.choice(empty_cells)
        self.board[row][col] = 4 if random.random() < 0.1 else 2
        return True

    def _has_target(self) -> bool:
        return any(value >= TARGET_TILE for row in self.board for value in row)

    def _can_move(self) -> bool:
        if self._empty_cells():
            return True
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = self.board[row][col]
                if row + 1 < BOARD_SIZE and self.board[row + 1][col] == value:
                    return True
                if col + 1 < BOARD_SIZE and self.board[row][col + 1] == value:
                    return True
        return False

    def move(self, direction: str) -> bool:
        if self.over:
            return False

        original_board = [row[:] for row in self.board]
        total_gain = 0

        if direction == "left":
            new_board = []
            for row in self.board:
                merged_row, gain = _merge_line(row)
                new_board.append(merged_row)
                total_gain += gain
            self.board = new_board
        elif direction == "right":
            new_board = []
            for row in self.board:
                merged_row, gain = _merge_line(list(reversed(row)))
                new_board.append(list(reversed(merged_row)))
                total_gain += gain
            self.board = new_board
        elif direction == "up":
            columns = list(zip(*self.board))
            merged_columns = []
            for column in columns:
                merged_column, gain = _merge_line(list(column))
                merged_columns.append(merged_column)
                total_gain += gain
            self.board = [list(row) for row in zip(*merged_columns)]
        elif direction == "down":
            columns = list(zip(*self.board))
            merged_columns = []
            for column in columns:
                merged_column, gain = _merge_line(list(reversed(column)))
                merged_columns.append(list(reversed(merged_column)))
                total_gain += gain
            self.board = [list(row) for row in zip(*merged_columns)]
        else:
            raise ValueError(f"Unsupported direction: {direction}")

        moved = self.board != original_board
        if moved:
            self.score += total_gain
            self._spawn_tile()
            if self._has_target():
                self.won = True
            self.over = not self._can_move()
        return moved
