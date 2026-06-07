# TransForum AI Architecture

当前项目根目录：

```text
D:\transforum-ai
```

后续所有命令均应在该目录下执行。

## 项目目标

TransForum AI Alpha 0.4.2 只服务 First Real Meeting：让一个用户使用一台电脑、一个麦克风和一台投影仪，在 5 分钟内开启一场中英双语 AI 同传会议，并在会议结束后生成完整会议成果。

## 系统模块

- 会议创建
- 实时语音识别
- 实时翻译
- 双语字幕展示
- 投屏模式
- 会议存档
- AI会议纪要
- DOCX导出

## 前端页面结构

- `/`：首页，展示项目名称、版本和入口按钮。
- `/meeting/new`：创建会议页，填写会议名称、源语言和目标语言。
- `/meeting/live`：会议控制台页，预留会议状态、麦克风状态、原文和译文区域。
- `/screen`：投屏页面，用于投影仪、LED大屏和会议室显示器。

## 后端 API 结构

- `GET /api/health`：健康检查。
- `POST /api/meeting/create`：创建会议。
- `GET /api/meeting/list`：获取最近会议列表。
- `GET /api/meeting/{meeting_id}`：获取会议详情。
- `POST /api/audio/upload`：上传会议测试音频。
- `POST /api/transcription/start`：启动录音文件语音识别。
- `GET /api/transcription/{meeting_id}`：获取逐字稿状态和结果。
- `GET /api/transcription/model-status`：检查本地 Whisper 模型是否已安装。
- `POST /api/meeting/start`：开始会议。
- `POST /api/meeting/end`：结束会议。
- `POST /api/meeting/export`：导出会议成果占位接口。

## 数据库结构

SQLite 数据库文件：

```text
D:\transforum-ai\data\transforum.db
```

当前表：

- `meetings`：保存会议名称、源语言、目标语言、状态、创建时间、开始时间、结束时间、音频文件路径、音频时长、逐字稿文件路径、逐字稿文本和逐字稿状态。

## 未来数据流

Microphone → Speech Recognition → Translation → Subtitle Display → Meeting Archive → Summary → Export

## Whisper 本地模型策略

默认模型目录：

```text
D:\transforum-ai\models\whisper
```

系统优先检查本地模型目录。如果模型不存在，返回 `MODEL_NOT_FOUND`，不自动访问 Hugging Face，不自动下载模型。

## Alpha 0.4.1 边界

本阶段只实现 Whisper 本地模型管理，不开发翻译、实时字幕、WebSocket、会议纪要、DOCX 导出、登录、支付、扫码字幕、手机 APP、AI 语音播报、多语言系统或复杂后台。
