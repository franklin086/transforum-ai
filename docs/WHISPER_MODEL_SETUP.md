# Whisper Model Setup

## Whisper 模型目录

```text
D:\transforum-ai\models\whisper
```

当前 tiny 模型安装目录：

```text
D:\transforum-ai\models\whisper\tiny
```

## 支持模型

- tiny
- base
- small
- medium

## 推荐选择

开发阶段：

```text
tiny
```

生产阶段：

```text
base
```

## 当前安装结果

时间标签：2026-06-07-TASK-005A-UAT

开发版本号：TransForum AI Alpha 0.4.2

下载来源：

```text
Systran/faster-whisper-tiny
```

保存路径：

```text
D:\transforum-ai\models\whisper\tiny
```

关键文件：

- config.json
- model.bin
- tokenizer.json
- vocabulary.txt
- README.md
- .gitattributes

## 安装方式

优先使用可控脚本安装：

```bash
cd /d D:\transforum-ai
python scripts\download_whisper_tiny.py
```

脚本会将模型下载到：

```text
D:\transforum-ai\models\whisper\tiny
```

业务接口不会在运行时自动下载模型。

## 手动安装方式

如果网络下载失败，可以手动下载 faster-whisper 兼容模型，并复制到：

```text
D:\transforum-ai\models\whisper\tiny
```

目录内至少应包含：

- config.json
- model.bin
- tokenizer.json
- vocabulary.txt

复制完成后重启后端，再访问模型状态接口验证。

## 后端配置

后端配置文件：

```text
D:\transforum-ai\backend\.env
```

默认配置：

```text
TRANSFORUM_WHISPER_MODEL=tiny
TRANSFORUM_WHISPER_MODEL_PATH=D:/transforum-ai/models/whisper
```

系统会优先检查：

```text
D:\transforum-ai\models\whisper\tiny
```

如果模型不存在，系统返回 `MODEL_NOT_FOUND`，不自动访问 Hugging Face，也不联网下载模型。

## 验证接口

启动后端后访问：

```text
http://localhost:8000/api/transcription/model-status
```

当前验收结果：

```json
{
  "installed": true,
  "model": "tiny",
  "path": "D:/transforum-ai/models/whisper",
  "model_path": "D:/transforum-ai/models/whisper/tiny",
  "message": "Ready"
}
```

显示 `Ready` 后，即可进入下一步 TASK 005B：本地 Whisper 中文识别验证。
