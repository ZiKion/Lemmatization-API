# Lemmatization API / 词形还原接口

English lemmatization service built with FastAPI and spaCy (`en_core_web_md`).
This project is designed for internal use: other services send a word and sentence,
and can optionally send a match index to disambiguate multiple matches.

基于 FastAPI 和 spaCy（`en_core_web_md`）实现的英文词形还原服务。
本项目面向内部使用：由其他接口传入目标词和句子，并可选传入匹配索引（用于多命中消歧），返回词形还原结果。

## Features / 功能

- Sentence-aware lemmatization / 基于句子语境的词形还原
- Word cleaning before processing / 先清洗输入词
- Matched-word occurrence indexing / 采用命中词列表的 occurrence 索引
- Google AIPs-style error responses / Google AIPs 风格错误返回
- Structured JSON request logs / 结构化 JSON 请求日志
- Request tracing with `X-Request-Id` / 支持 `X-Request-Id` 请求追踪
- Minimal spaCy pipeline for better efficiency / 精简 spaCy 管线以提升效率

## Install / 安装

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

If the model needs to be installed manually / 如需手动安装模型：

```bash
.venv/bin/python -m spacy download en_core_web_md
```

## Run / 启动

```bash
.venv/bin/uvicorn backend.main:app --reload
```

Open the API docs at / 打开接口文档：

- http://127.0.0.1:8000/docs

## Test / 测试

```bash
.venv/bin/python -m pytest -q
```

## Project Structure / 项目结构

- [backend/main.py](backend/main.py): app assembly / 应用装配入口
- [backend/api/routes/word_routes.py](backend/api/routes/word_routes.py): API routes / 路由层
- [backend/services/word_lemmatizer.py](backend/services/word_lemmatizer.py): core lemmatization logic / 核心词形还原逻辑
- [backend/core/nlp.py](backend/core/nlp.py): spaCy model loading and pipeline trimming / 模型加载与管线裁剪
- [backend/core/errors.py](backend/core/errors.py): Google AIPs error mapping / AIPs 错误映射
- [backend/core/logging_trace.py](backend/core/logging_trace.py): structured logging and request tracing / 日志与请求追踪
- [backend/schemas/word_models.py](backend/schemas/word_models.py): request/response models / 请求与响应模型

## API / 接口

### Health / 健康检查

- `GET /health`

Returns / 返回：

```json
{
  "status": "ok"
}
```

### Lemmatize / 词形还原

Google AIPs-style endpoint / Google AIPs 风格接口：

- `POST /v1/words:lemmatize`

Indexing rule / 索引规则：

The API first filters sentence tokens equal to `word` (case-insensitive).
If `word_occurrence_index` is provided, it is used as a 0-based index in the matched list.
If omitted, the API defaults to 0 only when there is exactly one match.

API 会先筛选出句子中与 `word` 相等（忽略大小写）的所有 token。
如果传入 `word_occurrence_index`，则按该 0 基索引定位命中项；
如果未传，则仅在“单命中”时默认使用 0。

Decision table / 决策表：

| Match count / 命中数量 | Index provided? / 是否传索引 | Behavior / 行为 |
| --- | --- | --- |
| 0 | Yes/No | 400 (`Target word must appear in the supplied sentence`) |
| 1 | No | Auto use `0` / 自动使用 `0` |
| 1 | Yes | Use provided index / 使用传入索引 |
| >1 | No | 400 (`Multiple matched tokens found; please provide word_occurrence_index explicitly`) |
| >1 | Yes | Use provided index / 使用传入索引 |

Example A (single match, index omitted) / 示例 A（单命中，省略索引）：

```json
{
  "word": "fucking",
  "sentence": "Change your fucking car."
}
```

Response example / 响应示例：

```json
{
  "original_word": "running",
  "original_sentence": "They are running in the park.",
  "cleaned_word": "running",
  "cleaned_sentence": "They are running in the park.",
  "matched_token": "running",
  "matched_token_index": 2,
  "matched_word_count": 1,
  "matched_word_occurrence_index": 0,
  "lemma": "run"
}
```

Example B (multiple matches, index required) / 示例 B（多命中，必须传索引）：

```json
{
  "word": "saw",
  "sentence": "I saw a saw on the table.",
  "word_occurrence_index": 1
}
```

Example C (multiple matches, index omitted -> error) / 示例 C（多命中省略索引 -> 报错）：

```json
{
  "word": "saw",
  "sentence": "I saw a saw on the table."
}
```

Optional request header / 可选请求头：

```text
X-Request-Id: req-12345
```

The same request id is returned in the response header / 响应头会返回相同的请求 ID：

```text
X-Request-Id: <same incoming id or generated uuid>
```

## Error Model / 错误模型

All errors follow a Google AIPs-style envelope / 所有错误都使用 Google AIPs 风格外壳：

```json
{
  "error": {
    "code": 400,
    "message": "Request validation failed",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "body.sentence",
            "description": "Field required"
          }
        ]
      }
    ]
  }
}
```

Common validation errors / 常见校验错误：

- Empty word -> 400 / 单词为空 -> 400
- Empty sentence -> 400 / 句子为空 -> 400
- More than one word after cleaning -> 400 / 清洗后仍有多个单词 -> 400
- Target word not found in sentence -> 400 / 目标词不在句子中 -> 400
- `word_occurrence_index` out of range -> 400 / `word_occurrence_index` 超出命中范围 -> 400
- Multiple matched tokens but index omitted -> 400 / 多命中且未传索引 -> 400

## Notes / 说明

- The service keeps only spaCy components required for contextual lemmatization.
  / 服务仅保留词形还原所需的 spaCy 组件。
