"""2048 — Kivy 版本，支持安卓打包。"""

from __future__ import annotations

import math
import os
import wave
import struct
import io

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from game_logic import BOARD_SIZE, Game2048, MovePreview

# ── 配色 ──────────────────────────────────────────────────────────────
TILE_COLORS: dict[int, tuple[float, float, float, float]] = {
    0:    (0.804, 0.757, 0.706, 1),
    2:    (0.933, 0.894, 0.855, 1),
    4:    (0.929, 0.878, 0.784, 1),
    8:    (0.949, 0.694, 0.475, 1),
    16:   (0.961, 0.584, 0.388, 1),
    32:   (0.965, 0.486, 0.373, 1),
    64:   (0.965, 0.369, 0.231, 1),
    128:  (0.929, 0.812, 0.447, 1),
    256:  (0.929, 0.800, 0.380, 1),
    512:  (0.929, 0.784, 0.314, 1),
    1024: (0.929, 0.773, 0.247, 1),
    2048: (0.929, 0.761, 0.180, 1),
}

TEXT_COLORS: dict[int, tuple[float, float, float, float]] = {
    0:    (0.467, 0.431, 0.396, 1),
    2:    (0.467, 0.431, 0.396, 1),
    4:    (0.467, 0.431, 0.396, 1),
}
DEFAULT_TEXT_COLOR = (0.976, 0.965, 0.949, 1)


def _to_rgba(color: tuple[float, ...]) -> tuple[float, ...]:
    return color


def _blend_color(
    c1: tuple[float, float, float, float],
    c2: tuple[float, float, float, float],
    t: float,
) -> tuple[float, float, float, float]:
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))


# ── 音效管理 ─────────────────────────────────────────────────────────
class SoundManager:
    def __init__(self) -> None:
        self._merge_sound = None
        self._init_sound()

    def _init_sound(self) -> None:
        try:
            path = self._generate_wav()
            self._merge_sound = SoundLoader.load(path)
            if self._merge_sound:
                self._merge_sound.volume = 0.5
        except Exception:
            self._merge_sound = None

    @staticmethod
    def _generate_wav() -> str:
        sample_rate = 44100
        duration = 0.12
        total_samples = int(sample_rate * duration)
        frequencies = [523.25, 659.25, 783.99]
        samples: list[float] = []

        for i in range(total_samples):
            t = i / sample_rate
            envelope = math.exp(-t * 18)
            value = sum(math.sin(2.0 * math.pi * f * t) for f in frequencies) * envelope * 0.25
            samples.append(value)

        path = os.path.join(os.path.dirname(__file__), "merge.wav")
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(struct.pack("<h", int(s * 32767)) for s in samples))
        return path

    def play_merge(self) -> None:
        if self._merge_sound:
            self._merge_sound.stop()
            self._merge_sound.play()


