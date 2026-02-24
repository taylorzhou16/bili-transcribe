#!/usr/bin/env python3
"""
B站视频转录工具 - 一键下载视频、提取音频、生成逐字稿

使用方法:
    python bili_transcribe.py <B站视频URL或BV号> [选项]

示例:
    python bili_transcribe.py https://b23.tv/LYMUM5G
    python bili_transcribe.py BV19NfJBoEDm --model medium
    python bili_transcribe.py BV19NfJBoEDm --keep-video --language zh
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
import urllib.request


class BiliTranscriber:
    """B站视频转录器"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path(tempfile.gettempdir()) / "bili_transcribe"
        self.temp_dir.mkdir(exist_ok=True)

    def extract_bvid(self, url: str) -> str:
        """从URL中提取BV号"""
        # 匹配BV号格式
        bv_pattern = r'BV[a-zA-Z0-9]{10}'
        match = re.search(bv_pattern, url)
        if match:
            return match.group()

        # 如果是短链接，尝试解析
        if 'b23.tv' in url or 'bili2233.cn' in url:
            try:
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                response = urllib.request.urlopen(req, timeout=10)
                final_url = response.geturl()
                match = re.search(bv_pattern, final_url)
                if match:
                    return match.group()
            except Exception as e:
                print(f"⚠️  解析短链接失败: {e}")

        raise ValueError(f"无法从URL中提取BV号: {url}")

    def check_dependency(self, cmd: str) -> bool:
        """检查依赖是否存在"""
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_dependencies(self) -> Dict[str, bool]:
        """检查所有依赖"""
        print("🔍 检查依赖...")

        deps = {
            "BBDown": self.check_dependency("BBDown"),
            "ffmpeg": self.check_dependency("ffmpeg"),
            "whisper": False
        }

        try:
            import whisper
            deps["whisper"] = True
        except ImportError:
            pass

        for name, installed in deps.items():
            status = "✅ 已安装" if installed else "❌ 未安装"
            print(f"  {name}: {status}")

        return deps

    def download_video(self, bvid: str, output_name: str) -> Path:
        """下载视频"""
        print(f"\n📥 正在下载视频 {bvid}...")
        output_path = self.temp_dir / f"{output_name}.mp4"

        # 使用BBDown下载
        cmd = [
            "BBDown",
            "--work-dir", str(self.temp_dir),
            "--file-pattern", output_name,
            bvid
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️  BBDown 输出: {result.stderr}")

            # 查找下载的文件
            for ext in ['.mp4', '.flv', '.mkv']:
                video_file = self.temp_dir / f"{output_name}{ext}"
                if video_file.exists():
                    print(f"✅ 视频已下载: {video_file}")
                    return video_file

            raise FileNotFoundError("视频文件未找到")

        except Exception as e:
            print(f"❌ 下载失败: {e}")
            raise

    def extract_audio(self, video_path: Path, output_name: str) -> Path:
        """提取音频"""
        print(f"\n🎵 正在提取音频...")
        audio_path = self.temp_dir / f"{output_name}.mp3"

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "2",
            "-y",
            str(audio_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ 音频提取失败: {result.stderr}")
            raise RuntimeError("音频提取失败")

        print(f"✅ 音频已提取: {audio_path}")
        return audio_path

    def transcribe_audio(self, audio_path: Path, model: str = "medium", language: str = "zh") -> dict:
        """使用Whisper转录音频"""
        print(f"\n📝 正在进行语音转录 (使用 {model} 模型)...")
        print("⏳ 这可能需要几分钟，请耐心等待...")

        import whisper

        # 加载模型
        model_obj = whisper.load_model(model)

        # 转录
        result = model_obj.transcribe(
            str(audio_path),
            language=language,
            verbose=False
        )

        print(f"✅ 转录完成! 共 {len(result['segments'])} 个片段")
        return result

    def save_transcript(self, result: dict, output_name: str, video_info: dict = None) -> Dict[str, Path]:
        """保存转录结果"""
        output_base = self.output_dir / output_name

        # 1. 保存纯文本
        txt_path = output_base.with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            if video_info:
                f.write(f"标题: {video_info.get('title', '未知')}\n")
                f.write(f"UP主: {video_info.get('up', '未知')}\n")
                f.write(f"BV号: {video_info.get('bvid', '未知')}\n")
                f.write("=" * 50 + "\n\n")
            f.write(result["text"])
        print(f"✅ 文本已保存: {txt_path}")

        # 2. 保存带时间戳的JSON
        json_path = output_base.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON已保存: {json_path}")

        # 3. 保存SRT字幕
        srt_path = output_base.with_suffix(".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(result["segments"], 1):
                start = self.format_time(seg["start"])
                end = self.format_time(seg["end"])
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{seg['text'].strip()}\n\n")
        print(f"✅ SRT字幕已保存: {srt_path}")

        # 4. 保存Markdown报告
        md_path = output_base.with_suffix(".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {video_info.get('title', '视频转录')}\n\n")
            if video_info:
                f.write(f"- **UP主**: {video_info.get('up', '未知')}\n")
                f.write(f"- **BV号**: {video_info.get('bvid', '未知')}\n")
                f.write(f"- **时长**: {self.format_duration(result.get('duration', 0))}\n\n")

            f.write("## 逐字稿\n\n")
            for seg in result["segments"]:
                time_str = self.format_time(seg["start"])
                f.write(f"**[{time_str}]** {seg['text'].strip()}\n\n")
        print(f"✅ Markdown报告已保存: {md_path}")

        return {
            "txt": txt_path,
            "json": json_path,
            "srt": srt_path,
            "md": md_path
        }

    def format_time(self, seconds: float) -> str:
        """格式化时间为 SRT 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def format_duration(self, seconds: float) -> str:
        """格式化时长"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}:{minutes:02d}"

    def cleanup(self, keep_video: bool = False, output_name: str = None):
        """清理临时文件"""
        print("\n🧹 清理临时文件...")

        # 清理音频文件
        for f in self.temp_dir.glob("*.mp3"):
            f.unlink()

        # 除非指定保留，否则清理视频文件
        if not keep_video and output_name:
            for ext in ['.mp4', '.flv', '.mkv']:
                video_file = self.temp_dir / f"{output_name}{ext}"
                if video_file.exists():
                    video_file.unlink()

        print("✅ 清理完成")

    def process(self, url: str, model: str = "medium", language: str = "zh",
                keep_video: bool = False, skip_download: bool = False):
        """主处理流程"""

        # 1. 提取BV号
        bvid = self.extract_bvid(url)
        print(f"✅ 识别到 BV号: {bvid}")

        # 2. 生成输出文件名
        output_name = f"{bvid}"

        # 3. 检查依赖
        deps = self.check_dependencies()
        if not all(deps.values()):
            print("\n❌ 缺少依赖，请安装后重试")
            print("安装命令:")
            print("  - BBDown: 见 https://github.com/nilaoda/BBDown")
            print("  - ffmpeg: brew install ffmpeg 或 apt install ffmpeg")
            print("  - whisper: pip install openai-whisper")
            sys.exit(1)

        try:
            # 4. 下载视频
            if not skip_download:
                video_path = self.download_video(bvid, output_name)
            else:
                video_path = self.temp_dir / f"{output_name}.mp4"
                if not video_path.exists():
                    raise FileNotFoundError(f"视频文件不存在: {video_path}")

            # 5. 提取音频
            audio_path = self.extract_audio(video_path, output_name)

            # 6. 语音转录
            result = self.transcribe_audio(audio_path, model, language)

            # 7. 保存结果
            video_info = {"bvid": bvid, "title": "未知", "up": "未知"}
            output_files = self.save_transcript(result, output_name, video_info)

            # 8. 清理
            self.cleanup(keep_video, output_name)

            print(f"\n🎉 全部完成!")
            print(f"📁 输出目录: {self.output_dir}")
            print(f"\n生成的文件:")
            for file_type, file_path in output_files.items():
                print(f"  - {file_type.upper()}: {file_path.name}")

            return output_files

        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="B站视频转录工具 - 一键生成逐字稿",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 基本用法
    python bili_transcribe.py https://b23.tv/LYMUM5G

    # 使用更快的模型
    python bili_transcribe.py BV19NfJBoEDm --model small

    # 保留视频文件
    python bili_transcribe.py BV19NfJBoEDm --keep-video

    # 英文视频
    python bili_transcribe.py BVxxxx --language en

模型选项 (从小到大, 速度越快准确率越低):
    tiny, base, small, medium, large
        """
    )

    parser.add_argument("url", help="B站视频URL或BV号")
    parser.add_argument("--model", default="medium",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper模型大小 (默认: medium)")
    parser.add_argument("--language", default="zh",
                        help="视频语言 (默认: zh, 中文)")
    parser.add_argument("--output-dir", default="./output",
                        help="输出目录 (默认: ./output)")
    parser.add_argument("--keep-video", action="store_true",
                        help="保留下载的视频文件")
    parser.add_argument("--skip-download", action="store_true",
                        help="跳过下载步骤(使用已有视频)")

    args = parser.parse_args()

    # 创建转录器实例
    transcriber = BiliTranscriber(output_dir=args.output_dir)

    # 开始处理
    transcriber.process(
        url=args.url,
        model=args.model,
        language=args.language,
        keep_video=args.keep_video,
        skip_download=args.skip_download
    )


if __name__ == "__main__":
    main()
