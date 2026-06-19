# Technical Debt

## Alpha 1.2.4 TASK 013E Technical Debt Update

Time label: 2026-06-XX-TASK-013E

Version: TransForum AI Alpha 1.2.4

New debt:

- [DEBT-041] The 8-second chunk strategy has inherent 8+ second latency and is not suitable for a true simultaneous interpretation experience.
- [DEBT-042] Whisper tiny with a laptop built-in microphone is not accurate enough for reliable real meeting captions and needs field validation.
- [DEBT-043] Future work should evaluate WAV/PCM input, external microphones, Whisper base/small, Gemini Live, or streaming ASR.

## Alpha 1.2.4 Technical Debt Update

时间标签：2026-06-XX-TASK-013D

开发版本号：TransForum AI Alpha 1.2.4

当前债务总数：36

新增债务：

- [DEBT-038] Gemini 服务返回 503 high demand 时无法完成成功态浏览器验收，需要稍后重试。
- [DEBT-039] 当前 Codex 浏览器自动化受信任边界阻止，人工浏览器验收需用户本机执行。
- [DEBT-040] Meeting Minutes 当前仍是归档型摘要，长期应接入更高质量的 AI 纪要生成。

已解决债务：

- 默认 Mock EN 文案不再由后端 fallback 自动生成。

## Alpha 1.2.3 Technical Debt Update

时间标签：2026-06-XX-TASK-013C

开发版本号：TransForum AI Alpha 1.2.3

当前债务总数：33

新增债务：

- [DEBT-035] 长期仍建议改为 WAV/PCM 音频输入，避免 WebM chunk 与 rolling window 对 ffmpeg 合并能力的依赖。
- [DEBT-036] 长会议实时识别稳定性仍需现场测试，尤其是 45 秒以上连续发言和多人轮流发言。
- [DEBT-037] 笔记本内置麦克风识别仍需真实会议验证，需记录距离、噪音和连续讲话条件下的准确率。

已解决债务：

- 无。

## Alpha 1.2.2-hotfix Technical Debt Update

时间标签：2026-06-XX-TASK-013B

开发版本号：TransForum AI Alpha 1.2.2-hotfix

当前债务总数：30

新增债务：

- [DEBT-032] 长期应改为 WAV/PCM 音频输入。
- [DEBT-033] 长期应使用更稳定的音频流处理方案。
- [DEBT-034] 笔记本内置麦克风识别仍需现场验证。

已解决债务：

- 无。

## Alpha 1.2.2 Current Technical Debt Update

时间标签：2026-06-09-TASK-014A

开发版本号：TransForum AI Alpha 1.2.2

当前债务总数：27

新增债务：

- [DEBT-027] 笔记本内置麦克风识别效果需真实会议验证。
- [DEBT-028] Gemini 翻译延迟需现场测试。
- [DEBT-029] Gemini 翻译准确率需真实会议语料验证。
- [DEBT-030] 完整会议流程仍需真实会议压力测试。
- [DEBT-031] 会议纪要质量需真实会议记录验证。

已解决债务：

- 无。

验证方式：

- 使用 Alpha 1.2.2 现场测试清单和报告模板记录真实会议测试结果。
- 根据现场评分和问题反馈决定 Alpha 1.2.3 或 Alpha 1.3 的修复优先级。

本文档记录 TransForum AI 每个 TASK 完成时发现、遗留、解决的技术债务。

## 当前状态

规则生效版本：TransForum AI Alpha 0.8

当前版本：TransForum AI Alpha 1.2.4

当前债务总数：27

## OPEN

### 2026-06-09-TASK-014A

时间标签：2026-06-09-TASK-014A

开发版本号：TransForum AI Alpha 1.2.2

新增债务：

- [DEBT-027] 类型：现场测试 / 音频输入风险
  描述：笔记本内置麦克风识别效果需真实会议验证。
  影响：仅依靠内置麦克风时，距离、回声和环境噪音可能导致 Whisper 识别准确率下降。
  修复建议：明天现场分别记录近距离、正常会议距离、噪音环境、连续讲话和多人轮流讲话的识别评分。
  状态：open

- [DEBT-028] 类型：现场测试 / 性能风险
  描述：Gemini 翻译延迟需现场测试。
  影响：真实会议中连续 chunk 可能产生延迟波动，影响参会者理解英文字幕。
  修复建议：使用 3 秒、5 秒、8 秒阈值记录每轮中文发言到英文字幕出现的估算延迟。
  状态：open

- [DEBT-029] 类型：现场测试 / 翻译质量风险
  描述：Gemini 翻译准确率需真实会议语料验证。
  影响：会议术语、长句、口语化表达和不完整句子可能造成漏译、误译或解释性废话。
  修复建议：记录典型中文原句、系统英文翻译和人工评价，形成后续 prompt 或术语表优化依据。
  状态：open

- [DEBT-030] 类型：现场测试 / 流程稳定性风险
  描述：完整会议流程仍需真实会议压力测试。
  影响：从启动、创建会议、实时字幕、停止会议到生成会议纪要的完整流程可能出现卡顿、报错或页面无响应。
  修复建议：按现场测试报告逐项记录启动后端、启动前端、创建会议、实时翻译、结束会议和查看会议记录是否顺畅。
  状态：open

- [DEBT-031] 类型：现场测试 / 会议纪要质量风险
  描述：会议纪要质量需真实会议记录验证。
  影响：真实会议语料可能包含长段口语、错字、断句和多人发言，Rule Based 纪要质量可能不足。
  修复建议：现场测试后对会议纪要的 Summary、Key Points、Action Items、Next Steps 进行人工评价。
  状态：open

已解决债务：

