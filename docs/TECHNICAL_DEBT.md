# Technical Debt

本文档记录 TransForum AI 每个 TASK 完成时发现、遗留、解决的技术债务。

## 记录规则

从 Alpha 0.8 开始，每个 TASK 完成时必须检查：

1. 遗留问题
2. 临时方案
3. 未自动化验收部分
4. 环境依赖问题
5. 性能风险

## 当前状态

规则生效版本：TransForum AI Alpha 0.8

当前版本：TransForum AI Alpha 1.1.1

当前债务总数：11

## OPEN

### 2026-06-08-TASK-011A

时间标签：2026-06-08-TASK-011A

开发版本号：TransForum AI Alpha 1.1.1

新增债务：

- 无

已解决债务：

- [DEBT-011] Gemini API Key 需要用户本地配置：本机 `backend/.env` 已配置成功，`GEMINI_API_KEY_CONFIGURED=yes`，并通过真实 Gemini 翻译验收。

当前债务总数：11

### 2026-06-08-TASK-011

- [DEBT-012] 类型：质量风险
  描述：Gemini 翻译质量需要更多真实会议语料测试。
  影响：本机单句测试已通过，但专业场景、长句和术语翻译质量仍未充分验证。
  修复建议：收集真实会议中文字幕样本，建立人工验收清单并迭代 prompt。
  状态：open

- [DEBT-013] 类型：未完成功能
  描述：Gemini Live API 暂未接入。
  影响：当前只做文本翻译，不支持语音到语音实时同传。
  修复建议：后续将 `gemini-3.5-live-translate-preview` 作为 AI 有声同传专项任务评估。
  状态：open

- [DEBT-014] 类型：性能风险
  描述：Gemini 调用延迟可能影响实时字幕体验。
  影响：网络延迟或 API 响应慢时，英文字幕可能滞后于中文字幕。
  修复建议：后续增加异步队列、超时配置、缓存和延迟监控。
  状态：open

### 2026-06-08-TASK-010

- [DEBT-010] 类型：兼容性 / 环境依赖问题
  描述：Alpha 1.0.1 新增的 PowerShell 启动脚本仍需在不同 Windows 环境反复测试。
  影响：演示前启动步骤已简化，但不同 PowerShell 策略、端口占用、Python/Node 路径差异仍可能造成启动失败。
  修复建议：在至少两台 Windows 机器上执行 `scripts\check_environment.ps1`、`scripts\start_backend.ps1`、`scripts\start_frontend.ps1`，并根据失败场景补充端口检测和自动 fallback。
  状态：open

### 2026-06-08-TASK-009

- [DEBT-007] 类型：性能 / 实时性风险
  描述：投屏页继续使用 2 秒轮询，仍未支持 WebSocket 推送。
  影响：投屏字幕存在刷新延迟，长时间会议会产生额外轮询请求。
  修复建议：后续引入 WebSocket 或 Server-Sent Events 推送字幕。
  状态：open

- [DEBT-008] 类型：未完成功能
  描述：仍未支持 DOCX 导出。
  影响：会议成果只能在页面和数据库中查看，不能直接导出正式文档。
  修复建议：后续基于纪要和逐字稿生成 DOCX。
  状态：open

- [DEBT-009] 类型：未完成功能
  描述：仍未支持会议历史管理页面。
  影响：用户无法通过 UI 浏览、搜索和管理历史会议归档。
  修复建议：后续新增会议历史列表、搜索、详情和归档入口。
  状态：open

### 2026-06-08-TASK-008

- [DEBT-004] 类型：临时方案
  描述：会议纪要当前采用 Rule Based 生成，不依赖 Gemini 或其他大模型。
  影响：纪要链路可跑通，但摘要质量有限，不能完全替代 AI 会议纪要。
  修复建议：后续接入 Gemini 或其他本地 / 云端模型生成结构化纪要。
  状态：open

- [DEBT-005] 类型：未完成功能
  描述：`meeting_archive` 已写入数据库，但尚未提供独立的会议归档列表或搜索页面。
  影响：会议内容已归档，但用户需要通过会议 ID 或数据库才能浏览全部归档。
  修复建议：后续新增会议归档列表页和按会议名称 / 时间搜索能力。
  状态：open

### 2026-06-08-TASK-007

- [DEBT-002] 类型：未自动化验收
  描述：浏览器麦克风授权、真实讲话 10 秒、投屏页实时刷新仍需人工验证。
  影响：自动化测试覆盖了 API 和构建，但未完全覆盖真实会议现场交互。
  修复建议：后续引入浏览器端 E2E 测试或保留标准 UAT 清单。
  状态：open

- [DEBT-003] 类型：性能风险
  描述：实时识别每个 chunk 都重新创建 WhisperModel。
  影响：长会议或低配置设备可能出现延迟和 CPU 压力。
  修复建议：后续将 WhisperModel 做成本地进程级缓存或服务级单例。
  状态：open

## CLOSED

- [DEBT-001] 关闭于 2026-06-08-TASK-011：Gemini 文本翻译已接入，未配置 key 时保留 Mock Fallback。
- [DEBT-006] 关闭于 2026-06-08-TASK-011：Alpha 1.1 已接入真实 Gemini 文本翻译服务。
- [DEBT-011] 关闭于 2026-06-08-TASK-011A：本机 Gemini API Key 已配置成功，真实 Gemini 翻译验收通过。
