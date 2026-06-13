# TransForum AI Alpha 1.0 Demo Guide

## 演示目标

一个人、一台电脑、一个麦克风、一台投影仪，5 分钟开启一场中英双语 AI 同传会议，并生成会议纪要。

## 演示步骤

1. 启动后端
2. 启动前端
3. 创建会议
4. 开始实时字幕
5. 打开投屏页
6. 讲话测试
7. 结束会议
8. 查看会议纪要

## 推荐测试语句

大家好，欢迎参加 TransForum AI 测试会议。今天我们正在演示中英双语字幕投屏和会议纪要功能。

## 当前限制

- 英文翻译仍为 Mock 或基础翻译，后续接 Gemini。
- 真实麦克风测试需人工确认。
- Whisper tiny 模型适合演示，不适合正式高精度会议。
- 投屏刷新仍为轮询，后续可升级 WebSocket。

## 启动命令

后端：

```bash
cd /d D:\transforum-ai\backend
python -m uvicorn main:app --reload
```

前端：

```bash
cd /d D:\transforum-ai\frontend
npm run build
npm run start -- -p 3001
```
