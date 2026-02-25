---
name: bili_transcribe
description: 转录B站视频为文字。下载B站视频，提取音频，使用Whisper生成逐字稿。
argument-hint: <B站视频URL或BV号> [--model <模型>]
---

# B站视频转录

当用户使用 /bili_transcribe 命令时，执行以下操作：

## 执行步骤

### 步骤 1：运行转录脚本
使用 Bash 工具执行：
```bash
python3 ~/.claude/skills/bili_transcribe/bili_transcribe.py "$ARGUMENTS"
```

### 步骤 2：读取结果文件
脚本完成后，在 `~/bili-transcribe-output/` 目录查找生成的 `.txt` 文件。

**注意**：输出目录已从 `./output` 改为 `~/bili-transcribe-output`（用户主目录下）

### 步骤 3：提供内容总结
读取转录文本后，向用户总结：
- 视频的主要内容和核心观点
- 关键信息（如提到的专业、建议、数据等）
- 用 3-5 个 bullet points 概括要点

### 步骤 4：报告结果
告知用户生成的所有文件路径，并展示内容总结。

## 注意事项

- **使用 Bash 工具执行**，不要使用 Task 工具
- **输出目录**：`~/bili-transcribe-output/`（绝对路径，确保任意工作目录下都能找到）
- 不要尝试用其他方式获取视频信息（如 curl API）
- 不要尝试自己下载或转录，脚本已经包含了完整的处理逻辑
- 如果脚本报告缺少依赖（BBDown/ffmpeg/whisper），提示用户安装

## 参数示例

- `/bili-transcribe BV1V3q6BZEAU`
- `/bili-transcribe https://bilibili.com/video/BV1V3q6BZEAU --model small`

## 技术说明

- `--task-mode` 模式下，脚本会输出 JSON 状态到 stderr，最终结果到 stdout
- 默认输出目录：`~/bili-transcribe-output`
- 支持的模型：tiny, base, small, medium, large
