# Changelog

本文件记录 TransForum AI 的阶段性版本变更。

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
