# 🎬 B站视频转录工具 (Bili Transcribe)

一键下载B站视频、提取音频、AI语音转录生成逐字稿。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 功能特点

- ✅ **智能识别** - 支持B站短链接、长链接、BV号自动识别
- ✅ **自动下载** - 使用BBDown高速下载视频
- ✅ **AI转录** - 基于OpenAI Whisper的语音识别
- ✅ **多格式输出** - TXT纯文本、JSON数据、SRT字幕、Markdown报告
- ✅ **多语言支持** - 中文、英文等多种语言
- ✅ **Docker支持** - 零环境依赖，开箱即用

## 🚀 快速开始

### 方式1：Docker（推荐，零依赖）

```bash
# 直接运行（自动下载镜像）
docker run -v $(pwd)/output:/app/output \
  ghcr.io/taylorzhou16/bili-transcribe \
  "https://b23.tv/xxxxx"

# 或者自己构建
git clone https://github.com/taylorzhou16/bili-transcribe.git
cd bili-transcribe
docker build -t bili-transcribe .
docker run -v $(pwd)/output:/app/output bili-transcribe "BVxxxxx"
```

### 方式2：本地安装

**前置依赖：**
- Python 3.8+
- [BBDown](https://github.com/nilaoda/BBDown) - B站视频下载
- ffmpeg - 音视频处理

**安装：**

```bash
# macOS
brew install bbdown ffmpeg
pip install openai-whisper

# Ubuntu/Debian
sudo apt install ffmpeg
# 下载BBDown二进制并放入PATH
pip install openai-whisper

# 克隆仓库
git clone https://github.com/taylorzhou16/bili-transcribe.git
cd bili-transcribe
```

**使用：**

```bash
# 基本用法
python bili_transcribe.py https://b23.tv/LYMUM5G

# 使用更快的模型
python bili_transcribe.py BV19NfJBoEDm --model small

# 保留视频文件
python bili_transcribe.py BV19NfJBoEDm --keep-video

# 英文视频
python bili_transcribe.py BVxxxx --language en
```

## 📋 输出文件

转录完成后会在 `output/` 目录生成：

| 文件 | 说明 |
|------|------|
| `BVxxxx.txt` | 纯文本逐字稿 |
| `BVxxxx.json` | 完整JSON数据（含时间戳、置信度） |
| `BVxxxx.srt` | SRT格式字幕文件 |
| `BVxxxx.md` | Markdown格式报告（带时间戳） |

## 🔧 模型选择

Whisper模型越大准确率越高，但速度越慢：

| 模型 | 显存需求 | 速度 | 准确率 | 推荐场景 |
|------|----------|------|--------|----------|
| tiny | ~1GB | 最快 | 一般 | 快速测试 |
| base | ~1GB | 快 | 较好 | 短视频 |
| small | ~2GB | 中等 | 好 | 日常使用 ⭐ |
| medium | ~5GB | 较慢 | 很好 | 长视频 |
| large | ~10GB | 最慢 | 最好 | 高精度需求 |

默认使用 `small` 模型（平衡速度和准确度）。

## 📝 命令行参数

```
usage: bili_transcribe.py [-h] [--model {tiny,base,small,medium,large}]
                          [--language LANGUAGE] [--output-dir OUTPUT_DIR]
                          [--keep-video] [--skip-download]
                          url

位置参数:
  url                   B站视频URL或BV号

可选参数:
  -h, --help            显示帮助信息
  --model {tiny,base,small,medium,large}
                        Whisper模型大小 (默认: small)
  --language LANGUAGE   视频语言 (默认: zh, 中文)
  --output-dir OUTPUT_DIR
                        输出目录 (默认: ./output)
  --keep-video          保留下载的视频文件
  --skip-download       跳过下载步骤(使用已有视频)
```

## 🤖 Claude Code Skill

本项目支持作为 [Claude Code](https://claude.ai/code) 的Skill使用：

```bash
# 添加Skill
claude config set skills.bili-transcribe \
  "https://raw.githubusercontent.com/taylorzhou16/bili-transcribe/main/skill.json"

# 然后在Claude中使用
/bili-transcribe https://b23.tv/xxxxx
```

## 🛠️ 技术栈

- **Python 3.8+** - 核心语言
- **BBDown** - B站视频下载工具
- **ffmpeg** - 音视频处理
- **OpenAI Whisper** - 语音识别模型

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [BBDown](https://github.com/nilaoda/BBDown) - 强大的B站下载工具
- [OpenAI Whisper](https://github.com/openai/whisper) - 开源语音识别模型
- [ffmpeg](https://ffmpeg.org/) - 音视频处理神器

## 💬 反馈

如有问题或建议，欢迎提交 [Issue](https://github.com/taylorzhou16/bili-transcribe/issues) 或 [Pull Request](https://github.com/taylorzhou16/bili-transcribe/pulls)。
