from __future__ import annotations

import tkinter as tk

from game_logic import BOARD_SIZE, Game2048


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


class Game2048App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("2048")
        self.configure(bg="#faf8ef")
        self.resizable(False, False)

        self.game = Game2048()

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

        self.score_frame = tk.Frame(self.header_frame, bg="#bbada0", padx=14, pady=8)
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

    def restart(self) -> None:
        self.game.reset()
        self.refresh()
        self.canvas.focus_set()

    def on_keypress(self, event: tk.Event) -> None:
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
        if direction and self.game.move(direction):
            self.refresh()

    def refresh(self) -> None:
        self.score_label.config(text=str(self.game.score))
        if self.game.over:
            self.status_label.config(text="游戏结束，按重新开始重新挑战")
        elif self.game.won:
            self.status_label.config(text="已达成 2048，可以继续挑战更高分")
        else:
            self.status_label.config(text="")
        self.draw_board()

    def draw_board(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.canvas_size, self.canvas_size, fill="#bbada0", outline="#bbada0")

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = self.game.board[row][col]
                x1 = self.tile_gap + col * (self.tile_size + self.tile_gap)
                y1 = self.tile_gap + row * (self.tile_size + self.tile_gap)
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size
                fill = TILE_COLORS.get(value, "#3c3a32") if value else TILE_COLORS[0]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=fill, width=2)
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


def main() -> None:
    app = Game2048App()
    app.mainloop()


if __name__ == "__main__":
    main()