- 无。

当前债务总数：27

### 2026-06-09-TASK-014

时间标签：2026-06-09-TASK-014

开发版本号：TransForum AI Alpha 1.2.1

新增债务：

- [DEBT-021] 类型：现场测试 / 环境依赖问题
  描述：真实会议现场麦克风稳定性待验证。
  影响：不同麦克风、会议室距离、噪声和回声可能影响 Whisper 中文识别连续性。
  修复建议：现场测试时记录麦克风型号、摆放位置、噪声环境和典型识别错误。
  状态：open

- [DEBT-022] 类型：现场测试 / 环境依赖问题
  描述：真实会议场地网络稳定性待验证。
  影响：Gemini 翻译和 WebSocket 连接可能受弱网、代理或会议室网络限制影响。
  修复建议：记录网络类型、延迟、断连情况，并准备 Mock Fallback 和中文字幕优先测试方案。
  状态：open

- [DEBT-023] 类型：现场测试 / 性能风险
  描述：Gemini 长时间连续翻译表现待验证。
  影响：连续会议语料下可能出现延迟波动、速率限制或术语不一致。
  修复建议：现场测试记录翻译 provider、latency、典型翻译错误和 fallback 发生次数。
  状态：open

- [DEBT-024] 类型：现场测试 / 稳定性风险
  描述：WebSocket 长时间连接稳定性待验证。
  影响：投屏页长时间打开时可能出现断线、恢复慢或回退到 Polling Fallback。
  修复建议：现场测试记录 `Realtime: WebSocket` 持续时长、掉线次数和 fallback 是否可用。
  状态：open

- [DEBT-025] 类型：现场测试 / UI体验问题
  描述：投屏在不同会议室设备上的显示效果待验证。
  影响：投影仪、LED 屏、分辨率和浏览器缩放差异可能影响字幕可读性。
  修复建议：现场测试记录屏幕尺寸、分辨率、观看距离和中英文字号是否清晰。
  状态：open

- [DEBT-026] 类型：现场测试 / 质量风险
  描述：会议纪要在真实会议语料下质量待验证。
  影响：当前 Rule Based 纪要在真实长会议、多人发言和不完整字幕下可能质量有限。
  修复建议：现场测试后对 Summary、Key Points、Action Items、Next Steps 进行人工评分并记录缺口。
  状态：open

已解决债务：

- 无。

当前债务总数：22

### 2026-06-09-TASK-013

时间标签：2026-06-09-TASK-013

开发版本号：TransForum AI Alpha 1.2

新增债务：

- [DEBT-017] 类型：稳定性 / 真实场景风险
  描述：WebSocket 字幕推送仍需真实长时间会议测试。
  影响：当前已通过基础握手和 broadcast 测试，但 30 分钟以上会议中的连接稳定性、内存占用和异常断开场景仍未充分验证。
  修复建议：使用真实或模拟长会议持续推送字幕，记录连接时长、断开次数、内存变化和字幕延迟。
  状态：open

- [DEBT-018] 类型：兼容性 / 断线恢复风险
  描述：WebSocket 断线重连策略仍较基础。
  影响：当前前端支持一次重连和 Polling Fallback，但弱网、电脑休眠、后端重启等场景下的恢复体验仍需验证。
  修复建议：后续增加指数退避、多次重连、用户可见恢复提示和重连成功后的状态同步。
  状态：open

- [DEBT-019] 类型：性能 / 多客户端风险
  描述：多个投屏页同时连接同一会议时仍需压力测试。
  影响：当前连接管理器支持按 meeting_id 广播，但多屏、多浏览器和长会议并发连接下的资源占用未量化。
  修复建议：构造多个 WebSocket 客户端并发接收字幕，记录广播耗时、失败连接清理和后端资源占用。
  状态：open

- [DEBT-020] 类型：性能 / 字幕延迟风险
  描述：WebSocket 推送链路的端到端字幕延迟仍缺少真实数据。
  影响：虽然投屏页不再只依赖 2 秒轮询，但从麦克风 chunk、Whisper、Gemini、数据库写入到 WebSocket 推送的总延迟仍未持续监控。
  修复建议：为每个 chunk 增加端到端时间戳，统计中文和英文字幕的 p50 / p95 / p99 延迟。
  状态：open

已解决债务：

- [DEBT-007] 投屏页不再单纯依赖 2 秒轮询，Alpha 1.2 已支持 WebSocket 优先推送并保留 Polling Fallback。

当前债务总数：16

### 2026-06-08-TASK-012

时间标签：2026-06-08-TASK-012

开发版本号：TransForum AI Alpha 1.1.2

新增债务：

- [DEBT-015] 类型：性能 / 真实场景风险
  描述：Gemini 翻译延迟仍需真实会议长时间测试。
  影响：单句翻译可返回 `latency_ms`，但长会议、连续 chunk 和弱网络下的延迟曲线仍未验证。
  修复建议：使用 30 分钟以上真实或模拟会议语料记录 p50 / p95 / p99 延迟。
  状态：open

- [DEBT-016] 类型：翻译质量风险
  描述：Gemini 字幕术语一致性仍需嘉宾专属词库支持。
  影响：专有名词、机构名、人名和行业术语在长会议中可能翻译不一致。
  修复建议：后续增加会议级术语表、嘉宾词库或 prompt 注入机制。
  状态：open

已解决债务：

- Gemini 真实文本翻译已接入。
- Gemini 基础 fallback 已接入。

当前债务总数：13

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
- [DEBT-007] 关闭于 2026-06-09-TASK-013：投屏页已支持 WebSocket 优先推送实时字幕，并保留 2 秒 Polling Fallback。