# ── 游戏画布 ──────────────────────────────────────────────────────────
class GameCanvas(Widget):
    board_data = ListProperty([[0] * BOARD_SIZE for _ in range(BOARD_SIZE)])
    flash_cells = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)
        self.bind(board_data=self._draw, flash_cells=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(0.733, 0.678, 0.627, 1)
            Rectangle(pos=self.pos, size=self.size)

        gap = 8
        board_size_px = min(self.width, self.height)
        tile_size = (board_size_px - gap * (BOARD_SIZE + 1)) / BOARD_SIZE
        x_offset = self.x + (self.width - board_size_px) / 2
        y_offset = self.y + (self.height - board_size_px) / 2

        flash_map = {(c[0], c[1]): c[2] for c in self.flash_cells}

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = self.board_data[row][col]
                x = x_offset + gap + col * (tile_size + gap)
                y = y_offset + gap + (BOARD_SIZE - 1 - row) * (tile_size + gap)

                is_flash = (row, col) in flash_map
                scale = flash_map.get((row, col), 1.0)

                tile_color = TILE_COLORS.get(value, (0.235, 0.227, 0.200, 1))
                if is_flash:
                    tile_color = _blend_color(tile_color, (1.0, 0.945, 0.722, 1), 0.5)

                actual_size = tile_size * scale
                dx = (tile_size - actual_size) / 2
                dy = (tile_size - actual_size) / 2

                with self.canvas:
                    Color(*tile_color)
                    RoundedRectangle(
                        pos=(x + dx, y + dy),
                        size=(actual_size, actual_size),
                        radius=[6],
                    )

                if value:
                    text_color = TEXT_COLORS.get(value, DEFAULT_TEXT_COLOR)
                    font_size = actual_size * 0.38
                    if value >= 100:
                        font_size *= 0.82
                    if value >= 1000:
                        font_size *= 0.75

                    lbl = Label(
                        text=str(value),
                        font_size=font_size,
                        bold=True,
                        color=text_color,
                        pos=(x + dx, y + dy),
                        size=(actual_size, actual_size),
                        halign="center",
                        valign="middle",
                    )
                    lbl.text_size = (actual_size, actual_size)
                    self.canvas.add(Color(*text_color))
                    self.add_widget(lbl)
                    # Note: labels added this way won't persist across redraws;
                    # we rely on canvas drawing for visual consistency.


# ── 顶层 UI ──────────────────────────────────────────────────────────
class GameRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.game = Game2048()
        self.sound = SoundManager()
        self.animating = False
        self.swipe_start = None

        # 顶部信息
        self.info_label = Label(
            text="滑动操作 | 目标: 2048",
            font_size=16,
            size_hint_y=0.08,
            color=(0.467, 0.431, 0.396, 1),
        )
        self.add_widget(self.info_label)

        # 分数
        self.score_label = Label(
            text=f"分数: {self.game.score}",
            font_size=20,
            bold=True,
            size_hint_y=0.08,
            color=(0.467, 0.431, 0.396, 1),
        )
        self.add_widget(self.score_label)

        # 游戏画布
        self.canvas_widget = GameCanvas(size_hint_y=0.74)
        self.add_widget(self.canvas_widget)

        # 重新开始按钮
        self.restart_btn = Label(
            text="[ref=restart]重新开始[/ref]",
            markup=True,
            font_size=18,
            size_hint_y=0.10,
            color=(0.561, 0.478, 0.400, 1),
        )
        self.restart_btn.bind(on_ref_press=self._restart)
        self.add_widget(self.restart_btn)

        self._sync_board()

    def _sync_board(self):
        self.canvas_widget.board_data = [row[:] for row in self.game.board]
        self.score_label.text = f"分数: {self.game.score}"

        if self.game.over:
            self.info_label.text = "游戏结束！点击重新开始"
        elif self.game.won:
            self.info_label.text = "已达成 2048！继续挑战更高分"
        else:
            self.info_label.text = "滑动操作 | 目标: 2048"

    def _restart(self, *args):
        self.game.reset()
        self._sync_board()

    # ── 触摸滑动 ──────────────────────────────────────────────────
    def on_touch_down(self, touch):
        if self.canvas_widget.collide_point(*touch.pos):
            self.swipe_start = (touch.x, touch.y)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.swipe_start is None or self.animating:
            return super().on_touch_up(touch)

        dx = touch.x - self.swipe_start[0]
        dy = touch.y - self.swipe_start[1]
        self.swipe_start = None

        threshold = 30
        if abs(dx) < threshold and abs(dy) < threshold:
            return super().on_touch_up(touch)

        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "up" if dy > 0 else "down"

        self._do_move(direction)
        return super().on_touch_up(touch)

    def _do_move(self, direction: str):
        preview = self.game.preview_move(direction)
        if not preview.moved:
            return

        has_merge = any(m.merged for m in preview.tile_moves)
        self.game.move(direction)

        if has_merge:
            self.sound.play_merge()

        self._sync_board()


# ── App ───────────────────────────────────────────────────────────────
class Game2048App(App):
    title = "2048"

    def build(self):
        return GameRoot()


if __name__ == "__main__":
    Game2048App().run()
