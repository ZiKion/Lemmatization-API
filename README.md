# Lemmatization API

一个面向英文词形还原的服务，提供两种使用方式：

1. 服务端 API：基于 FastAPI + spaCy，对外提供 HTTP 接口。
2. 本地 Worker：基于 wink-nlp，可在 Electron 或浏览器渲染进程本地执行。

项目错误响应遵循 Google AIP 风格，便于统一接入和自动化处理。

## 功能概览

- 单词词形还原：适合简单单词输入。
- 句子语境词形还原：传入一句话和目标词，根据上下文还原。
- 标准错误结构：非法参数统一返回 `INVALID_ARGUMENT`。
- 本地前端执行：支持 Web Worker 中运行 wink-nlp，避免阻塞渲染线程。

## 目录结构

```text
Lemmatization-API/
  main.py                         # 应用入口和全局异常处理
  api/routes/lemmatization.py     # 路由层
  core/config.py                  # spaCy 模型预加载
  schemas/                        # 请求/响应/错误模型
  services/                       # 清洗、还原、上下文还原逻辑
  renderer/                       # 本地渲染进程 Worker 示例
```

## 环境准备

### Python 依赖

```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 启动服务

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

启动后可访问：

- Swagger 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/healthz

## API 说明

### 1. 单词词形还原

接口：`POST /api/v1/lemmas`

请求：

```json
{
  "word": "running"
}
```

成功响应：

```json
{
  "lemma": "run"
}
```

### 2. 句子语境词形还原

接口：`POST /api/v1/lemmas:resolve`

用途：
调用方已经拿到“目标词所在句子”时，传入句子和目标词，由服务完成语境判断与词形还原。

请求：

```json
{
  "sentence": "This is a better choice.",
  "target_word": "better"
}
```

成功响应：

```json
{
  "lemma": "good",
  "token": "better",
  "start": 10,
  "end": 16
}
```

字段说明：

- `lemma`: 词形还原结果
- `token`: 实际命中的词
- `start`: 命中词在句子中的起始字符位置
- `end`: 命中词在句子中的结束字符位置

当前行为说明：

- `target_word` 匹配时不区分大小写。
- 如果同一句子中同一个词出现多次，当前默认命中第一个匹配项。
- 如果 `target_word` 不在 `sentence` 中，返回 400。

## 错误响应

所有参数错误统一返回 Google AIP 风格结构：

```json
{
  "error": {
    "code": 400,
    "message": "Invalid argument: 'target_word' was not found in 'sentence'.",
    "status": "INVALID_ARGUMENT"
  }
}
```

## 手动测试

### PowerShell 调用示例

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/lemmas:resolve" -ContentType "application/json" -Body '{"sentence":"This is a better choice.","target_word":"better"}' | ConvertTo-Json -Compress
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/lemmas:resolve" -ContentType "application/json" -Body '{"sentence":"She sings better than him.","target_word":"better"}' | ConvertTo-Json -Compress
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/lemmas:resolve" -ContentType "application/json" -Body '{"sentence":"This is the worst case.","target_word":"worst"}' | ConvertTo-Json -Compress
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/lemmas:resolve" -ContentType "application/json" -Body '{"sentence":"It was a bore to listen to him.","target_word":"bore"}' | ConvertTo-Json -Compress
```

## 本地渲染进程 Worker

如果不想走后端 API，也可以在前端本地执行词形还原。

适用场景：

- Electron 渲染进程
- 浏览器前端
- 已由外部模块定位好关键词并拿到句子
- 需要离线处理或降低网络延迟

### 安装前端依赖

```powershell
npm install wink-nlp wink-eng-lite-web-model
```

### 相关文件

- `renderer/winkLemmatizer.worker.js`: Worker 中运行 wink-nlp
- `renderer/winkLemmatizerClient.js`: 渲染进程调用封装
- `renderer/exampleUsage.js`: 最小示例

### 本地 Worker 输入

```json
{
  "sentence": "It was a bore to listen to him.",
  "target_word": "bore"
}
```

### 本地 Worker 输出

```json
{
  "lemma": "bore",
  "token": "bore"
}
```

说明：

- 本地 Worker 是 API 之外的另一条执行链路。
- 在线场景可以调用 FastAPI。
- 本地场景可以直接在渲染进程调用 Worker。

## 当前建议的接入方式

如果你的上游系统已经能完成这一步：

1. 人工或程序定位关键词
2. 自动提取关键词所在句子

那么最直接的接入方式就是调用：

```json
{
  "sentence": "关键词所在句子",
  "target_word": "关键词"
}
```

这就是当前项目最推荐的使用模式。
