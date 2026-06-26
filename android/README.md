# 2048 Android 版

使用 Kivy 框架编写的 2048 安卓版，支持触摸滑动操作和合成音效。

## 环境要求

- **Linux** 或 **WSL**（Windows 子系统 Linux）
- Python 3.10+
- Java JDK 17
- Android SDK / NDK（由 Buildozer 自动下载）

## 构建步骤

### 1. 安装系统依赖（Ubuntu/Debian）

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
    git zip unzip openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev
```

### 2. 创建虚拟环境并安装 Buildozer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install buildozer cython
```

### 3. 构建 APK

```bash
cd android
buildozer android debug
```

首次构建会自动下载 Android SDK/NDK，耗时较长（30 分钟以上）。构建完成后 APK 位于：

```
bin/game2048-1.0.0-debug.apk
```

### 4. 安装到手机

```bash
buildozer android debug deploy run
```

或直接将 APK 传到手机安装。

## 操作方式

- **上滑 / 下滑 / 左滑 / 右滑**：移动方块
- 点击 **重新开始** 重置游戏
