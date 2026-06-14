# TransForum AI Alpha 1.2.1 Field Test Checklist

## 一、测试定位

本次测试为 Alpha 现场验证，不是正式商用交付。

## 二、会前30分钟检查

### 1. 设备检查

- 笔记本电源
- 麦克风
- 投影仪
- HDMI / 转接头
- 网络
- 浏览器
- 音量
- 备用电源

### 2. 项目检查

执行：

```powershell
cd D:\transforum-ai
git pull
```

执行环境检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
```

### 3. 后端启动

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

检查：

```text
http://localhost:8000/api/health
```

应返回：

```text
Alpha 1.2 或 Alpha 1.2.1
```

### 4. 前端启动

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
```

打开：

```text
http://localhost:3001
```

### 5. Whisper检查

访问：

```text
http://localhost:8000/api/transcription/model-status
```

应返回：

```text
installed=true
message=Ready
```

### 6. Gemini检查

测试一句中文：

```text
大家好，欢迎参加 TransForum AI 测试会议。
```

应显示：

```text
Translation: Gemini
```

### 7. WebSocket检查

投屏页应显示：

```text
Realtime: WebSocket
```

如果失败，应显示：

```text
Polling Fallback
```

## 三、测试流程

1. 创建会议
2. Start Realtime Caption
3. 打开 Screen Mode
4. 朗读测试句
5. 观察中文字幕
6. 观察英文字幕
7. 观察投屏延迟
8. 结束会议
9. 生成会议纪要
10. 保存测试结果

## 四、推荐测试语句

大家好，欢迎参加今天的会议。现在我们正在测试 TransForum AI 的实时中英双语字幕功能。

今天的会议主要讨论人工智能在国际传播和跨语言会议中的应用。

接下来我们将进入讨论环节，请各位嘉宾依次发言。

## 五、现场备用方案

如果 Gemini 失败：

继续测试中文字幕。

如果 WebSocket 失败：

使用 Polling Fallback。

如果麦克风失败：

更换麦克风或改用电脑内置麦克风。

如果投影失败：

使用本机浏览器录屏测试。
