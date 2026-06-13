# TransForum AI Alpha 1.1 Demo Guide

## 演示目标

一个人、一台电脑、一个麦克风、一台投影仪，5 分钟内启动一场中英双语 AI 同传会议，并生成会议纪要。

Alpha 1.1 在 Alpha 1.0 First Real Meeting Demo 的基础上接入 Gemini 文本翻译，并继续保留演示启动检查流程。

## 演示前环境检查

在项目根目录执行：

```powershell
cd D:\transforum-ai
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
```

检查项包括：

- 当前目录是否为 `D:\transforum-ai`
- `backend`、`frontend` 目录是否存在
- `models\whisper\tiny` 是否存在
- `data\audio`、`data\chunks`、`data\transcripts` 是否存在
- Python、Node、npm 是否可用

## 启动后端

```powershell
cd D:\transforum-ai
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

后端地址：

```text
http://localhost:8000
```

健康检查应返回：

```json
{
  "status": "ok",
  "project": "TransForum AI",
  "version": "Alpha 1.1"
}
```

## 启动前端

```powershell
cd D:\transforum-ai
powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
```

默认访问：

```text
http://localhost:3000
```

如果开发服务不稳定，可使用生产模式：

```powershell
cd D:\transforum-ai\frontend
npm run build
npm run start -- -p 3001
```

备用访问：

```text
http://localhost:3001
```

## 演示步骤

1. 打开首页
2. 点击 Start First Real Meeting Demo
3. 创建会议
4. 点击 Start Realtime Caption
5. 打开 Screen Mode
6. 朗读测试语句
7. 检查中英双语字幕
8. 结束会议
9. 查看会议纪要

## 推荐测试语句

大家好，欢迎参加 TransForum AI 测试会议。今天我们正在演示中英双语字幕投屏和会议纪要功能。

## 演示检查清单

详细清单见：

```text
scripts\demo_checklist.md
```

## 当前限制

- 英文翻译仍为 Mock 或基础翻译，后续接 Gemini。
- 真实麦克风测试需人工确认。
- Whisper tiny 模型适合演示，不适合正式高精度会议。
- 投屏刷新仍为轮询，后续可升级 WebSocket。
- 新增启动脚本仍需在不同 Windows 环境反复测试。
- Gemini API Key 需要在演示电脑本地配置；未配置时会显示 Mock Fallback。
