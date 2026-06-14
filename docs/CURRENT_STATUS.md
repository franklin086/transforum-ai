# Current Status

## 当前项目

项目名称：TransForum AI

当前开发版本号：TransForum AI Alpha 1.2

当前里程碑：WebSocket Subtitle Push

当前项目根目录：

```text
D:\transforum-ai
```

## 当前阶段

Alpha 1.2 将实时字幕投屏从 2 秒轮询升级为 WebSocket 优先推送，并保留 Polling Fallback。

本阶段不接入 Gemini Live API，不做语音到语音翻译、AI 语音播报、DOCX 导出或用户系统。

## 当前已完成能力

- Gemini API Key 本机配置成功。
- Gemini 真实文本翻译已通过。
- Gemini 提示词优化为专业会议同传字幕风格。
- 翻译结果清洗：去除 `Translation:`、`English:`、引号、Markdown 和多余换行。
- Gemini 调用返回 `latency_ms`。
- 后端日志输出 `Gemini translation latency: xxx ms`。
- Gemini 错误分类：`GEMINI_API_KEY_MISSING`、`GEMINI_RATE_LIMIT`、`GEMINI_NETWORK_ERROR`、`GEMINI_API_ERROR`。
- 速率限制时最多重试 1 次，间隔 0.5 秒。
- Gemini 失败时自动 Mock Fallback，中文字幕链路不受影响。
- `GET /api/realtime/bilingual/{meeting_id}` 返回 `provider` 和 `latency_ms`。
- Meeting Console 显示 `Translation` 和 `Latency`。
- Screen 投屏页显示 `Translation: Gemini · xxx ms`。
- 新增 `backend/tests/test_translation_service.py`。
- 新增后端 WebSocket 连接管理器。
- 新增 `/ws/realtime/{meeting_id}` WebSocket 字幕推送接口。
- 实时字幕 chunk 识别成功后广播 `subtitle_update` 消息。
- Meeting Console 显示 `WebSocket Status`。
- Screen 投屏页优先使用 WebSocket 刷新字幕。
- Screen 投屏页保留 2 秒 Polling Fallback。
- Screen 投屏页显示 `Realtime: WebSocket / Polling Fallback`。
- 新增 `backend/tests/test_realtime_websocket.py`。

## 当前限制

- Gemini 翻译延迟仍需真实会议长时间测试。
- Gemini 字幕术语一致性仍需嘉宾专属词库支持。
- Gemini Live API 暂未接入。
- WebSocket 长时间会议稳定性仍需真实环境测试。
- WebSocket 断线重连策略仍需真实会议验证。
- 多个投屏页同时连接时仍需压力测试。
- DOCX 导出仍未实现。
- 会议历史管理页面仍未实现。

## 当前最新任务记录

时间标签：2026-06-09-TASK-013

开发版本号：TransForum AI Alpha 1.2

任务名称：WebSocket 字幕推送

完成状态：后端 WebSocket、投屏页 WebSocket 优先刷新、Polling Fallback、前端构建和后端测试通过。

下一阶段建议：

- Alpha 1.3：WebSocket 长会议稳定性、重连策略或 DOCX 导出专项。
