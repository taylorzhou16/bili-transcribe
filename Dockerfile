FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装BBDown
RUN arch=$(dpkg --print-architecture) && \
    if [ "$arch" = "amd64" ]; then \
        wget -O /usr/local/bin/BBDown https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_linux-x64; \
    else \
        wget -O /usr/local/bin/BBDown https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_linux-arm64; \
    fi && \
    chmod +x /usr/local/bin/BBDown

# 安装Python依赖
RUN pip install --no-cache-dir openai-whisper tqdm

# 创建工作目录
WORKDIR /app

# 复制脚本
COPY bili_transcribe.py /app/

# 创建输出目录
RUN mkdir -p /app/output

# 设置入口点
ENTRYPOINT ["python3", "/app/bili_transcribe.py"]
CMD ["--help"]
