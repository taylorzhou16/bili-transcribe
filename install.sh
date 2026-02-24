#!/bin/bash
# B站视频转录工具 - 安装脚本

set -e

echo "🚀 B站视频转录工具安装脚本"
echo "================================"

# 检查操作系统
OS=$(uname -s)
ARCH=$(uname -m)

echo "检测到系统: $OS $ARCH"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请先安装 Python3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查并安装ffmpeg
echo ""
echo "📦 检查ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg未安装，尝试安装..."

    if [ "$OS" = "Darwin" ]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ 请先安装Homebrew: https://brew.sh"
            exit 1
        fi
    elif [ "$OS" = "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            echo "❌ 无法自动安装ffmpeg，请手动安装"
            exit 1
        fi
    else
        echo "❌ 不支持的操作系统"
        exit 1
    fi
else
    echo "✅ ffmpeg已安装"
fi

# 安装BBDown
echo ""
echo "📦 检查BBDown..."
if ! command -v BBDown &> /dev/null; then
    echo "⚠️  BBDown未安装，尝试安装..."

    INSTALL_DIR="/usr/local/bin"
    if [ ! -w "$INSTALL_DIR" ]; then
        INSTALL_DIR="$HOME/bin"
        mkdir -p "$INSTALL_DIR"
    fi

    if [ "$OS" = "Darwin" ]; then
        if [ "$ARCH" = "arm64" ]; then
            BBDOWN_URL="https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_osx-arm64"
        else
            BBDOWN_URL="https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_osx-x64"
        fi
    elif [ "$OS" = "Linux" ]; then
        if [ "$ARCH" = "aarch64" ]; then
            BBDOWN_URL="https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_linux-arm64"
        else
            BBDOWN_URL="https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_linux-x64"
        fi
    fi

    echo "正在下载BBDown..."
    curl -L "$BBDOWN_URL" -o "$INSTALL_DIR/BBDown"
    chmod +x "$INSTALL_DIR/BBDown"
    echo "✅ BBDown已安装到 $INSTALL_DIR/BBDown"

    # 添加到PATH
    if [ "$INSTALL_DIR" = "$HOME/bin" ]; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.zshrc
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.bashrc
        export PATH="$INSTALL_DIR:$PATH"
    fi
else
    echo "✅ BBDown已安装"
fi

# 安装Python依赖
echo ""
echo "📦 安装Python依赖..."
pip3 install --user openai-whisper tqdm

echo ""
echo "================================"
echo "✅ 安装完成!"
echo "================================"
echo ""
echo "使用方法:"
echo "  python3 bili_transcribe.py <B站视频URL>"
echo ""
echo "示例:"
echo "  python3 bili_transcribe.py https://b23.tv/LYMUM5G"
echo "  python3 bili_transcribe.py BV19NfJBoEDm --model small"
echo ""
echo "查看帮助:"
echo "  python3 bili_transcribe.py --help"
echo ""
