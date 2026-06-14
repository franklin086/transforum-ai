# TransForum AI Development Plan

当前版本：TransForum AI Alpha 1.2.1

当前里程碑：Field Test Preparation

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
- Alpha 1.0.1：演示稳定性检查与启动流程优化
- Alpha 1.1：Gemini 真实文本翻译接入
- Alpha 1.1.1：Gemini API Key 本机配置与真实翻译验收通过
- Alpha 1.1.2：Gemini 翻译质量、稳定性与延迟记录优化
- Alpha 1.2：WebSocket 实时字幕推送与 Polling Fallback
- Alpha 1.2.1：现场测试准备阶段

## Alpha 1.2.1 范围

目标：为真实会议现场测试准备清单、记录模板、问题反馈模板和测试后复盘模板。

本阶段只做：

- 现场测试会前检查清单
- 现场测试报告模板
- 问题反馈模板
- 测试后复盘模板
- README 现场测试说明
- 文档和技术债务更新

本阶段不做：

- Gemini Live API
- AI 语音播报
- 后端、前端、数据库、API 或 WebSocket 代码修改
- DOCX 导出
- 手机扫码
- 用户系统

## 下一阶段建议

- Alpha 1.2.2：现场测试问题修复。
- WebSocket 长会议稳定性和断线重连专项。
- Gemini 术语一致性和嘉宾词库专项。
- 增加 DOCX 导出。
