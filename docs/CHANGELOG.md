# Changelog

本文件记录 TransForum AI 的阶段性版本变更。

## TransForum AI Alpha 1.0

时间标签：2026-06-08-TASK-009

里程碑：First Real Meeting Demo

新增：

- 首页 `Start First Real Meeting Demo` 演示入口。
- 首页演示流程说明。
- 会议控制台 `Current Step` 流程提示。
- 投屏页 `Alpha 1.0 Demo Mode`。
- `docs/ALPHA_1_DEMO_GUIDE.md`。

变更：

- 创建会议默认名称改为 `TransForum AI Demo Meeting`。
- 创建会议默认 Source Language 为 `Chinese zh`，Target Language 为 `English en`。
- 会议控制台按钮顺序调整为 Start Realtime Caption、Open Screen Mode、End Meeting & Generate Minutes。
- Generate Transcript 标记为 `Optional: Generate Full Transcript`。
- 会议纪要页增加 Back to Home、Back to Console、Open Screen Mode。
- `/api/health` 版本更新为 Alpha 1.0。
- README、PROJECT_RULES、CURRENT_STATUS、TASK_HISTORY、CHANGELOG、DEVELOPMENT_PLAN、TECHNICAL_DEBT 更新到 Alpha 1.0。

完成状态：代码实现完成，真实麦克风浏览器演示需人工确认。

验收结果：

- 后端 Python 编译检查通过。
- 前端构建通过。
- `/api/health` 返回 `Alpha 1.0`。
- 首页 Alpha 1.0 演示入口可访问。
- 纪要页和投屏页可访问。

技术债务：

- 新增债务 4 项。
- 已解决债务 0 项。
- 当前债务总数 9 项。

## TransForum AI Alpha 0.9

时间标签：2026-06-08-TASK-008

新增：

- `meeting_archive` 会议归档表。
- `meetings` 表纪要字段：`minutes_summary`、`minutes_key_points`、`minutes_action_items`、`minutes_next_steps`。
- `backend/services/minutes_service.py`。
- `POST /api/minutes/generate`。
- `/meeting/minutes?meeting_id=xxx` 会议纪要页面。
- Meeting Console 的 End Meeting 按钮。
- End Meeting 执行结束会议、归档、生成纪要并跳转纪要页。

变更：

- `/api/health` 版本更新为 Alpha 0.9。
- 前端首页、metadata 和 package 版本更新到 Alpha 0.9。
- README、CURRENT_STATUS、TASK_HISTORY、CHANGELOG、DEVELOPMENT_PLAN、TECHNICAL_DEBT 更新到 Alpha 0.9。

完成状态：代码实现完成，真实浏览器点击 End Meeting 链路需人工验收。

验收结果：

- 后端 Python 编译检查通过。
- 前端构建通过。
- `/api/health` 返回 `Alpha 0.9`。
- `/api/minutes/generate` 返回 `summary`、`key_points`、`action_items`、`next_steps`。
- `meeting_archive` 写入会议归档内容。
- `/meeting/minutes?meeting_id=xxx` 页面可构建。

技术债务：

- 新增债务 2 项。
- 已解决债务 0 项。
- 当前债务总数 5 项。

下一阶段建议：

- 2026-06-08-TASK-009：TransForum AI Alpha 1.0，First Real Meeting 演示闭环打磨。

## TransForum AI Alpha 0.8

时间标签：2026-06-08-TASK-007

新增：

- SQLite 字段 `english_transcript_text`。
- 翻译服务 `translate_zh_to_en(text)`。
- Gemini API 优先翻译路径。
- 未配置 Gemini API 时的 Mock 翻译回退。
- 实时 chunk 中文识别后自动生成英文字幕。
- `GET /api/realtime/bilingual/{meeting_id}`。
- 投屏页中英双语字幕布局。
- Meeting Console 显示 Current Translation。
- `docs/TECHNICAL_DEBT.md` 技术债记录。

变更：

- `/api/health` 版本更新为 Alpha 0.8。
- 前端首页、metadata 和 package 版本更新到 Alpha 0.8。
- README、CURRENT_STATUS、TASK_HISTORY、CHANGELOG、DEVELOPMENT_PLAN、TECHNICAL_DEBT 更新到 Alpha 0.8。

修改文件：

