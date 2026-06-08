# Current Status

## 当前项目

项目名称：TransForum AI

当前开发版本号：TransForum AI Alpha 0.5.1

当前项目根目录：

```text
D:\transforum-ai
```

后续所有开发命令均应在该目录下执行。

## 当前阶段

First Real Meeting - Sprint 3B：本地 Whisper 中文逐字稿能力。

本阶段目标是让已上传的会议录音文件通过本地 `tiny` 模型生成中文逐字稿，保存为 TXT 文件，写入 SQLite，并显示在会议控制台。

## 当前已完成功能

- 创建会议并保存到 SQLite。
- 浏览器麦克风录音。
- 上传会议音频并保存到 `data/audio`。
- 本地 Whisper tiny 模型状态检查。
- `GET /api/transcription/model-status` 返回 Ready。
- `POST /api/transcription/start` 使用本地模型同步生成中文逐字稿。
- `GET /api/transcription/{meeting_id}` 读取逐字稿状态、文本和文件路径。
- 中文逐字稿保存到 `data/transcripts/meeting_{meeting_id}_transcript.txt`。
- `meetings` 表写入 `transcript_status`、`transcript_file`、`transcript_text`。
- 会议控制台显示 Whisper Status、Transcript Status、Generate Transcript 和 Transcript Preview。

## 当前模型状态

默认模型目录：

```text
D:\transforum-ai\models\whisper\tiny
```

模型加载要求：

- 使用 `faster-whisper`。
- `language="zh"`。
- `task="transcribe"`。
- `local_files_only=True`。
- 模型不存在时返回 `MODEL_NOT_FOUND`，不自动访问 Hugging Face。

## 当前禁止开发

- 英文翻译
- 实时字幕
- WebSocket
- GPT
- Gemini
- 会议纪要
- DOCX 导出
- AI 语音播报
- 多语言同步
- 手机扫码字幕
- 用户系统
- 支付系统
- 嘉宾专属词库

## 当前最新任务记录

时间标签：2026-06-08-TASK-005B-UAT

开发版本号：TransForum AI Alpha 0.5.1

完成状态：完成。

UAT 验收结果：

- 已通过 `scripts/download_whisper_tiny.py` 将模型安装到 `D:\transforum-ai\models\whisper\tiny`。
- `model-status` 返回 `installed=true`、`message=Ready`。
- 使用办公电脑本地生成的中文测试音频完成上传与转写验收。
- 测试会议 ID：`meeting_29357c757f4b`。
- 测试音频：`D:\transforum-ai\data\audio\meeting_29357c757f4b_20260608_084530.wav`。
- 逐字稿文件：`D:/transforum-ai/data/transcripts/meeting_29357c757f4b_transcript.txt`。
- SQLite 写入结果：`transcript_status=completed`，`transcript_file` 与 `transcript_text` 已写入。
- 识别耗时约 4.57 秒。
- 业务转写继续使用 `local_files_only=True`，不依赖运行时在线下载。

主要修改文件：

- backend/main.py
- backend/api/transcription.py
- backend/services/transcription_service.py
- backend/tests/test_transcription_service.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- PROJECT_RULES.md
- README.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md
- docs/DEVELOPMENT_PLAN.md
- docs/WHISPER_MODEL_SETUP.md

下一步任务：

- 2026-06-08-TASK-006：TransForum AI Alpha 0.6，中英翻译基础能力。
