# Lemmatization API (Minimal)

A minimal FastAPI service for English lemmatization using spaCy (`en_core_web_md`).

## Features

- Accepts one input string (`word`)
- Accepts the target word and its sentence (`word`, `sentence`)
- Cleans extra spaces and whitespace
- Ensures the cleaned result is exactly one word
- Uses the sentence context to select the target token and returns its lemma

## Install

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

If model installation is required manually:

```bash
.venv/bin/python -m spacy download en_core_web_md
```

## Run

```bash
.venv/bin/uvicorn backend.main:app --reload
```

## Test

```bash
.venv/bin/python -m pytest -q
```

The test suite includes all 17 spaCy universal POS tags and marks which samples
are lemmatized (changed) vs unchanged.

## API

The lemmatization endpoint follows a Google AIPs-style versioned custom method
pattern: `POST /v1/words:lemmatize`.

### Health

- `GET /health`

### Lemmatize

- `POST /v1/words:lemmatize`
- Request body:

```json
{
  "word": "  running   ",
  "sentence": "They are running in the park."
}
```

- Example response:

```json
{
  "original_word": "  running   ",
  "original_sentence": "They are running in the park.",
  "cleaned_word": "running",
  "cleaned_sentence": "They are running in the park.",
  "matched_token": "running",
  "lemma": "run"
}
```

- Validation behavior:
  - empty input -> 400
  - empty sentence -> 400
  - more than one word after cleaning -> 400
  - target word not found in sentence -> 400
