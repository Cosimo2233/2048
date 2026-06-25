from __future__ import annotations

import json
import math
from pathlib import Path
import tkinter as tk

from game_logic import BOARD_SIZE, Game2048, MovePreview


ROOT_DIR = Path(__file__).resolve().parent
BEST_SCORE_FILE = ROOT_DIR / "best_score.json"

TILE_COLORS = {
    0: "#cdc1b4",
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
}

TEXT_COLORS = {
    0: "#776e65",
    2: "#776e65",
    4: "#776e65",
}


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def ease_out_cubic(progress: float) -> float:
    return 1 - pow(1 - progress, 3)


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    return f"#{red:02x}{green:02x}{blue:02x}"


def blend_channel(start: int, end: int, amount: float) -> int:
    return int(start + (end - start) * amount)


def blend_hex(start_hex: str, end_hex: str, amount: float) -> str:
    start_hex = start_hex.lstrip("#")
    end_hex = end_hex.lstrip("#")
    start_red, start_green, start_blue = (int(start_hex[index:index + 2], 16) for index in (0, 2, 4))
    end_red, end_green, end_blue = (int(end_hex[index:index + 2], 16) for index in (0, 2, 4))
    return rgb_to_hex(
        blend_channel(start_red, end_red, amount),
        blend_channel(start_green, end_green, amount),
        blend_channel(start_blue, end_blue, amount),
    )