- backend/main.py
- backend/api/realtime.py
- backend/database/connection.py
- backend/models/meeting.py
- backend/services/meeting_repository.py
- backend/services/realtime_transcription_service.py
- backend/services/translation_service.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/app/screen/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- README.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md
- docs/DEVELOPMENT_PLAN.md
- docs/TECHNICAL_DEBT.md

完成状态：代码实现完成，真实 Gemini 在线翻译和浏览器麦克风投屏联动需按环境人工验收。

验收结果：

- 后端 Python 编译检查通过。
- 前端构建通过。
- `/api/health` 返回 `Alpha 0.8`。
- `/api/realtime/bilingual/{meeting_id}` 返回 `chinese`、`english`、`updated_at`。
- SQLite `meetings` 表包含 `english_transcript_text`。
- Mock 翻译链路可用。

技术债务：

- 新增债务 3 项。
- 已解决债务 1 项。
- 当前债务总数 3 项。

下一步任务建议：

- 2026-06-08-TASK-008：TransForum AI Alpha 0.9，会议存档与会后内容整理。

## TransForum AI Alpha 0.7

时间标签：2026-06-08-TASK-006

新增：

- `GET /api/realtime/transcript/{meeting_id}`。
- `/screen?meeting_id=xxx` 中文字幕投屏大屏模式。
- 投屏页显示最新字幕和最近 5 行字幕。
- 投屏页每 2 秒自动刷新实时字幕。
- 投屏页支持全屏投影。
- 会议控制台打开当前会议投屏页按钮。

变更：

- `/api/health` 版本更新为 Alpha 0.7。
- 前端首页、metadata 和 package 版本更新到 Alpha 0.7。
- README、CURRENT_STATUS、TASK_HISTORY、CHANGELOG、DEVELOPMENT_PLAN 更新到 Alpha 0.7。

修改文件：

- backend/main.py
- backend/api/realtime.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/app/meeting/live/page.tsx
- frontend/src/app/screen/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- README.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md
- docs/DEVELOPMENT_PLAN.md

完成状态：代码实现完成，真实浏览器投屏联动验收需用户在本机执行。

验收结果：

- 后端 Python 编译检查通过。
- 前端构建通过。
- `/api/health` 返回 `Alpha 0.7`。
- `/api/realtime/transcript/{meeting_id}` 可读取实时字幕。
- `/screen?meeting_id=xxx` 页面可打开并渲染大屏中文投屏样式。

下一步任务：

- 2026-06-08-TASK-007：TransForum AI Alpha 0.8，中英双语字幕。

## TransForum AI Alpha 0.6

时间标签：2026-06-08-TASK-005C

新增：

- 实时中文音频分片能力。
- `POST /api/realtime/transcribe-chunk`。
- 后端保存实时 chunk 到 `data/chunks`。
- 本地 Whisper tiny 分片中文识别。
- 会议控制台 Real-time Chinese Subtitles 区域。
- Start Realtime Caption 和 Stop Realtime Caption。
- 实时逐字稿 TXT 保存。
- SQLite `realtime_transcript_text` 字段。

变更：

- `/api/health` 版本更新为 Alpha 0.6。
- 前端首页、metadata 和 package 版本更新到 Alpha 0.6。
- README、CURRENT_STATUS、TASK_HISTORY、CHANGELOG、DEVELOPMENT_PLAN 更新到 Alpha 0.6。

修改文件：

- backend/main.py
- backend/api/realtime.py
- backend/database/connection.py
- backend/models/meeting.py
- backend/services/meeting_repository.py
- backend/services/realtime_transcription_service.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- README.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md
- docs/DEVELOPMENT_PLAN.md

完成状态：代码实现完成，真实浏览器麦克风人工验收需用户在本机执行。

验收结果：

- 后端 Python 编译检查通过。
- 前端构建通过。
- `/api/health` 返回 `Alpha 0.6`。
- `/api/realtime/transcribe-chunk` 已实现 multipart 接收、chunk 保存、本地模型识别、TXT 追加和 SQLite 追加。
- 浏览器真实麦克风授权、朗读 10 到 15 秒和页面实时字幕显示需人工确认。

下一步任务：

- 2026-06-08-TASK-007：TransForum AI Alpha 0.8，中英双语字幕。

## TransForum AI Alpha 0.5.1

时间标签：2026-06-08-TASK-005B-UAT

新增：

