# TransForum AI Development Plan

当前版本：TransForum AI Alpha 0.5

当前项目根目录：

```text
D:\transforum-ai
```

后续所有命令均应在该目录下执行。

## Development Version Rule

TransForum AI 使用阶段性开发版本号。

- Alpha 0.1：项目骨架完成
- Alpha 0.1.1：项目迁移到 `D:\transforum-ai` 并建立任务标签与版本规则
- Alpha 0.2：会议创建与基础控制台可用
- Alpha 0.3：会议音频采集、上传和保存链路可用
- Alpha 0.4：录音文件 Whisper 识别入口可用
- Alpha 0.4.1：Whisper 本地模型优先管理可用
- Alpha 0.4.2：Whisper tiny 本地模型 Ready 验证完成
- Alpha 0.5：本地 Whisper 中文逐字稿可用
- Alpha 0.6：中英翻译基础能力可用
- Alpha 0.7：会议存档可用
- Alpha 0.8：会议纪要生成可用
- Alpha 1.0：First Real Meeting 完整闭环可演示

## Sprint 3B：本地 Whisper 中文逐字稿

目标：使用本地 Whisper tiny 模型对已上传会议录音进行中文转写，生成中文逐字稿，并写入文件和 SQLite。

开发内容：

- 使用 `D:\transforum-ai\models\whisper\tiny` 本地模型。
- 禁止运行时自动访问 Hugging Face 下载模型。
- `POST /api/transcription/start` 返回转写最终结果。
- `GET /api/transcription/{meeting_id}` 返回当前转写状态、文本和文件路径。
- 逐字稿保存到 `data/transcripts/meeting_{meeting_id}_transcript.txt`。
- SQLite `meetings` 表写入 `transcript_status`、`transcript_file`、`transcript_text`。
- 会议控制台显示 Whisper Status、Transcript Status、Generate Transcript、Transcript Preview。

验收标准：

- `GET /api/transcription/model-status` 返回 `installed=true` 和 `message=Ready`。
- webm 音频可被本地模型识别。
- 中文逐字稿生成成功。
- TXT 文件保存成功。
- SQLite 更新成功。
- 前端显示 `Completed`。
- 前端显示前 500 字逐字稿预览。
- 系统不依赖运行时在线下载。

## Sprint 4：中英翻译基础能力

目标：在 Alpha 0.6 中基于已生成的中文逐字稿，提供最小可用的中英翻译能力。

开发边界：

- 只做基础翻译链路。
- 不做实时字幕。
- 不做 WebSocket。
- 不做会议纪要。
- 不做 DOCX 导出。

下一任务：

```text
2026-06-08-TASK-006
TransForum AI Alpha 0.6
目标：中英翻译基础能力
```