class Game2048App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("2048")
        self.configure(bg="#faf8ef")
        self.resizable(False, False)

        self.game = Game2048()
        self.best_score = self.load_best_score()
        self.animation_running = False
        self.animation_jobs: list[str] = []
        self.pending_preview: MovePreview | None = None
        self.pending_old_board: list[list[int]] | None = None
        self.pending_spawn_cell: tuple[int, int] | None = None
        self.pending_spawn_value: int | None = None
        self.pulse_phase = 0.0

        self.header_frame = tk.Frame(self, bg="#faf8ef")
        self.header_frame.pack(fill="x", padx=18, pady=(18, 8))

        self.title_label = tk.Label(
            self.header_frame,
            text="2048",
            font=("Segoe UI", 28, "bold"),
            bg="#faf8ef",
            fg="#776e65",
        )
        self.title_label.pack(side="left")

        self.score_panel = tk.Frame(self.header_frame, bg="#faf8ef")
        self.score_panel.pack(side="right")

        self.best_score_frame = tk.Frame(self.score_panel, bg="#8f7a66", padx=14, pady=8)
        self.best_score_frame.pack(side="right", padx=(8, 0))
        self.best_score_label = tk.Label(
            self.best_score_frame,
            text=str(self.best_score),
            font=("Segoe UI", 18, "bold"),
            bg="#8f7a66",
            fg="#ffffff",
        )
        self.best_score_label.pack()
        self.best_score_caption = tk.Label(
            self.best_score_frame,
            text="BEST",
            font=("Segoe UI", 8, "bold"),
            bg="#8f7a66",
            fg="#eee4da",
        )
        self.best_score_caption.pack()

        self.score_frame = tk.Frame(self.score_panel, bg="#bbada0", padx=14, pady=8)
        self.score_frame.pack(side="right")
        self.score_label = tk.Label(
            self.score_frame,
            text="0",
            font=("Segoe UI", 18, "bold"),
            bg="#bbada0",
            fg="#ffffff",
        )
        self.score_label.pack()
        self.score_caption = tk.Label(
            self.score_frame,
            text="SCORE",
            font=("Segoe UI", 8, "bold"),
            bg="#bbada0",
            fg="#eee4da",
        )
        self.score_caption.pack()

        self.info_label = tk.Label(
            self,
            text="方向键或 WASD 操作，按 R 重开",
            font=("Segoe UI", 10),
            bg="#faf8ef",
            fg="#776e65",
        )
        self.info_label.pack(anchor="w", padx=20, pady=(0, 8))

        self.canvas_size = 420
        self.tile_gap = 12
        self.tile_size = (self.canvas_size - self.tile_gap * (BOARD_SIZE + 1)) / BOARD_SIZE
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="#bbada0", highlightthickness=0)
        self.canvas.pack(padx=18, pady=(0, 18))

        self.status_label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg="#faf8ef",
            fg="#8f7a66",
        )
        self.status_label.pack(pady=(0, 10))

        self.restart_button = tk.Button(
            self,
            text="重新开始",
            font=("Segoe UI", 10, "bold"),
            command=self.restart,
            relief="flat",
            bg="#8f7a66",
            fg="#ffffff",
            activebackground="#9f8b77",
            activeforeground="#ffffff",
            padx=12,
            pady=6,
        )
        self.restart_button.pack(pady=(0, 18))

        self.bind_all("<KeyPress>", self.on_keypress)
        self.canvas.focus_set()
        self.refresh()
        self.animate_pulse()

    def load_best_score(self) -> int:
        if not BEST_SCORE_FILE.exists():
            return 0
        try:
            data = json.loads(BEST_SCORE_FILE.read_text(encoding="utf-8"))
            return int(data.get("best_score", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return 0

    def save_best_score(self) -> None:
        try:
            BEST_SCORE_FILE.write_text(
                json.dumps({"best_score": self.best_score}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def restart(self) -> None:
        self.cancel_animation()
        self.game.reset()
        self.refresh()
        self.canvas.focus_set()

    def cancel_animation(self) -> None:
        self.animation_running = False
        while self.animation_jobs:
            job_id = self.animation_jobs.pop()
            try:
                self.after_cancel(job_id)
            except tk.TclError:
                pass

    def on_keypress(self, event: tk.Event) -> None:
        if self.animation_running:
            return

        key = event.keysym.lower()
        direction_map = {
            "left": "left",
            "a": "left",
            "right": "right",
            "d": "right",
            "up": "up",
            "w": "up",
            "down": "down",
            "s": "down",
        }

        if key == "r":
            self.restart()
            return

        direction = direction_map.get(key)
        if direction:
            self.start_move_animation(direction)

    def start_move_animation(self, direction: str) -> None:
        preview = self.game.preview_move(direction)
        if not preview.moved:
            return

        self.pending_preview = preview
        self.pending_old_board = [row[:] for row in self.game.board]
        self.animation_running = True

        self.game.move(direction)
        self.pending_spawn_cell, self.pending_spawn_value = self.detect_spawn_tile(preview.board, self.game.board)
        self.update_best_score()
        self.animate_move_frame(0)

    def detect_spawn_tile(self, before_board: list[list[int]], after_board: list[list[int]]) -> tuple[tuple[int, int] | None, int | None]:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if before_board[row][col] == 0 and after_board[row][col] != 0:
                    return (row, col), after_board[row][col]
        return None, None

    def update_best_score(self) -> None:
        if self.game.score > self.best_score:
            self.best_score = self.game.score
            self.best_score_label.config(text=str(self.best_score))
            self.save_best_score()

    def refresh(self) -> None:
        self.score_label.config(text=str(self.game.score))
        self.best_score_label.config(text=str(self.best_score))
        if self.game.over:
            self.status_label.config(text="游戏结束，按重新开始重新挑战")
        elif self.game.won:
            self.status_label.config(text="已达成 2048，可以继续挑战更高分")
        else:
            self.status_label.config(text="")
        self.draw_board(self.game.board)

    def cell_bounds(self, row: int, col: int) -> tuple[float, float, float, float]:
        x1 = self.tile_gap + col * (self.tile_size + self.tile_gap)
        y1 = self.tile_gap + row * (self.tile_size + self.tile_gap)
        x2 = x1 + self.tile_size
        y2 = y1 + self.tile_size
        return x1, y1, x2, y2

    def rounded_tile(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        fill: str,
        outline: str | None = None,
        outline_width: int = 1,
        radius: float = 18,
    ) -> None:
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            fill=fill,
            outline=outline or fill,
            width=outline_width,
        )

    def draw_overlay_tile(self, tile: dict[str, float]) -> None:
        x1 = tile["x"]
        y1 = tile["y"]
        size = tile["size"]
        value = int(tile["value"])
        scale = tile["scale"]

        scaled_size = size * scale
        center_x = x1 + size / 2
        center_y = y1 + size / 2
        left = center_x - scaled_size / 2
        top = center_y - scaled_size / 2
        right = center_x + scaled_size / 2
        bottom = center_y + scaled_size / 2

        fill = TILE_COLORS.get(value, "#3c3a32")
        self.rounded_tile(left, top, right, bottom, fill=fill, outline=fill, outline_width=2, radius=18 * scale)
        font_size = 32 if value < 128 else 28 if value < 1024 else 22
        font_size = int(clamp(font_size * scale, 12, font_size))
        text_color = TEXT_COLORS.get(value, "#f9f6f2")
        self.canvas.create_text(
            center_x,
            center_y,
            text=str(value),
            fill=text_color,
            font=("Segoe UI", font_size, "bold"),
        )

    def draw_board(
        self,
        board: list[list[int]],
        overlay_tiles: list[dict[str, float]] | None = None,
        ghost_highlight: tuple[int, int] | None = None,
    ) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.canvas_size, self.canvas_size, fill="#bbada0", outline="#bbada0")

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = board[row][col]
                x1, y1, x2, y2 = self.cell_bounds(row, col)
                fill = TILE_COLORS.get(value, "#3c3a32") if value else TILE_COLORS[0]
                self.rounded_tile(x1, y1, x2, y2, fill=fill)
                if value:
                    font_size = 32 if value < 128 else 28 if value < 1024 else 22
                    text_color = TEXT_COLORS.get(value, "#f9f6f2")
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=str(value),
                        fill=text_color,
                        font=("Segoe UI", font_size, "bold"),
                    )

        if ghost_highlight is not None:
            row, col = ghost_highlight
            x1, y1, x2, y2 = self.cell_bounds(row, col)
            self.rounded_tile(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill="#fff2b2", outline="#f7d36b", outline_width=2, radius=16)

        if overlay_tiles:
            for tile in overlay_tiles:
                self.draw_overlay_tile(tile)

        if self.game.over:
            self.canvas.create_rectangle(0, 0, self.canvas_size, self.canvas_size, fill="#faf8ef", stipple="gray50", outline="")
            self.canvas.create_text(
                self.canvas_size / 2,
                self.canvas_size / 2 - 20,
                text="游戏结束",
                fill="#776e65",
                font=("Segoe UI", 24, "bold"),
            )
            self.canvas.create_text(
                self.canvas_size / 2,
                self.canvas_size / 2 + 18,
                text="按重新开始再试一次",
                fill="#776e65",
                font=("Segoe UI", 12),
            )

    def animate_move_frame(self, frame: int) -> None:
        if not self.pending_preview or self.pending_old_board is None:
            self.finish_animation()
            return

        total_frames = 10
        progress = ease_out_cubic(frame / total_frames)

        moving_sources = {
            (move.source_row, move.source_col)
            for move in self.pending_preview.tile_moves
            if (move.source_row, move.source_col) != (move.target_row, move.target_col)
        }

        masked_board = [row[:] for row in self.pending_old_board]
        for row, col in moving_sources:
            masked_board[row][col] = 0

        overlays: list[dict[str, float]] = []
        for move in self.pending_preview.tile_moves:
            if (move.source_row, move.source_col) == (move.target_row, move.target_col):
                continue
            start_x1, start_y1, _, _ = self.cell_bounds(move.source_row, move.source_col)
            end_x1, end_y1, _, _ = self.cell_bounds(move.target_row, move.target_col)
            current_x = start_x1 + (end_x1 - start_x1) * progress
            current_y = start_y1 + (end_y1 - start_y1) * progress
            overlays.append(
                {
                    "x": current_x,
                    "y": current_y,
                    "size": self.tile_size,
                    "value": float(move.value),
                    "scale": 1.0,
                }
            )

        self.draw_board(masked_board, overlays)

        if frame < total_frames:
            job_id = self.after(16, lambda: self.animate_move_frame(frame + 1))
            self.animation_jobs.append(job_id)
            return

        self.animate_spawn_frame(0)

    def animate_spawn_frame(self, frame: int) -> None:
        if self.pending_spawn_cell is None or self.pending_spawn_value is None:
            self.finish_animation()
            return

        total_frames = 7
        progress = ease_out_cubic(frame / total_frames)
        scale = 0.55 + 0.45 * progress

        row, col = self.pending_spawn_cell
        x1, y1, _, _ = self.cell_bounds(row, col)
        overlays = [
            {
                "x": x1,
                "y": y1,
                "size": self.tile_size,
                "value": float(self.pending_spawn_value),
                "scale": scale,
            }
        ]
        self.draw_board(self.game.board, overlays, ghost_highlight=self.pending_spawn_cell)

        if frame < total_frames:
            job_id = self.after(16, lambda: self.animate_spawn_frame(frame + 1))
            self.animation_jobs.append(job_id)
            return

        self.finish_animation()

    def finish_animation(self) -> None:
        self.animation_running = False
        self.pending_preview = None
        self.pending_old_board = None
        self.pending_spawn_cell = None
        self.pending_spawn_value = None
        self.refresh()
        self.canvas.focus_set()

    def animate_pulse(self) -> None:
        self.pulse_phase = (self.pulse_phase + 0.08) % math.tau
        accent_amount = 0.5 + 0.5 * math.sin(self.pulse_phase)
        title_color = blend_hex("#776e65", "#9a8f7d", accent_amount * 0.45)
        best_bg = blend_hex("#8f7a66", "#9f8d79", accent_amount * 0.25)
        self.title_label.config(fg=title_color)
        self.best_score_frame.config(bg=best_bg)
        self.best_score_label.config(bg=best_bg)
        self.best_score_caption.config(bg=best_bg)
        self.after(120, self.animate_pulse)


def main() -> None:
    app = Game2048App()
    app.mainloop()


if __name__ == "__main__":
    main()