- 办公电脑本地 Whisper tiny 模型安装验收记录。
- 办公电脑中文测试音频逐字稿验收记录。

变更：

- 当前版本更新为 Alpha 0.5.1。
- README 与项目状态文档记录办公电脑 UAT 结果。
- `/api/health` 返回版本更新为 `Alpha 0.5.1`。
- 前端首页和页面 metadata 更新为 Alpha 0.5.1。

验收结果：

- `scripts/download_whisper_tiny.py` 下载 `Systran/faster-whisper-tiny` 成功。
- tiny 模型已保存到 `D:\transforum-ai\models\whisper\tiny`。
- `model-status` 返回 `installed=true`、`message=Ready`。
- UAT 测试会议：`meeting_29357c757f4b`。
- 测试音频：`D:\transforum-ai\data\audio\meeting_29357c757f4b_20260608_084530.wav`。
- 逐字稿文件：`D:/transforum-ai/data/transcripts/meeting_29357c757f4b_transcript.txt`。
- `transcript_status=completed`。
- 识别耗时约 4.57 秒。
- 业务转写仍使用本地模型，不依赖运行时在线下载。

下一步任务：

- 2026-06-08-TASK-006：TransForum AI Alpha 0.6，中英翻译基础能力。

## TransForum AI Alpha 0.5

时间标签：2026-06-08-TASK-005B

新增：

- 本地 Whisper 中文逐字稿生成能力。
- 逐字稿 TXT 保存到 `data/transcripts`。
- 逐字稿结果写入 SQLite。
- 后端转写服务单元测试。
- PROJECT_RULES Rule 2：默认中文汇报和文档规则。

变更：

- `/api/health` 版本更新为 Alpha 0.5。
- `POST /api/transcription/start` 改为同步返回转写最终结果。
- Whisper 转写参数固定为 `language="zh"`、`task="transcribe"`。
- Whisper 模型加载保持 `local_files_only=True`。
- 前端 Generate Transcript 在处理中显示 `Processing...`。
- 前端成功后直接显示 `Completed` 和逐字稿预览。
- README、CURRENT_STATUS、TASK_HISTORY、DEVELOPMENT_PLAN、WHISPER_MODEL_SETUP 更新到 Alpha 0.5。

修改文件：

- PROJECT_RULES.md
- README.md
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
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md
- docs/DEVELOPMENT_PLAN.md
- docs/WHISPER_MODEL_SETUP.md

完成状态：代码实现完成；真实 Whisper 转写验收受本机资源缺失阻塞。

验收结果：

- 后端单元测试已通过。
- 后端 Python 编译检查已通过。
- 前端 `npm run build` 已通过。
- `GET /api/transcription/model-status` 当前返回 `installed=false`、`message=Model not found`。
- 指定验收音频不存在，当前 SQLite 无可复用会议记录。
- 真实音频转写、TXT 实际生成、SQLite 实际写入和前端真实点击验收需在本地模型与音频恢复后执行。

下一步任务：

- 2026-06-08-TASK-006：TransForum AI Alpha 0.6，中英翻译基础能力。

## TransForum AI Alpha 0.4.2

时间标签：2026-06-07-TASK-005A-UAT

新增：

- `scripts/download_whisper_tiny.py`。
- 本地 tiny 模型目录 `models/whisper/tiny`。

变更：

- 当前版本更新为 Alpha 0.4.2。
- README 增加 tiny 模型安装路径、来源和 Ready 验证结果。
- Whisper 模型安装文档补充可控脚本安装方式、手动安装方式和当前 UAT 结果。
- CURRENT_STATUS 更新为本地模型 Ready 状态。

修改文件：

