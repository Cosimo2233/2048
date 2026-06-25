from __future__ import annotations

import random
from dataclasses import dataclass, field


BOARD_SIZE = 4
TARGET_TILE = 2048


@dataclass(frozen=True)
class TileMove:
    value: int
    source_row: int
    source_col: int
    target_row: int
    target_col: int
    merged: bool = False


@dataclass(frozen=True)
class MovePreview:
    board: list[list[int]]
    score_gain: int
    moved: bool
    tile_moves: list[TileMove]


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


def _build_line_preview(
    line_positions: list[tuple[int, int]],
    line_values: list[int],
) -> tuple[list[int], int, list[TileMove]]:
    compacted = [(value, row, col) for value, (row, col) in zip(line_values, line_positions) if value != 0]
    destination_values: list[int] = []
    tile_moves: list[TileMove] = []
    score_gain = 0
    index = 0

    while index < len(compacted):
        current_value, current_row, current_col = compacted[index]
        next_item = compacted[index + 1] if index + 1 < len(compacted) else None
        destination_index = len(destination_values)
        destination_row, destination_col = line_positions[destination_index]

        if next_item is not None and next_item[0] == current_value:
            next_value, next_row, next_col = next_item
            doubled = current_value * 2
            destination_values.append(doubled)
            tile_moves.append(
                TileMove(current_value, current_row, current_col, destination_row, destination_col, True)
            )
            tile_moves.append(TileMove(next_value, next_row, next_col, destination_row, destination_col, True))
            score_gain += doubled
            index += 2
        else:
            destination_values.append(current_value)
            tile_moves.append(TileMove(current_value, current_row, current_col, destination_row, destination_col, False))
            index += 1

    destination_values.extend([0] * (BOARD_SIZE - len(destination_values)))
    return destination_values, score_gain, tile_moves


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

    def preview_move(self, direction: str) -> MovePreview:
        board = [row[:] for row in self.board]
        total_gain = 0
        tile_moves: list[TileMove] = []

        if direction == "left":
            preview_board: list[list[int]] = []
            for row_index, row in enumerate(board):
                line_positions = [(row_index, col_index) for col_index in range(BOARD_SIZE)]
                line_values, gain, line_moves = _build_line_preview(line_positions, row)
                preview_board.append(line_values)
                total_gain += gain
                tile_moves.extend(line_moves)
        elif direction == "right":
            preview_board = []
            for row_index, row in enumerate(board):
                line_positions = [(row_index, col_index) for col_index in range(BOARD_SIZE - 1, -1, -1)]
                line_values, gain, line_moves = _build_line_preview(line_positions, list(reversed(row)))
                preview_board.append(list(reversed(line_values)))
                total_gain += gain
                tile_moves.extend(line_moves)
        elif direction == "up":
            columns = list(zip(*board))
            preview_columns: list[list[int]] = []
            for col_index, column in enumerate(columns):
                line_positions = [(row_index, col_index) for row_index in range(BOARD_SIZE)]
                line_values, gain, line_moves = _build_line_preview(line_positions, list(column))
                preview_columns.append(line_values)
                total_gain += gain
                tile_moves.extend(line_moves)
            preview_board = [list(row) for row in zip(*preview_columns)]
        elif direction == "down":
            columns = list(zip(*board))
            preview_columns = []
            for col_index, column in enumerate(columns):
                line_positions = [(row_index, col_index) for row_index in range(BOARD_SIZE - 1, -1, -1)]
                line_values, gain, line_moves = _build_line_preview(line_positions, list(reversed(column)))
                preview_columns.append(list(reversed(line_values)))
                total_gain += gain
                tile_moves.extend(line_moves)
            preview_board = [list(row) for row in zip(*preview_columns)]
        else:
            raise ValueError(f"Unsupported direction: {direction}")

        moved = preview_board != board
        return MovePreview(board=preview_board, score_gain=total_gain, moved=moved, tile_moves=tile_moves)

    def move(self, direction: str) -> bool:
        if self.over:
            return False

        preview = self.preview_move(direction)
        if not preview.moved:
            return False

        self.board = [row[:] for row in preview.board]
        self.score += preview.score_gain
        self._spawn_tile()
        if self._has_target():
            self.won = True
        self.over = not self._can_move()
        return True
