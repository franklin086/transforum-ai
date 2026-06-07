# TransForum AI

当前版本：TransForum AI Alpha 0.4.2

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

## First Real Meeting 核心流程

创建会议 → 接入麦克风 → 实时语音识别 → 实时中英翻译 → 双语字幕投屏 → 保存会议内容 → 生成中英文逐字稿和会议纪要 → 导出会议成果

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
- Whisper 本地模型检查

## 当前 API

- `GET /api/health`
- `POST /api/meeting/create`
- `GET /api/meeting/list`
- `GET /api/meeting/{meeting_id}`
- `POST /api/audio/upload`
- `POST /api/transcription/start`
- `GET /api/transcription/{meeting_id}`
- `GET /api/transcription/model-status`
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
TransForum AI Alpha 0.4.2
```

版本规则：

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