- README.md
- backend/main.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- docs/ARCHITECTURE.md
- docs/DEVELOPMENT_PLAN.md
- docs/WHISPER_MODEL_SETUP.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md
- scripts/download_whisper_tiny.py
- models/whisper/tiny/*

完成状态：完成

验收结果：

- tiny 模型已安装到 `D:\transforum-ai\models\whisper\tiny`。
- 模型关键文件存在：`config.json`、`model.bin`、`tokenizer.json`、`vocabulary.txt`。
- 后端 Python 编译检查通过。
- 前端 `npm install` 通过。
- 前端 `npm run build` 通过。
- `/api/health` 返回 `Alpha 0.4.2`。
- `/api/transcription/model-status` 返回 `installed=true`、`message=Ready`。
- 前端会议控制台路由可访问。
- 系统不再依赖运行时在线下载 Whisper 模型。

下一步任务：

- TASK 005B：本地 Whisper 中文识别验证

## TransForum AI Alpha 0.4.1

时间标签：2026-06-07-TASK-005A

新增：

- `models/whisper` 本地模型目录。
- `backend/.env`。
- `backend/config.py`。
- `GET /api/transcription/model-status`。
- 前端 Whisper Status。
- `docs/WHISPER_MODEL_SETUP.md`。

变更：

- Whisper 加载策略改为本地模型优先。
- 模型不存在时返回 `MODEL_NOT_FOUND`。
- 系统不再自动访问 Hugging Face 下载模型。
- Generate Transcript 在模型未安装时禁用。
- `/api/health` 版本更新为 Alpha 0.4.1。
- README、PROJECT_RULES、DEVELOPMENT_PLAN、ARCHITECTURE 更新到 Alpha 0.4.1。

修改文件：

- README.md
- .gitignore
- PROJECT_RULES.md
- backend/.env
- backend/config.py
- backend/main.py
- backend/api/transcription.py
- backend/services/transcription_service.py
- models/whisper/.gitkeep
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- docs/ARCHITECTURE.md
- docs/DEVELOPMENT_PLAN.md
- docs/WHISPER_MODEL_SETUP.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md

完成状态：完成

验收结果：

- 后端 Python 语法检查通过。
- 前端构建通过。
- `/api/health` 返回 `Alpha 0.4.1`。
- `/api/transcription/model-status` 返回模型未安装状态。
- `/api/transcription/start` 在模型未安装时返回 `MODEL_NOT_FOUND`。
- 前端页面可访问。

下一步任务：

- TASK 005B：本地 Whisper 模型识别验证

## TransForum AI Alpha 0.4

时间标签：2026-06-07-TASK-005

新增：

- `data/transcripts` 逐字稿目录。
- Meeting 表逐字稿字段：`transcript_file`、`transcript_text`、`transcript_status`。
- `backend/services/transcription_service.py`。
- `POST /api/transcription/start`。
- `GET /api/transcription/{meeting_id}`。
- 会议控制台 Speech Recognition 区域。
- Generate Transcript 按钮。
- Transcript Preview。

变更：

- `/api/health` 版本更新为 Alpha 0.4。
- README、PROJECT_RULES、DEVELOPMENT_PLAN、ARCHITECTURE 更新到 Alpha 0.4。
- `.gitignore` 忽略本地逐字稿产物，保留 `data/transcripts/.gitkeep`。

修改文件：

- README.md
- .gitignore
- PROJECT_RULES.md
- backend/main.py
- backend/requirements.txt
- backend/api/transcription.py
- backend/database/connection.py
- backend/models/meeting.py
- backend/services/meeting_repository.py
- backend/services/transcription_service.py
- data/transcripts/.gitkeep
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- docs/ARCHITECTURE.md
- docs/DEVELOPMENT_PLAN.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md

完成状态：否，受模型下载失败阻塞

验收结果：

- `faster-whisper 1.2.1` 安装成功。
- 前端构建通过。
- 后端依赖安装和语法检查通过。
- `/api/health` 返回 `Alpha 0.4`。
- `/api/transcription/start` 返回 `processing`。
- `/api/transcription/{meeting_id}` 返回 `failed`。
- Whisper 模型下载失败，本地没有模型缓存。
- 中文逐字稿 txt 未生成。

下一步任务：

- 修复 Whisper 模型下载或配置本地模型路径后重试 TASK 005。
- 原计划后续任务：TASK 006：实时字幕（单语）。

## TransForum AI Alpha 0.3

时间标签：2026-06-07-TASK-004

新增：

- 浏览器麦克风录音 UI。
- Recording Duration 计时。
- Audio Upload Status。
- `/api/audio/upload`。
- `data/audio` 音频保存目录。
- Meeting 表音频字段：`audio_file`、`audio_duration`。
- 可播放测试音频保存验证。

变更：

- `/api/health` 版本更新为 Alpha 0.3。
- README、PROJECT_RULES、DEVELOPMENT_PLAN、ARCHITECTURE 更新到 Alpha 0.3。
- `.gitignore` 忽略本地音频产物，保留 `data/audio/.gitkeep`。

修改文件：

- README.md
- .gitignore
- PROJECT_RULES.md
- backend/main.py
- backend/requirements.txt
- backend/api/audio.py
- backend/database/connection.py
- backend/models/meeting.py
- backend/services/meeting_repository.py
- backend/uploads/.gitkeep
- data/audio/.gitkeep
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- docs/ARCHITECTURE.md
- docs/DEVELOPMENT_PLAN.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md

完成状态：部分完成

验收结果：

- 前端构建通过。
- 后端依赖安装和语法检查通过。
- `/api/health` 返回 `Alpha 0.3`。
- `/api/audio/upload` 通过 multipart 测试。
- SQLite 音频字段写入成功。
- 可播放 WAV 测试音频已保存。
- 真实浏览器麦克风录音流程需人工确认。

下一步任务：

- TASK 005：Whisper Speech Recognition

## TransForum AI Alpha 0.2

时间标签：2026-06-07-TASK-003

新增：

- 会议创建功能
- SQLite 本地保存会议
- 会议详情读取
- 最近会议列表
- 前端创建会议到控制台跳转流程

变更：

- `/api/health` 版本更新为 Alpha 0.2
- README、PROJECT_RULES、DEVELOPMENT_PLAN、ARCHITECTURE 更新到 Alpha 0.2

修改文件：

- README.md
- .gitignore
- PROJECT_RULES.md
- backend/main.py
- backend/api/meeting.py
- backend/models/meeting.py
- backend/database/connection.py
- backend/services/meeting_repository.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/app/layout.tsx
- frontend/src/app/page.tsx
- frontend/src/app/meeting/new/page.tsx
- frontend/src/app/meeting/live/page.tsx
- frontend/src/components/CreateMeetingForm.tsx
- frontend/src/components/MeetingConsole.tsx
- frontend/src/components/RecentMeetings.tsx
- frontend/src/services/api.ts
- frontend/src/types/meeting.ts
- docs/ARCHITECTURE.md
- docs/DEVELOPMENT_PLAN.md
- docs/CURRENT_STATUS.md
- docs/TASK_HISTORY.md
- docs/CHANGELOG.md

完成状态：完成

验收结果：

- 前端构建通过。
- 后端语法检查通过。
- `pip install -r requirements.txt` 通过。
- `npm install` 通过。
- `/api/health` 返回 `Alpha 0.2`。
- 会议创建、列表、详情 API 已通过。
- SQLite 文件和 `meetings` 表已验证。
- 前端首页和会议控制台路由可访问。
- 浏览器点击自动化工具不可用，未做真实点击自动化；表单提交代码路径和后端 API 已验证。

下一步任务：

- TASK 004：麦克风接入与语音输入测试

## TransForum AI Alpha 0.1.1

时间标签：2026-06-07-TASK-002B

变更内容：

- 新增永久规则 Rule 1。
- 明确每个 Codex TASK 完成后必须自动更新 `docs/CURRENT_STATUS.md`、`docs/TASK_HISTORY.md`、`docs/CHANGELOG.md`。
- 明确每次记录必须包含时间标签、开发版本号、修改文件、完成状态、验收结果和下一步任务。

验收结果：

- Rule 1 已写入 README.md。
- Rule 1 已写入 PROJECT_RULES.md。
- 三个固定治理文档已同步更新。

下一步任务：

- 后续所有 TASK 严格按 Rule 1 自动更新状态文档。

## TransForum AI Alpha 0.1.1

时间标签：2026-06-07-TASK-002A

变更内容：

- 项目主目录已迁移至 `D:\transforum-ai`。
- 建立 Codex Task Label Rule。
- 建立 Development Version Rule。
- 清理旧 C 盘项目目录中的 `frontend` 残留文件夹。
- 新增固定项目治理文档：`CHANGELOG.md`、`TASK_HISTORY.md`、`CURRENT_STATUS.md`。

验收结果：

- 前端构建通过。
- 前端页面可通过 `http://localhost:3001` 访问。
- 后端 `/api/health` 返回 `Alpha 0.1.1`。

## 更新规则

每个 TASK 完成后，Codex 必须更新本文件，记录：

- 时间标签
- 开发版本号
- 修改文件
- 完成状态
- 验收结果
- 下一步任务
- 未完成事项（如有）
