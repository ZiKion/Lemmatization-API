# Lemmatization API

基于 FastAPI + spaCy 的词形还原服务，采用 Google AIP 风格接口与错误响应。

## 1. 安装依赖

```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 2. 启动服务

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 3. 接口规范

- URL: `POST /api/v1/lemmas`
- Request:

```json
{
  "word": "   running   "
}
```

- Success Response:

```json
{
  "lemma": "run"
}
```

- URL: `POST /api/v1/lemmas:resolve`
- 用途: 在句子语境中定位目标词并还原。
- Request:

```json
{
  "sentence": "This is a better choice.",
  "target_word": "better"
}
```

- Success Response:

```json
{
  "lemma": "good",
  "token": "better",
  "start": 10,
  "end": 16
}
```

- Error Response (Google AIP style):

```json
{
  "error": {
    "code": 400,
    "message": "Invalid argument: String should have at least 1 character",
    "status": "INVALID_ARGUMENT"
  }
}
```

## 4. 分层结构

```text
project/
  main.py                    # 应用入口 + 全局异常映射
  core/config.py             # spaCy 模型预加载（仅一次）
  api/routes/lemmatization.py# FastAPI 接入层
  schemas/                   # Pydantic 请求/响应/错误模型
  services/cleaner.py        # 输入清洗器
  services/restorer.py       # 词形还原器
```

## 5. 健康检查

- URL: `GET /healthz`
