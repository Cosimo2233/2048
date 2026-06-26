# 2048 Python GUI

一个使用 Python 和 `tkinter` 编写的 2048 小游戏，带图形界面、弹性动画和合成音效。

## 下载

前往 [Releases](../../releases) 页面下载 `2048.exe`，双击即可运行，无需安装 Python。

## 从源码运行

1. 创建虚拟环境：
   ```bash
   python -m venv .venv
   ```
2. 激活虚拟环境：
   ```bash
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # Windows CMD
   .venv\Scripts\activate.bat
   ```
3. 启动游戏：
   ```bash
   python main.py
   ```

## 操作说明

| 按键 | 操作 |
|------|------|
| `↑` `↓` `←` `→` 或 `W` `A` `S` `D` | 移动方块 |
| `R` | 重新开始 |

目标是合成 **2048**！

## 功能

- 🎮 经典 2048 玩法
- ✨ 方块移动和合并的弹性动画
- 🔊 合成音效（仅 Windows）
- 💾 本地最高分记录
- 🎨 经典配色方案

## 项目结构

```
├── main.py          # 图形界面与动画系统
├── game_logic.py    # 游戏核心逻辑
├── best_score.json  # 最高分记录（运行时自动生成）
└── dist/
    └── 2048.exe     # 打包后的可执行文件
```

## 技术栈

- Python 3
- tkinter（GUI）
- winsound（音效，仅 Windows）

## 打包

使用 PyInstaller 打包为单文件可执行程序：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name 2048 --hidden-import tkinter main.py
```

打包产物位于 `dist/2048.exe`。
