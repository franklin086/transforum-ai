# TransForum AI

当前版本：TransForum AI Alpha 1.2.2-hotfix

当前项目根目录：

```text
D:\transforum-ai
```

后续所有命令均应在该目录下执行。

## 项目目标

TransForum AI 的目标不是做一个功能丰富的翻译软件，而是让任何人都能在 5 分钟内开启一场专业的双语国际会议，并在会议结束时获得完整的会议成果。

## Rule 0（最高开发原则）

当前只开发 First Real Meeting，不开发与真实会议闭环无关的扩展功能。

任何功能开发前，必须先回答：

“这个功能是否能够帮助用户更快、更稳定地完成一场真实会议？”

如果答案是否定的，则该功能不进入当前开发周期。

## Rule 1：每个 TASK 必须自动更新项目状态文档

每完成一个 Codex TASK，必须自动更新以下三个文件：

- `docs/CURRENT_STATUS.md`
- `docs/TASK_HISTORY.md`
- `docs/CHANGELOG.md`

每次更新必须记录：

- 时间标签
- 开发版本号
- 修改文件
- 完成状态
- 验收结果
- 下一步任务

这条规则用于确保即使半年后继续开发，也可以通过项目文档迅速恢复上下文，而不需要反复依赖截图、聊天记录或复制大量内容。

## Rule 2：Technical Debt Tracking

从 Alpha 0.8 开始，每个 TASK 完成时必须检查并记录技术债务。

每次 TASK 完成时必须检查：

1. 遗留问题
2. 临时方案
3. 未自动化验收部分
4. 环境依赖问题
5. 性能风险

检查结果必须同步更新：

- `docs/TECHNICAL_DEBT.md`

禁止仅记录在聊天记录中。

最终报告必须增加：

```text
开发债务检查结果

新增债务：
...

已解决债务：
...

当前债务总数：
...
```

## Rule 3：默认使用中文进行项目沟通与文档记录

所有开发过程汇报、设计方案、验收报告默认使用中文。

代码中的变量名、API 路径、数据库字段保持英文。

文档、说明、开发日志、验收结果统一使用中文。

## First Real Meeting 核心流程

创建会议 → 接入麦克风 → 实时语音识别 → 实时中英翻译 → 双语字幕投屏 → 保存会议内容 → 生成中英文逐字稿和会议纪要 → 导出会议成果

## Alpha 1.2 演示前快速检查

进入项目根目录：

```powershell
cd D:\transforum-ai
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
```

该脚本会检查项目目录、前后端目录、本地 Whisper tiny 模型、`data\audio`、`data\chunks`、`data\transcripts`、Python、Node 和 npm。

## Alpha 1.2 一键启动脚本

后端：

```powershell
cd D:\transforum-ai
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

前端：

```powershell
cd D:\transforum-ai
powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
```

如果前端开发服务不稳定，可使用：

```powershell
cd D:\transforum-ai\frontend
npm run build
npm run start -- -p 3001
```

演示前清单见：

```text
scripts\demo_checklist.md
```

## 本地启动方式

进入项目根目录：

```bash
cd /d D:\transforum-ai
```

### 前端启动命令

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：

```text
http://localhost:3000
```

### 后端启动命令

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

后端默认地址：

```text
http://localhost:8000
```

健康检查：

```text
http://localhost:8000/api/health
```

## 当前页面

- `/`
- `/meeting/new`
- `/meeting/live`
- `/meeting/minutes`
- `/screen`

## 当前可用功能

- 创建会议
- 保存会议
- 读取会议
- 查看最近会议
- 浏览器麦克风录音
- 上传测试音频
- 保存测试音频文件
- Whisper 录音文件识别
- 生成中文逐字稿
- 保存中文逐字稿 TXT 文件
- 将 `transcript_status`、`transcript_file`、`transcript_text` 写入 SQLite
- 会议控制台显示转写状态和前 500 字预览
- Whisper 本地模型检查
- 前端每 3 秒生成实时音频分片
- `POST /api/realtime/transcribe-chunk` 使用本地 Whisper tiny 识别中文分片
- 会议控制台实时显示中文滚动字幕
- 实时逐字稿保存到 TXT 和 SQLite `realtime_transcript_text`
- `/screen?meeting_id=xxx` 中文字幕投屏大屏模式
- 投屏页每 2 秒自动刷新实时字幕
- 会议控制台可打开当前会议投屏页
- 实时中文识别后自动生成英文字幕
- Gemini 文本翻译优先生成英文字幕
- Gemini 未配置或调用失败时自动 Mock Fallback
- Gemini 会议字幕风格提示词
- Gemini 翻译结果清洗
- Gemini 翻译延迟记录
- Gemini 错误分类与一次重试
- SQLite 保存 `english_transcript_text`
- SQLite 保存 `translation_provider`
- SQLite 保存 `translation_latency_ms`
- `/api/realtime/bilingual/{meeting_id}` 返回中英双语字幕
- `/ws/realtime/{meeting_id}` 推送实时中英双语字幕
- 投屏页同步显示中文与 English 字幕
- 投屏页优先使用 WebSocket 实时刷新字幕
- 投屏页保留 2 秒 Polling Fallback
- 会议控制台显示 Current Translation
- 会议控制台显示 Translation Provider
- 会议控制台显示 WebSocket Status
- 投屏页显示 Translation: Gemini / Mock
- 投屏页显示 Realtime: WebSocket / Polling Fallback
- 结束会议并归档到 `meeting_archive`
- Rule Based 会议纪要生成

## Alpha 1.2 WebSocket 字幕推送

Alpha 1.2 将投屏页从单纯 2 秒轮询升级为 WebSocket 优先推送：

- 后端 WebSocket：`ws://localhost:8000/ws/realtime/{meeting_id}`
- 投屏页：`/screen?meeting_id=xxx`
- 控制台显示：`WebSocket Status: Connected / Disconnected / Fallback Polling / Error`
- 投屏页显示：`Realtime: WebSocket` 或 `Realtime: Polling Fallback`

