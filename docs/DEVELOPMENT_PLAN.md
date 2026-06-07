# TransForum AI Development Plan

当前版本：TransForum AI Alpha 0.4.2

当前项目根目录：

```text
D:\transforum-ai
```

后续所有命令均应在该目录下执行。

## Development Version Rule

TransForum AI 使用阶段性开发版本号。

- Alpha 0.1：项目骨架完成
- Alpha 0.1.1：项目迁移到 D:\transforum-ai 并建立任务标签与版本规则
- Alpha 0.2：会议创建与基础控制台可用
- Alpha 0.3：麦克风接入与语音识别可用
- Alpha 0.4：中英实时翻译可用
- Alpha 0.5：双语字幕投屏可用
- Alpha 0.6：会议存档可用
- Alpha 0.7：会议纪要生成可用
- Alpha 1.0：First Real Meeting 完整闭环可演示

每完成一个里程碑阶段，必须更新 README.md 和 docs/DEVELOPMENT_PLAN.md 中的当前版本号。

## Sprint 1：项目骨架与会议创建

目标：完成 Alpha 0.2 会议创建业务功能，并提供最小可用会议控制台入口。

开发内容：

- 创建 frontend、backend、docs、data、exports 目录。
- 创建首页、创建会议页、会议控制台页、投屏页。
- 创建 FastAPI 健康检查和会议创建占位接口。
- 初始化 SQLite 数据库。
- 创建 meetings 表。
- 实现创建会议、会议详情、最近会议列表 API。
- 实现前端创建会议表单提交。
- 创建成功后跳转会议控制台。
- 控制台读取并展示会议信息。

验收标准：

- 首页可以打开。
- 创建会议页可以打开。
- `GET /api/health` 返回 `Alpha 0.2`。
- `POST /api/meeting/create` 可以创建真实会议记录。
- `GET /api/meeting/list` 可以返回最近 50 条会议。
- `GET /api/meeting/{meeting_id}` 可以返回会议详情。
- SQLite 文件 `data/transforum.db` 已创建，且会议写入成功。

## Sprint 2：麦克风接入与语音识别

目标：接入浏览器麦克风并完成音频上传保存的最小可用链路。本阶段只验证音频链路，不做语音识别。

开发内容：

- 前端增加麦克风权限请求。
- 前端使用 MediaRecorder 录音和计时。
- 后端接收 multipart 音频上传。
- 保存音频到 `data/audio`。
- Meeting 表记录 `audio_file` 和 `audio_duration`。

验收标准：

- 用户可以在会议控制台启动麦克风。
- 用户可以停止录音并上传音频。
- 后端成功保存测试音频文件。
- Meeting 表记录音频文件和时长。
- 本阶段不接入 Whisper。

## Sprint 3：录音文件语音识别

目标：使用本地 Whisper 对会议录音文件进行中文语音识别，生成中文逐字稿。本阶段不做实时识别、翻译、字幕推送或会议纪要。

开发内容：

- 新增 `data/transcripts` 目录。
- Meeting 表新增 `transcript_file`、`transcript_text`、`transcript_status`。
- 新增 `backend/services/transcription_service.py`。
- 新增 `POST /api/transcription/start`。
- 新增 `GET /api/transcription/{meeting_id}`。
- 会议控制台新增 Speech Recognition、Transcript Status、Transcript Preview。
- 新增 Generate Transcript 按钮。

验收标准：

- Whisper 依赖安装成功。
- 可以读取会议录音文件。
- 可以生成 txt 中文逐字稿。
- 数据库保存识别文本、文件路径和状态。
- 前端可以显示识别状态和前 500 字预览。

## Sprint 3A：Whisper 本地模型管理

目标：让 Whisper 识别能力优先使用本地模型，会议现场不依赖 Hugging Face 在线下载或外部网络。

开发内容：

- 新增 `models/whisper` 目录。
- 新增 `backend/.env`。
- 新增 `backend/config.py`。
- 新增 `GET /api/transcription/model-status`。
- 修改转写服务为本地模型优先。
- 模型不存在时返回 `MODEL_NOT_FOUND`，不自动联网下载。
- 会议控制台显示 Whisper Status。
- 模型未安装时禁用 Generate Transcript。
- 新增 `docs/WHISPER_MODEL_SETUP.md`。

验收标准：

- 未安装模型时 `model-status` 返回 `installed=false`。
- 已安装模型时 `model-status` 返回 `installed=true`。
- 模型未安装时 Generate Transcript 禁用。
- 系统不会自动访问 Hugging Face 下载模型。

## Sprint 4：实时翻译

目标：将识别文本实时翻译为英文。

开发内容：

- 创建翻译服务适配层。
- 接入 GPT / Gemini 翻译能力。
- 处理基础错误和延迟状态。

验收标准：

- 中文原文可以实时生成英文译文。
- 翻译延迟满足会议可用性要求。
- 翻译失败时会议不中断。

## Sprint 5：双语字幕投屏

目标：提供适合投影仪、LED大屏和会议室显示器的字幕页面。

开发内容：

- 完善 `/screen` 全屏展示。
- 同步显示原文和译文。
- 优化字号、对比度和换行。

验收标准：

- 大屏远距离可读。
- 原文和译文同步刷新。
- 投屏页面不显示干扰会议的复杂控件。

## Sprint 6：会议内容存档

目标：自动保存会议过程中的原文和译文。

开发内容：

- 设计 SQLite 存储表。
- 保存时间戳、原文、译文。
- 增加会议状态流转。

验收标准：

- 会议结束后可以查询完整转写和翻译内容。
- 每条内容包含时间戳。
- 异常退出时尽量保留已产生内容。

## Sprint 7：AI会议纪要

目标：根据会议存档生成中英文会议纪要。

开发内容：

- 创建纪要生成服务。
- 生成摘要、核心观点和 Action Items。
- 输出中文会议纪要和英文会议纪要。

验收标准：

- 会议结束后自动生成纪要。
- 纪要内容来自会议存档。
- 中文和英文纪要都可查看。

## Sprint 8：DOCX导出

目标：导出完整会议成果。

开发内容：

- 创建 DOCX 导出服务。
- 导出中文逐字稿、英文逐字稿、中文会议纪要、英文会议纪要。
- 提供下载入口。

验收标准：

- 用户可以导出 DOCX。
- DOCX 包含完整会议成果。
- 文件命名包含会议名称和时间。
