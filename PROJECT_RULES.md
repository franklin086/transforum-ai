# TransForum AI Project Rules

## 项目名称

TransForum AI

## 当前项目根目录

```text
D:\transforum-ai
```

后续所有开发工作都必须在 `D:\transforum-ai` 目录下执行。

## Rule 0：先完成 First Real Meeting

TransForum AI 的第一阶段目标是完成 First Real Meeting，也就是“第一场真实会议”。

所有开发都必须围绕以下核心流程：

创建会议 → 接入麦克风 → 实时语音识别 → 实时中英翻译 → 双语字幕投屏 → 保存会议内容 → 生成中英文逐字稿和会议纪要 → 导出会议成果

任何功能开发前，必须先回答：

“这个功能是否能够帮助用户更快、更稳定地完成一场真实会议？”

如果答案是否定的，则该功能不进入当前开发周期。

## Rule 1：每个 TASK 必须自动更新项目状态文档

每完成一个 Codex TASK，必须自动更新以下三个文件：

- `docs/CURRENT_STATUS.md`
- `docs/TASK_HISTORY.md`
- `docs/CHANGELOG.md`

每次更新必须记录：

- 时间标签
- 开发版本号
- 修改文件
- 完成状态
- 验收结果
- 下一步任务

这条规则用于确保即使半年后继续开发，也可以通过项目文档迅速恢复上下文，而不需要反复依赖截图、聊天记录或复制大量内容。

## V1 只允许开发以下模块

- 会议创建
- 语音识别
- AI翻译
- 双语字幕
- 投屏模式
- 会议存档
- 会议纪要
- DOCX导出

## 当前禁止开发

- AI语音同传
- 声纹克隆
- APP客户端
- Zoom插件
- Teams插件
- 用户系统
- 支付系统
- SaaS订阅
- 多语言同步输出
- 手机扫码字幕
- 数据统计中心
- CRM功能
- 企业管理后台

## 最终验收标准

一个用户、一台电脑、一个麦克风、一台投影仪，5分钟内开启一场中英双语 AI 同传会议，并在结束后自动生成完整会议成果。

## Codex Task Label Rule

所有 Codex 工作指令必须包含时间标签，格式为：

```text
YYYY-MM-DD-TASK-编号
```

示例：

```text
2026-06-07-TASK-002
```

每次任务完成后，必须在回复中明确写出：

- 任务编号
- 时间标签
- 完成状态
- 主要修改文件
- 验收结果

## Development Version Rule

TransForum AI 使用阶段性开发版本号。

当前版本：

```text
TransForum AI Alpha 0.4.2
```

版本规则：

- Alpha 0.1：项目骨架完成
- Alpha 0.1.1：项目迁移到 D:\transforum-ai 并建立任务标签与版本规则
- Alpha 0.2：会议创建与基础控制台可用
- Alpha 0.3：麦克风接入与语音识别可用
- Alpha 0.4：中英实时翻译可用
- Alpha 0.5：双语字幕投屏可用
- Alpha 0.6：会议存档可用
- Alpha 0.7：会议纪要生成可用
- Alpha 1.0：First Real Meeting 完整闭环可演示

每完成一个里程碑阶段，必须更新 README.md 和 docs/DEVELOPMENT_PLAN.md 中的当前版本号。