当 WebSocket 不可用时，前端自动保留原有 2 秒轮询兜底，不影响字幕演示闭环。

## Alpha 1.2.1 Field Test Preparation

当前版本用于 Alpha 现场验证准备，不新增核心功能。

明天真实会议测试前应先查看：

```text
docs/FIELD_TEST_CHECKLIST.md
```

测试后填写：

```text
docs/FIELD_TEST_REPORT_TEMPLATE.md
```

问题记录使用：

```text
docs/ISSUE_FEEDBACK_TEMPLATE.md
```

测试后复盘使用：

```text
docs/POST_TEST_REVIEW_TEMPLATE.md
```

## Alpha 1.2.2 Field Test Focus

本次现场测试重点不是投屏。

本次测试重点：

1. 实时翻译准确率
2. 实时翻译响应速度
3. 会议完整流程顺畅度
4. 笔记本内置麦克风识别率

投屏页本次只做基础打开检查，不评价大屏显示质量、投影仪适配或远距离可读性。

现场记录以 `docs/FIELD_TEST_REPORT_TEMPLATE.md` 为准，复盘结论记录到 `docs/POST_TEST_REVIEW_TEMPLATE.md`。

- 会议纪要页面显示摘要、核心观点、待办事项、下一步计划
- 重新打开会议可查看历史纪要
- 首页提供 Start First Real Meeting Demo 一键演示入口
- Alpha 1.2 Demo Guide 已更新
- Alpha 1.2 演示前环境检查脚本已可用
- Alpha 1.2 前后端启动脚本已可用
- Gemini API Setup 文档已新增
- Gemini API Key 本机配置成功
- Gemini 真实文本翻译验收通过

## Alpha 1.2.2-hotfix Realtime Audio Stability

本 hotfix 重点修复实时字幕只能识别前 3 秒的问题。

修复内容：

- 前端实时录音 chunk 从 3 秒调整为 8 秒，减少不可独立解码 WebM chunk。
- 后端为每个 meeting 保留最近 3 个有效 chunk，并优先使用 rolling audio window 识别。
- rolling window 合并失败时回退到当前有效 chunk，不中断会议。
- 连续无效 chunk 时先显示 `Waiting for valid speech input...`，避免过早提示麦克风不稳定。
- 新增 `GET /api/translation/status`，用于检查 Gemini API Key 是否已配置、当前 provider 和模型名，不返回 Key 明文。

长期方向：后续应改为 WAV/PCM 或更稳定的音频流处理方案。

## 当前 API

- `GET /api/health`
- `POST /api/meeting/create`
- `GET /api/meeting/list`
- `GET /api/meeting/{meeting_id}`
- `POST /api/audio/upload`
- `POST /api/transcription/start`
- `GET /api/transcription/{meeting_id}`
- `GET /api/transcription/model-status`
- `GET /api/translation/status`
- `POST /api/realtime/transcribe-chunk`
- `GET /api/realtime/transcript/{meeting_id}`
- `GET /api/realtime/bilingual/{meeting_id}`，返回 `provider` 和 `latency_ms`
- `WS /ws/realtime/{meeting_id}`
- `POST /api/minutes/generate`
- `POST /api/meeting/start`
- `POST /api/meeting/end`
- `POST /api/meeting/export`

## 当前禁止开发

- AI语音同传
- 声纹克隆
- APP客户端
- Zoom插件
- Teams插件
- 用户系统
- 支付系统
- SaaS订阅
- 多语言同步输出
- 手机扫码字幕
- 数据统计中心
- CRM功能
- 企业管理后台

