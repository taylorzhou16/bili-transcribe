---
name: bili_transcribe
description: 转录B站视频为文字。下载B站视频，提取音频，使用Whisper生成逐字稿。
argument-hint: <B站视频URL或BV号> [--model <模型>]
---

# B站视频转录

**重要：直接执行 Python 脚本，不要递归调用 Skill**

当用户使用 /bili_transcribe 命令时，执行以下操作：

## 执行步骤

### 步骤 1：启动转录任务

使用 Task 工具执行 Python 脚本（**不是调用 skill，是直接执行脚本**）：

```json
{
  "command": "python3 ~/.claude/skills/bili_transcribe/bili_transcribe.py \"$ARGUMENTS\" --task-mode",
  "description": "转录B站视频"
}
```

### 步骤 2：等待任务完成

使用 TaskOutput 工具获取任务结果：
```json
{
  "task_id": "<上一步返回的task_id>"
}
```

### 步骤 3：读取结果文件

脚本完成后，在 `~/bili-transcribe-output/` 目录查找生成的 `.txt` 文件。

### 步骤 4：提供内容总结

读取转录文本后，向用户总结：
- 视频的主要内容和核心观点
- 关键信息（如提到的专业、建议、数据等）
- 用 3-5 个 bullet points 概括要点

### 步骤 5：报告结果

告知用户生成的所有文件路径，并展示内容总结。

## 关键提醒

- **不要**在 Task 里再次调用 `Skill(bili_transcribe)`，这会形成无限循环
- 直接在 Task 里执行 `python3 bili_transcribe.py` 命令
- 使用 `--task-mode` 参数获取 JSON 进度输出
- **输出目录**：`~/bili-transcribe-output/`

## 参数示例

- `/bili_transcribe BV1V3q6BZEAU`
- `/bili_transcribe https://bilibili.com/video/BV1V3q6BZEAU --model small`

## 技术说明

- `--task-mode` 参数启用 JSON 状态输出到 stderr
- 最终结果以 JSON 格式输出到 stdout
- 支持的模型：tiny, base, small, medium, large
