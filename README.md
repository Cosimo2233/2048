# 2048 Python GUI

一个使用 Python 编写的 2048 小游戏，支持 Windows 桌面版和安卓版，带弹性动画和合成音效。

## 下载

前往 [Releases](../../releases) 页面下载：

| 平台 | 文件 | 说明 |
|------|------|------|
| Windows | `2048.exe` | 双击即玩，无需 Python |
| Android | `game2048-debug.apk` | 需自行构建，见下方说明 |

## 从源码运行（Windows）

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 启动游戏：
   ```bash
   python main.py
   ```

## 构建安卓版

安卓版使用 Kivy 框架，需在 **Linux 或 WSL** 环境下构建。详见 [android/README.md](android/README.md)。

快速步骤：

```bash
cd android
pip install buildozer cython
buildozer android debug
```

构建产物：`android/bin/game2048-1.0.0-debug.apk`

## 操作说明

### Windows 版

| 按键 | 操作 |
|------|------|
| `↑` `↓` `←` `→` 或 `W` `A` `S` `D` | 移动方块 |
| `R` | 重新开始 |

### 安卓版

- 上滑 / 下滑 / 左滑 / 右滑移动方块
- 点击「重新开始」重置游戏

目标是合成 **2048**！

## 功能

- 🎮 经典 2048 玩法
- ✨ 方块移动和合并的弹性动画
- 🔊 合成音效
- 💾 本地最高分记录
- 🎨 经典配色方案
- 📱 支持 Windows 和 Android 平台

## 项目结构

```
├── main.py              # Windows 版（tkinter）
├── game_logic.py        # 游戏核心逻辑（共用）
├── icon.ico             # 应用图标
├── requirements.txt     # Python 依赖
├── best_score.json      # 最高分记录（运行时自动生成）
├── dist/
│   └── 2048.exe         # Windows 打包产物
└── android/
    ├── main.py          # 安卓版（Kivy）
    ├── game_logic.py    # 游戏核心逻辑（共用）
    ├── buildozer.spec   # 安卓构建配置
    └── README.md        # 安卓构建说明
```

## 技术栈

- **Windows 版**：Python 3 + tkinter + winsound
- **安卓版**：Python 3 + Kivy + Buildozer

## 打包 Windows 版

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name 2048 --icon icon.ico --hidden-import tkinter main.py
```

产物位于 `dist/2048.exe`。
