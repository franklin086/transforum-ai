# TransForum AI Development Plan

当前版本：TransForum AI Alpha 0.9

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
- Alpha 1.0：First Real Meeting 完整闭环可演示

## Sprint 6：会议存档与会议纪要

目标：结束会议后自动归档会议内容，生成 Rule Based 会议纪要，并提供纪要查看页面。

开发内容：

- 新增 `meeting_archive` 表。
- 新增纪要字段：`minutes_summary`、`minutes_key_points`、`minutes_action_items`、`minutes_next_steps`。
- 新增 `backend/services/minutes_service.py`。
- 新增 `POST /api/minutes/generate`。
- 新增 `/meeting/minutes?meeting_id=xxx`。
- Meeting Console 新增 End Meeting。
- End Meeting 执行归档、生成纪要、跳转纪要页。
- 按 Rule 2 更新 `docs/TECHNICAL_DEBT.md`。

验收标准：

- `/api/health` 返回 Alpha 0.9。
- 结束会议成功。
- `meeting_archive` 写入会议内容。
- 会议纪要字段写入 `meetings` 表。
- `/meeting/minutes?meeting_id=xxx` 可查看历史纪要。

## 下一阶段建议

```text
2026-06-08-TASK-009
TransForum AI Alpha 1.0
目标：First Real Meeting 演示闭环打磨
```
