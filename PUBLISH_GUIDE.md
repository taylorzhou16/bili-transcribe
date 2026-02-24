# 🚀 发布到 GitHub 指南

## 1. 创建 GitHub 仓库

1. 登录 GitHub: https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `bili-transcribe` (或其他你喜欢的名字)
   - Description: `B站视频转录工具 - 一键下载视频并生成逐字稿`
   - 选择 "Public" (公开) 或 "Private" (私有)
   - 不要勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

## 2. 上传代码

```bash
# 进入项目目录
cd ~/github/bili-transcribe

# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: B站视频转录工具"

# 添加远程仓库 (替换 your-username 为taylorzhou16)
git remote add origin https://github.com/your-username/bili-transcribe.git

# 推送代码
git push -u origin main
```

## 3. 配置 GitHub Actions (自动构建Docker镜像)

1. 在GitHub仓库页面，点击 "Settings" → "Secrets and variables" → "Actions"
2. 确保 `GITHUB_TOKEN` 有权限推送镜像到 GitHub Packages
3. 或者去 "Settings" → "Packages" 启用

## 4. 发布第一个版本

```bash
# 创建标签
git tag -a v1.0.0 -m "第一个正式版本"

# 推送标签
git push origin v1.0.0
```

这会自动触发 GitHub Actions 构建 Docker 镜像并推送到 GitHub Container Registry。

## 5. 分享给朋友

### 方式1: Docker (推荐)

```bash
# 直接运行 (无需安装任何依赖)
docker run -v $(pwd)/output:/app/output \
  ghcr.io/your-username/bili-transcribe:v1.0.0 \
  "https://b23.tv/xxxxx"
```

### 方式2: 本地安装

```bash
git clone https://github.com/your-username/bili-transcribe.git
cd bili-transcribe
./install.sh
python3 bili_transcribe.py "BVxxxxx"
```

### 方式3: Claude Code Skill

```bash
claude config set skills.bili-transcribe \
  "https://raw.githubusercontent.com/your-username/bili-transcribe/main/skill.json"
```

## 6. 更新 README

记得修改 README.md 中的以下内容：
- 所有的 `taylorzhou16` 替换为taylorzhou16
- 根据需要调整描述信息

## 7. 后续更新

```bash
# 修改代码后
git add .
git commit -m "更新描述"
git push

# 发布新版本
git tag -a v1.1.0 -m "版本描述"
git push origin v1.1.0
```

## 注意事项

1. **BBDown登录**: 有些B站视频需要登录才能下载高清版本，建议在使用前运行 `BBDown login` 扫码登录
2. **模型下载**: 第一次使用会自动下载Whisper模型（small约500MB，medium约1.5GB）
3. **Docker权限**: Linux/macOS可能需要 `sudo` 运行docker命令

## 需要帮助？

遇到问题可以在GitHub仓库提交 Issue。
