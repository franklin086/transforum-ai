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

或单独安装：

```powershell
pip install google-genai
```

## 5. 启动后端

```powershell
cd D:\transforum-ai\backend
python -m uvicorn main:app --reload
```

## 6. 验证

进入会议控制台，开始实时字幕。

如果 Translation Provider 显示 Gemini，说明 Gemini 文本翻译接入成功。

如果显示 Mock Fallback，说明没有读取到 key，或 Gemini API 调用失败后系统自动回退到 Mock。

## 7. 关于 Gemini Live API

Gemini 3.5 Live Translate 模型：

```text
gemini-3.5-live-translate-preview
```

该模型用于语音到语音实时翻译。

TransForum AI Alpha 1.1 暂不接入 Live API。后续 Alpha 1.2 或 Alpha 1.3 可作为 AI 有声同传专项任务接入。
