# Whisper Model Setup

## 模型目录

默认模型根目录：

```text
D:\transforum-ai\models\whisper
```

当前 tiny 模型目录：

```text
D:\transforum-ai\models\whisper\tiny
```

## 后端配置

配置文件：

```text
D:\transforum-ai\backend\.env
```

默认配置：

```text
TRANSFORUM_WHISPER_MODEL=tiny
TRANSFORUM_WHISPER_MODEL_PATH=D:/transforum-ai/models/whisper
TRANSFORUM_WHISPER_DEVICE=cpu
TRANSFORUM_WHISPER_COMPUTE_TYPE=int8
```

## 运行要求

会议转写必须使用本地模型：

```text
D:\transforum-ai\models\whisper\tiny
```

业务转写时必须保持：

- `local_files_only=True`
- `language="zh"`
- `task="transcribe"`

如果模型不存在，系统返回：

```json
{
  "success": false,
  "error": "MODEL_NOT_FOUND",
  "message": "Local Whisper model not found.",
  "status": "failed"
}
```

系统不得在业务转写时自动访问 Hugging Face，也不得在业务接口中自动下载模型。

## 状态检查

启动后端后访问：

```text
GET http://localhost:8000/api/transcription/model-status
```

Ready 示例：

```json
{
  "installed": true,
  "model": "tiny",
  "path": "D:/transforum-ai/models/whisper",
  "model_path": "D:/transforum-ai/models/whisper/tiny",
  "message": "Ready"
}
```

## 转写输出

成功调用：

```text
POST http://localhost:8000/api/transcription/start
```

请求体：

```json
{
  "meeting_id": "meeting_xxx"
}
```

成功返回：

```json
{
  "success": true,
  "status": "completed",
  "transcript": "大家好，欢迎参加 TransForum AI 测试会议。",
  "transcript_file": "D:/transforum-ai/data/transcripts/meeting_xxx_transcript.txt"
}
```

逐字稿保存目录：

```text
D:\transforum-ai\data\transcripts
```

文件命名规则：

```text
meeting_{meeting_id}_transcript.txt
```

## Alpha 0.5 验收重点

- 本地 tiny 模型可加载。
- webm 音频可被识别。
- 中文逐字稿可生成。
- TXT 文件可保存。
- SQLite 可写入 `transcript_status`、`transcript_file`、`transcript_text`。
- 前端会议控制台可显示 `Completed` 和逐字稿预览。
- 业务转写不依赖运行时在线下载。
