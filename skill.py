#!/usr/bin/env python3
"""
Claude Code Skill - B站视频转录
"""

import subprocess
import sys
from pathlib import Path


def main(url: str, model: str = "small", summarize: bool = False):
    """Skill入口函数"""

    # 获取skill所在目录
    skill_dir = Path(__file__).parent
    script_path = skill_dir / "bili_transcribe.py"

    if not script_path.exists():
        print("❌ 错误: 找不到主程序 bili_transcribe.py")
        return 1

    # 构建命令
    cmd = [
        sys.executable,
        str(script_path),
        url,
        "--model", model,
        "--output-dir", "./output"
    ]

    # 如果是总结模式，添加 --summarize 参数
    if summarize:
        cmd.append("--summarize")

    if summarize:
        print(f"🎬 开始转录并总结: {url}")
    else:
        print(f"🎬 开始转录: {url}")
    print(f"🤖 使用模型: {model}")
    print()

    # 执行转录
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ 转录失败: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        return 130


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--model", default="small")
    parser.add_argument("--summarize", action="store_true", help="启用总结模式")
    args = parser.parse_args()
    sys.exit(main(args.url, args.model, args.summarize))
