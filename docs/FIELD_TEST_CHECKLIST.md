# Alpha 1.2.2 Field Test Focus

本次测试不以投屏效果为重点。

本次重点测试：

## 第一优先级：实时翻译准确率与响应速度

测试问题：

- Gemini 英文翻译是否准确
- 翻译是否自然
- 是否适合会议字幕
- 是否出现漏译
- 是否出现解释性废话
- 平均延迟是否可接受
- 延迟是否影响会议理解

记录指标：

- 翻译准确率主观评分：1-5
- 翻译自然度评分：1-5
- 平均响应速度评分：1-5
- 可接受延迟阈值：建议 5 秒以内
- 不可接受延迟：超过 8 秒

## 第二优先级：完整会议流程顺畅度

测试流程：

1. 启动系统
2. 创建会议
3. 开始实时字幕
4. 进行中文发言测试
5. 查看中英字幕
6. 停止会议
7. 生成会议记录
8. 查看会议纪要
9. 查看会议数据是否保存

记录指标：

- 创建会议是否顺畅
- 开始实时字幕是否顺畅
- Gemini 翻译是否正常
- 结束会议是否顺畅
- 会议纪要是否生成
- 是否出现卡顿、报错、页面无响应

## 第三优先级：笔记本内置麦克风识别率

测试条件：

仅使用笔记本内置麦克风。

不接外置麦克风。

观察：

- Whisper 是否能正确识别普通会议讲话
- 稍远距离讲话是否还能识别
- 环境噪音是否明显影响识别
- 连续讲话是否丢字
- 是否出现错别字
- 是否出现断句问题

记录指标：

- 近距离识别准确率评分：1-5
- 会议距离识别准确率评分：1-5
- 噪音环境表现评分：1-5
- 是否建议正式测试使用外接麦克风

## 暂不重点测试

投屏效果暂不作为本次测试重点。

只做基础打开检查：

- `/screen` 页面能打开即可
- 不评价大屏显示质量
- 不评价投影仪适配
- 不评价远距离可读性

## 会前基础检查

```powershell
cd D:\transforum-ai
git pull
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
```

启动后端：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

启动前端：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
```

Whisper readiness：

```text
GET http://localhost:8000/api/transcription/model-status
```

期望：

```text
installed=true
message=Ready
```