这些功能全部延后，直到 First Real Meeting 核心闭环完成。

## Whisper模型管理

TransForum AI 采用本地模型优先策略。

会议现场不依赖网络下载模型，不自动访问 Hugging Face，也不自动拉取模型。

默认模型目录：

```text
D:\transforum-ai\models\whisper
```

默认后端配置：

```text
TRANSFORUM_WHISPER_MODEL=tiny
TRANSFORUM_WHISPER_MODEL_PATH=D:/transforum-ai/models/whisper
```

模型状态检查：

```text
http://localhost:8000/api/transcription/model-status
```

当前 tiny 模型已安装并通过验证：

```text
D:\transforum-ai\models\whisper\tiny
```

模型来源：

```text
Systran/faster-whisper-tiny
```

当前验证结果：

```json
{
  "installed": true,
  "model": "tiny",
  "path": "D:/transforum-ai/models/whisper",
  "model_path": "D:/transforum-ai/models/whisper/tiny",
  "message": "Ready"
}
```

如果模型不存在，系统返回 `MODEL_NOT_FOUND`，并提示先安装 Whisper 模型。

详细说明见：

```text
docs/WHISPER_MODEL_SETUP.md
```

## Gemini 文本翻译配置

Alpha 1.1.2 已优化 Gemini 翻译提示词、结果清洗、错误分类、fallback 重试和延迟记录。

配置模板：

```text
backend/.env.example
```

本地配置：

```text
backend/.env
```

示例：

```text
GEMINI_API_KEY=你的key
GEMINI_TRANSLATION_MODEL=gemini-3.5-flash
```

不要提交真实 API Key。详细说明见：

```text
docs/GEMINI_SETUP.md
```

## Alpha 0.5.1 办公电脑 UAT

时间标签：2026-06-08-TASK-005B-UAT

验收结论：

- Whisper tiny 模型已安装到 `D:\transforum-ai\models\whisper\tiny`。
- `/api/transcription/model-status` 返回 `installed=true`、`message=Ready`。
- 办公电脑本地测试音频已保存到 `D:\transforum-ai\data\audio\meeting_29357c757f4b_20260608_084530.wav`。
- 中文逐字稿已保存到 `D:/transforum-ai/data/transcripts/meeting_29357c757f4b_transcript.txt`。
- SQLite 已写入 `transcript_status=completed`、`transcript_file`、`transcript_text`。
- 识别耗时约 4.57 秒。
- 业务转写使用 `local_files_only=True`，不依赖运行时在线下载。

## Codex Task Label Rule

所有 Codex 工作指令必须包含时间标签，格式为：

```text
YYYY-MM-DD-TASK-编号
```

示例：

```text
2026-06-07-TASK-002
```

每次任务完成后，必须在回复中明确写出：

- 任务编号
- 时间标签
- 完成状态
- 主要修改文件
- 验收结果

## Development Version Rule

TransForum AI 使用阶段性开发版本号。

当前版本：

```text
TransForum AI Alpha 1.2.2-hotfix
```

版本规则：

- Alpha 0.1：项目骨架完成
- Alpha 0.1.1：项目迁移到 D:\transforum-ai 并建立任务标签与版本规则
- Alpha 0.2：会议创建与基础控制台可用
- Alpha 0.3：麦克风接入与语音识别可用
- Alpha 0.4：录音文件 Whisper 识别入口可用
- Alpha 0.4.1：Whisper 本地模型优先管理可用
- Alpha 0.4.2：Whisper tiny 本地模型 Ready 验证完成
- Alpha 0.5：本地 Whisper 中文逐字稿可用
- Alpha 0.5.1：办公电脑 Whisper tiny 本地模型安装与中文逐字稿 UAT 通过
- Alpha 0.6：实时中文字幕基础能力可用
- Alpha 0.7：中文字幕投屏模式可用
- Alpha 0.8：中英双语字幕可用
- Alpha 0.9：会议存档与会后内容整理可用
- Alpha 1.0：First Real Meeting Demo 可演示
- Alpha 1.0.1：演示稳定性检查与启动流程优化
- Alpha 1.1：Gemini 真实文本翻译接入
- Alpha 1.1.1：Gemini API Key 本机配置与真实翻译验收通过
- Alpha 1.1.2：Gemini 翻译质量、稳定性与延迟记录优化
- Alpha 1.2：WebSocket 实时字幕推送与 Polling Fallback
- Alpha 1.2.1：真实会议现场测试文档准备
- Alpha 1.2.2：现场测试重点调整为翻译、流程和内置麦克风
- Alpha 1.2.2-hotfix：实时音频 chunk 稳定性修复

每完成一个里程碑阶段，必须更新 README.md 和 docs/DEVELOPMENT_PLAN.md 中的当前版本号。

