# TransForum AI Development Plan

当前版本：TransForum AI Alpha 1.0

当前里程碑：First Real Meeting Demo

当前项目根目录：

```text
D:\transforum-ai
```

## Development Version Rule

- Alpha 0.1：项目骨架完成
- Alpha 0.1.1：项目迁移到 `D:\transforum-ai` 并建立任务标签与版本规则
- Alpha 0.2：会议创建与基础控制台可用
- Alpha 0.3：会议音频采集、上传和保存链路可用
- Alpha 0.4：录音文件 Whisper 识别入口可用
- Alpha 0.4.1：Whisper 本地模型优先管理可用
- Alpha 0.4.2：Whisper tiny 本地模型 Ready 验证完成
- Alpha 0.5：本地 Whisper 中文逐字稿可用
- Alpha 0.5.1：办公电脑 Whisper tiny 本地模型安装与中文逐字稿 UAT 通过
- Alpha 0.6：实时中文字幕基础能力可用
- Alpha 0.7：中文字幕投屏模式可用
- Alpha 0.8：中英双语字幕可用
- Alpha 0.9：会议存档与 Rule Based 会议纪要可用
- Alpha 1.0：First Real Meeting Demo 可演示

## Alpha 1.0 演示闭环

目标：把已有功能串成完整演示流程，而不是新增大功能。

演示流程：

1. Create Meeting
2. Start Realtime Caption
3. Open Screen Mode
4. End Meeting & Generate Minutes
5. View Meeting Minutes

## 下一阶段建议

- 接入真实 Gemini 翻译。
- 将投屏刷新从轮询升级到 WebSocket。
- 增加会议历史管理页面。
- 增加 DOCX 导出。
