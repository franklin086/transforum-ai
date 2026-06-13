# Gemini API Setup

## 1. 打开 Google AI Studio

进入 Google AI Studio。

## 2. 创建 Gemini API Key

在 API Keys 页面创建 key。

## 3. 配置环境变量

Windows PowerShell 临时配置：

```powershell
$env:GEMINI_API_KEY="你的key"
```

推荐写入：

```text
D:\transforum-ai\backend\.env
```

内容：

```text
GEMINI_API_KEY=你的key
GEMINI_TRANSLATION_MODEL=gemini-3.5-flash
```

不要提交真实 API Key。仓库只提交：

```text
backend\.env.example
```

## 4. 安装依赖

```powershell
cd D:\transforum-ai\backend
pip install -r requirements.txt
```

## 5. 启动后端

```powershell
cd D:\transforum-ai\backend
python -m uvicorn main:app --reload
```

## 6. 验证

进入会议控制台，开始实时字幕。

如果 Translation 显示 Gemini，并且 Latency 显示毫秒数，说明 Gemini 文本翻译接入成功。

如果显示 Mock Fallback，说明没有读取到 key，或 Gemini API 调用失败后系统自动回退到 Mock。

## 7. Alpha 1.1.2 翻译稳定性

Alpha 1.1.2 已增加：

- 专业会议同传字幕风格 prompt
- 翻译结果清洗
- `latency_ms` 返回
- 后端日志 `Gemini translation latency: xxx ms`
- 错误码：`GEMINI_API_KEY_MISSING`、`GEMINI_RATE_LIMIT`、`GEMINI_NETWORK_ERROR`、`GEMINI_API_ERROR`
- 速率限制时最多重试 1 次，间隔 0.5 秒
- Gemini 失败时自动 Mock Fallback

## 8. 关于 Gemini Live API

Gemini 3.5 Live Translate 模型：

```text
gemini-3.5-live-translate-preview
```

该模型用于语音到语音实时翻译。

TransForum AI Alpha 1.1.2 暂不接入 Live API。后续可作为 AI 有声同传专项任务接入。
