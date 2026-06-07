# Current Status

## 当前项目

项目名称：TransForum AI

当前开发版本号：TransForum AI Alpha 0.4.2

当前项目根目录：

```text
D:\transforum-ai
```

后续所有开发命令均应在该目录下执行。

## 当前阶段

First Real Meeting - Sprint 3A UAT：Whisper 本地 tiny 模型安装与验证。

本阶段目标不是开发新功能，而是确认会议现场可以使用项目内本地模型，不依赖运行时联网下载。

## 当前已完成

- TASK 001：项目骨架搭建
- TASK 002：项目迁移与版本规则
- TASK 002A：旧目录清理
- TASK 002B：Rule 1 项目状态文档规则
- TASK 003：会议创建业务功能
- TASK 004：会议音频采集、上传和保存链路
- TASK 005：录音文件 Whisper 语音识别接口与前端入口
- TASK 005A：Whisper 本地模型优先管理
- TASK 005A-UAT：本地 Whisper tiny 模型安装与 Ready 验证

## 当前可用功能

- 创建会议
- 保存会议到 SQLite
- 读取会议详情
- 查看最近会议列表
- 会议控制台展示会议信息
- 浏览器麦克风录音 UI
- 录音计时
- 音频上传到 FastAPI
- 音频保存到 `data/audio`
- Meeting 表记录音频文件路径和音频时长
- 启动录音文件语音识别 API
- 查询逐字稿状态 API
- 前端 Generate Transcript 按钮和 Transcript Preview 区域
- Whisper 本地模型状态检查
- 模型未安装时禁用 Generate Transcript
- 本地 tiny 模型安装后返回 Ready
- 模型不存在时返回 `MODEL_NOT_FOUND`，不自动联网下载

## 当前验收状态

- `faster-whisper`：已安装，版本 `1.2.1`。
- Whisper tiny 模型：已安装到 `D:\transforum-ai\models\whisper\tiny`。
- 模型来源：`Systran/faster-whisper-tiny`。
- 模型关键文件：`config.json`、`model.bin`、`tokenizer.json`、`vocabulary.txt`。
- 后端 Python 编译检查：通过。
- 前端 `npm install`：通过。
- 前端 `npm run build`：通过。
- 后端 `/api/health`：返回 `Alpha 0.4.2`。
- 后端 `/api/transcription/model-status`：返回 `installed=true`、`message=Ready`。
- 前端 `/meeting/live?meeting_id=meeting_dcfbfedd8e74`：HTTP 200，可访问。
- 前端 Alpha 0.4.2 页面内容：已通过 HTTP 验证。
- 内置浏览器可视化自动化：当前环境提示 browser-client 未被信任，未完成视觉读取；API 与前端代码逻辑已验证。

## 当前模型状态

```json
{
  "installed": true,
  "model": "tiny",
  "path": "D:/transforum-ai/models/whisper",
  "model_path": "D:/transforum-ai/models/whisper/tiny",
  "message": "Ready"
}
```

## 当前禁止开发

- 翻译
- 字幕
- GPT
- Gemini
- WebSocket
- 会议纪要
- DOCX 导出
- 用户登录
- 支付系统
- 手机扫码字幕
- 嘉宾专属词库
- 多语言扩展

## 更新规则

每个 TASK 完成后，Codex 必须更新以下三个文件：

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

## 当前最新任务记录

时间标签：2026-06-07-TASK-005A-UAT

开发版本号：TransForum AI Alpha 0.4.2

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

- tiny 模型已安装到项目可管理目录。
- 模型目录非空。
- `model-status` 返回 `installed=true`。
- `message` 返回 `Ready`。
- 业务接口不再运行时自动访问 Hugging Face 下载模型。
- 前端生产构建通过，会议控制台页面可访问。

下一步任务：

- TASK 005B：本地 Whisper 中文识别验证
