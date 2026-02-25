#!/usr/bin/env python3
"""
B站视频转录工具 - 一键下载视频、提取音频、生成逐字稿
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict
import urllib.request


class BiliTranscriber:
    """B站视频转录器"""

    COMMON_PATHS = [
        "/usr/local/bin",
        "/opt/homebrew/bin",
        "/usr/bin",
        "/bin",
        str(Path.home() / "bin"),
        str(Path.home() / ".local" / "bin"),
        "/opt/bin",
        "/usr/local/opt/bbdown/bin",  # Homebrew 可能的安装路径
        str(Path.home() / ".dotnet" / "tools"),  # dotnet tools
    ]

    def __init__(self, output_dir: str = "~/bili-transcribe-output", task_mode: bool = False):
        # 展开 ~ 为实际家目录路径
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path.home() / ".cache" / "bili_transcribe"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._cmd_cache: Dict[str, Optional[str]] = {}
        self.task_mode = task_mode

    def report_status(self, stage: str, status: str, message: str = "", data: dict = None):
        """在Task模式下报告状态到stderr"""
        if self.task_mode:
            status_obj = {
                "stage": stage,
                "status": status,
                "message": message
            }
            if data:
                status_obj["data"] = data
            print(json.dumps(status_obj, ensure_ascii=False), file=sys.stderr, flush=True)

    def find_executable(self, cmd: str) -> Optional[str]:
        """查找可执行文件 - 使用多种方法确保找到已安装的命令"""
        if cmd in self._cmd_cache:
            return self._cmd_cache[cmd]

        # 方法1: 使用 shutil.which（最标准的方式）
        result = shutil.which(cmd)
        if result:
            self._cmd_cache[cmd] = result
            return result

        # 方法2: 对于 BBDown，尝试各种大小写变体
        if cmd.lower() == "bbdown":
            for variant in ["BBDown", "bbdown", "Bbdown", "bbDown"]:
                result = shutil.which(variant)
                if result:
                    self._cmd_cache[cmd] = result
                    return result

        # 方法3: 使用 shell 的 command -v（能处理更多情况）
        try:
            shell_cmd = f"command -v {cmd}"
            result = subprocess.run(
                shell_cmd, shell=True, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    self._cmd_cache[cmd] = path
                    return path
        except Exception:
            pass

        # 方法4: 使用 which -a 查找所有可能的匹配
        try:
            result = subprocess.run(
                ["which", "-a", cmd],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    path = line.strip()
                    if path and os.path.isfile(path) and os.access(path, os.X_OK):
                        self._cmd_cache[cmd] = path
                        return path
        except Exception:
            pass

        # 方法5: 在常见路径中搜索
        for path in self.COMMON_PATHS:
            full_path = Path(path) / cmd
            if full_path.exists() and os.access(full_path, os.X_OK):
                self._cmd_cache[cmd] = str(full_path)
                return str(full_path)

            # 对于 BBDown，尝试各种大小写
            if cmd.lower() == "bbdown":
                for variant in ["BBDown", "bbdown", "Bbdown"]:
                    full_path_alt = Path(path) / variant
                    if full_path_alt.exists() and os.access(full_path_alt, os.X_OK):
                        self._cmd_cache[cmd] = str(full_path_alt)
                        return str(full_path_alt)

        # 方法6: 尝试使用 type 命令（bash 内建）
        try:
            result = subprocess.run(
                ["bash", "-c", f"type -P {cmd}"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                if os.path.isfile(path):
                    self._cmd_cache[cmd] = path
                    return path
        except Exception:
            pass

        # 方法7: 使用 whereis
        try:
            result = subprocess.run(
                ["whereis", cmd],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                paths = result.stdout.strip().split(":")[-1].strip().split()
                for p in paths:
                    if os.path.isfile(p) and os.access(p, os.X_OK):
                        self._cmd_cache[cmd] = p
                        return p
        except Exception:
            pass

        self._cmd_cache[cmd] = None
        return None

    def check_dependency(self, cmd: str) -> bool:
        """检查依赖是否存在 - 改进版，提供更多诊断信息"""
        path = self.find_executable(cmd)
        if path:
            print(f"  {cmd}: ✅ 已安装 ({path})")
            return True

        print(f"  {cmd}: ❌ 未安装")
        return False

    def get_cmd(self, cmd: str) -> str:
        """获取命令的绝对路径"""
        path = self.find_executable(cmd)
        return path if path else cmd

    def extract_bvid(self, url: str) -> str:
        """从URL中提取BV号"""
        url = url.strip()

        bv_pattern = r'BV[a-zA-Z0-9]{10}'
        match = re.search(bv_pattern, url)
        if match:
            return match.group()

        if 'b23.tv' in url or 'bili2233.cn' in url:
            try:
                print("🔗 正在解析短链接...")
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
                req.add_header('Accept', 'text/html,application/xhtml+xml')
                response = urllib.request.urlopen(req, timeout=15)
                final_url = response.geturl()
                match = re.search(bv_pattern, final_url)
                if match:
                    return match.group()
            except Exception as e:
                print(f"⚠️  解析短链接失败: {e}")
                try:
                    req = urllib.request.Request(url, method='GET')
                    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
                    response = urllib.request.urlopen(req, timeout=15)
                    final_url = response.geturl()
                    match = re.search(bv_pattern, final_url)
                    if match:
                        return match.group()
                except Exception as e2:
                    print(f"⚠️  GET 请求也失败: {e2}")

        raise ValueError(f"无法从URL中提取BV号: {url}\n请提供完整的B站视频链接或正确的BV号")

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
            print(f"  whisper: ✅ 已安装 (Python包)")
        except ImportError:
            print(f"  whisper: ❌ 未安装")

        return deps

    def download_video(self, bvid: str, output_name: str) -> Path:
        """下载视频"""
        print(f"\n📥 正在下载视频 {bvid}...")
        print("   这可能需要一些时间，请耐心等待...")

        bbdown_cmd = self.get_cmd("BBDown")

        cmd = [
            bbdown_cmd,
            "--work-dir", str(self.temp_dir),
            "--file-pattern", output_name,
            "--select-page", "1",
            bvid
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if error_msg:
                    print(f"⚠️  BBDown 输出: {error_msg[:500]}")

            possible_files = []
            for ext in ['.mp4', '.flv', '.mkv', '.m4v']:
                video_file = self.temp_dir / f"{output_name}{ext}"
                if video_file.exists():
                    possible_files.append(video_file)

                for f in self.temp_dir.glob(f"{output_name}*{ext}"):
                    if f.exists():
                        possible_files.append(f)

            if possible_files:
                video_file = max(possible_files, key=lambda p: p.stat().st_size)
                print(f"✅ 视频已下载: {video_file.name}")
                return video_file

            print(f"\n⚠️  未找到下载的视频文件")
            print(f"   临时目录内容: {list(self.temp_dir.glob('*'))}")
            raise FileNotFoundError(f"视频文件未找到，BV号: {bvid}")

        except FileNotFoundError:
            raise
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            raise RuntimeError(f"视频下载失败: {e}")

    def extract_audio(self, video_path: Path, output_name: str) -> Path:
        """提取音频"""
        print(f"\n🎵 正在提取音频...")

        audio_path = self.temp_dir / f"{output_name}.mp3"

        cmd = [
            self.get_cmd("ffmpeg"),
            "-i", str(video_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "2",
            "-y",
            str(audio_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        if result.returncode != 0:
            error_msg = result.stderr or "未知错误"
            print(f"❌ 音频提取失败: {error_msg[:500]}")
            raise RuntimeError(f"音频提取失败: {error_msg[:200]}")

        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件未生成: {audio_path}")

        print(f"✅ 音频已提取: {audio_path.name}")
        return audio_path

    def transcribe_audio(self, audio_path: Path, model: str = "medium", language: str = "zh") -> dict:
        """使用Whisper转录音频"""
        print(f"\n📝 正在进行语音转录...")
        print(f"   模型: {model} | 语言: {language}")
        print("   ⏳ 这可能需要几分钟，请耐心等待...")

        try:
            import whisper
        except ImportError:
            raise ImportError("未安装 openai-whisper，请运行: pip install openai-whisper")

        valid_models = ["tiny", "base", "small", "medium", "large", "large-v1", "large-v2", "large-v3"]
        if model not in valid_models:
            print(f"⚠️  未知模型 '{model}'，使用默认的 'small'")
            model = "small"

        try:
            model_obj = whisper.load_model(model)
        except Exception as e:
            raise RuntimeError(f"加载 Whisper 模型失败: {e}")

        try:
            result = model_obj.transcribe(
                str(audio_path),
                language=language if language else None,
                verbose=False,
                fp16=False
            )
        except Exception as e:
            raise RuntimeError(f"语音转录失败: {e}")

        segments_count = len(result.get('segments', []))
        print(f"✅ 转录完成! 共 {segments_count} 个片段")
        return result

    def save_transcript(self, result: dict, output_name: str, video_info: dict = None) -> Dict[str, Path]:
        """保存转录结果"""
        output_base = self.output_dir / output_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        files_created = {}

        try:
            txt_path = output_base.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                if video_info:
                    f.write(f"标题: {video_info.get('title', '未知')}\n")
                    f.write(f"UP主: {video_info.get('up', '未知')}\n")
                    f.write(f"BV号: {video_info.get('bvid', '未知')}\n")
                    f.write("=" * 50 + "\n\n")
                f.write(result.get("text", ""))
            files_created["txt"] = txt_path
            print(f"✅ 文本: {txt_path.name}")
        except Exception as e:
            print(f"⚠️  保存文本失败: {e}")

        try:
            json_path = output_base.with_suffix(".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            files_created["json"] = json_path
            print(f"✅ JSON: {json_path.name}")
        except Exception as e:
            print(f"⚠️  保存JSON失败: {e}")

        try:
            srt_path = output_base.with_suffix(".srt")
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, seg in enumerate(result.get("segments", []), 1):
                    start = self.format_time(seg.get("start", 0))
                    end = self.format_time(seg.get("end", 0))
                    text = seg.get("text", "").strip()
                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{text}\n\n")
            files_created["srt"] = srt_path
            print(f"✅ SRT: {srt_path.name}")
        except Exception as e:
            print(f"⚠️  保存SRT失败: {e}")

        try:
            md_path = output_base.with_suffix(".md")
            with open(md_path, "w", encoding="utf-8") as f:
                title = video_info.get('title', '视频转录') if video_info else '视频转录'
                f.write(f"# {title}\n\n")
                if video_info:
                    f.write(f"- **UP主**: {video_info.get('up', '未知')}\n")
                    f.write(f"- **BV号**: {video_info.get('bvid', '未知')}\n")
                    duration = result.get('duration', 0)
                    f.write(f"- **时长**: {self.format_duration(duration)}\n\n")

                f.write("## 逐字稿\n\n")
                for seg in result.get("segments", []):
                    time_str = self.format_time(seg.get("start", 0))
                    text = seg.get("text", "").strip()
                    f.write(f"**[{time_str}]** {text}\n\n")
            files_created["md"] = md_path
            print(f"✅ Markdown: {md_path.name}")
        except Exception as e:
            print(f"⚠️  保存Markdown失败: {e}")

        return files_created

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
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def cleanup(self, keep_video: bool = False, output_name: str = None):
        """清理临时文件"""
        print("\n🧹 清理临时文件...")

        cleaned = []

        if output_name:
            audio_file = self.temp_dir / f"{output_name}.mp3"
            if audio_file.exists():
                audio_file.unlink()
                cleaned.append(audio_file.name)

        if not keep_video and output_name:
            for ext in ['.mp4', '.flv', '.mkv', '.m4v']:
                for video_file in self.temp_dir.glob(f"{output_name}*{ext}"):
                    if video_file.exists():
                        video_file.unlink()
                        cleaned.append(video_file.name)

        if cleaned:
            print(f"   已清理: {', '.join(cleaned[:3])}")
        print("✅ 清理完成")

    def process(self, url: str, model: str = "medium", language: str = "zh",
                keep_video: bool = False, skip_download: bool = False) -> Optional[Dict[str, Path]]:
        """主处理流程"""

        self.report_status("init", "running", f"开始处理: {url}")

        bvid = self.extract_bvid(url)
        print(f"✅ 识别到 BV号: {bvid}")
        self.report_status("extract_bvid", "completed", f"识别到BV号: {bvid}", {"bvid": bvid})

        output_name = f"{bvid}"

        deps = self.check_dependencies()
        missing = [name for name, installed in deps.items() if not installed]
        if missing:
            print(f"\n❌ 缺少依赖: {', '.join(missing)}")
            print("\n安装指南:")
            print("  • BBDown: https://github.com/nilaoda/BBDown/releases")
            print("  • ffmpeg: brew install ffmpeg")
            print("  • whisper: pip install openai-whisper")
            self.report_status("dependencies", "failed", f"缺少依赖: {', '.join(missing)}")
            raise RuntimeError(f"缺少必要依赖: {', '.join(missing)}")

        self.report_status("dependencies", "completed", "所有依赖已安装")

        video_path = None
        try:
            if not skip_download:
                self.report_status("download", "running", "开始下载视频")
                video_path = self.download_video(bvid, output_name)
                self.report_status("download", "completed", f"视频下载完成: {video_path.name}")
            else:
                found = False
                for ext in ['.mp4', '.flv', '.mkv', '.m4v']:
                    for f in self.temp_dir.glob(f"{output_name}*{ext}"):
                        video_path = f
                        found = True
                        break
                    if found:
                        break

                if not video_path or not video_path.exists():
                    raise FileNotFoundError(f"未找到现有视频文件: {self.temp_dir}/{output_name}.*")
                print(f"✅ 使用现有视频: {video_path.name}")
                self.report_status("download", "skipped", f"使用现有视频: {video_path.name}")

            self.report_status("extract_audio", "running", "正在提取音频")
            audio_path = self.extract_audio(video_path, output_name)
            self.report_status("extract_audio", "completed", f"音频提取完成: {audio_path.name}")

            self.report_status("transcribe", "running", "正在进行语音转录")
            result = self.transcribe_audio(audio_path, model, language)
            self.report_status("transcribe", "completed", f"转录完成，共 {len(result.get('segments', []))} 个片段")

            video_info = {"bvid": bvid, "title": "B站视频", "up": "未知"}
            output_files = self.save_transcript(result, output_name, video_info)

            # 转换为字符串路径用于JSON序列化
            files_dict = {k: str(v) for k, v in output_files.items()}
            self.report_status("save", "completed", "转录结果已保存", {"files": files_dict})

            self.cleanup(keep_video, output_name)
            self.report_status("cleanup", "completed", "临时文件已清理")

            return output_files

        except Exception as e:
            self.report_status("error", "failed", str(e))
            try:
                self.cleanup(keep_video, output_name)
            except:
                pass
            raise


def parse_arguments(args_list):
    """解析参数，支持多种格式"""
    parser = argparse.ArgumentParser(
        description="B站视频转录工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("url", help="B站视频URL或BV号")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--language", default="zh", help="视频语言 (默认: zh)")
    parser.add_argument("--output-dir", default="~/bili-transcribe-output", help="输出目录")
    parser.add_argument("--keep-video", action="store_true", help="保留视频文件")
    parser.add_argument("--skip-download", action="store_true", help="跳过下载")
    parser.add_argument("--task-mode", action="store_true", help="Task模式：输出JSON状态到stderr，最终结果到stdout")

    return parser.parse_args(args_list)


def main():
    """主入口"""
    args = parse_arguments(sys.argv[1:])

    print(f"🎬 B站视频转录")
    print(f"{'─' * 40}")
    print(f"📹 视频: {args.url}")
    print(f"🤖 模型: {args.model}")
    print(f"🌐 语言: {args.language}")
    print(f"📁 输出: {args.output_dir}")
    print(f"{'─' * 40}\n")

    try:
        transcriber = BiliTranscriber(output_dir=args.output_dir, task_mode=args.task_mode)
        result = transcriber.process(
            url=args.url,
            model=args.model,
            language=args.language,
            keep_video=args.keep_video,
            skip_download=args.skip_download
        )

        if result:
            print(f"\n{'─' * 40}")
            print("✅ 转录完成！")
            print(f"📁 输出目录: {args.output_dir}")
            print("\n生成的文件:")
            for file_type, file_path in result.items():
                print(f"  • {file_type.upper()}: {file_path.name}")

            # Task模式下输出JSON结果到stdout
            if args.task_mode:
                output_result = {
                    "success": True,
                    "output_dir": str(transcriber.output_dir),
                    "files": {k: str(v) for k, v in result.items()}
                }
                print(json.dumps(output_result, ensure_ascii=False))

            return 0
        else:
            if args.task_mode:
                print(json.dumps({"success": False, "error": "转录未完成"}, ensure_ascii=False))
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        if args.task_mode:
            print(json.dumps({"success": False, "error": "用户中断"}, ensure_ascii=False))
        return 130
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        if args.task_mode:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            print(json.dumps(error_result, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
