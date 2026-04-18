from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field
import spacy

app = FastAPI(title="Lemmatization API", version="0.1.0")
router = APIRouter(prefix="/v1")


try:
    nlp = spacy.load("en_core_web_md")
except OSError as exc:
    raise RuntimeError(
        "spaCy model 'en_core_web_md' is missing. Install it with: "
        "python -m spacy download en_core_web_md"
    ) from exc


class LemmatizeWordRequest(BaseModel):
    word: str = Field(..., description="Input text that should contain exactly one word")
    sentence: str = Field(..., description="Sentence containing the target word in context")


class LemmatizeWordResponse(BaseModel):
    original_word: str
    original_sentence: str
    cleaned_word: str
    cleaned_sentence: str
    matched_token: str
    lemma: str


def clean_to_single_word(text: str) -> str:
    cleaned = " ".join(text.split()).strip()

    if not cleaned:
        raise HTTPException(status_code=400, detail="Input cannot be empty")

    if " " in cleaned:
        raise HTTPException(
            status_code=400,
            detail="Input must contain exactly one word after cleaning",
        )

    return cleaned


def clean_sentence(text: str) -> str:
    cleaned = " ".join(text.split()).strip()

    if not cleaned:
        raise HTTPException(status_code=400, detail="Sentence cannot be empty")

    return cleaned


def find_target_token(doc: spacy.tokens.Doc, word: str) -> spacy.tokens.Token:
    lowered_word = word.lower()

    for token in doc:
        if token.text.lower() == lowered_word:
            return token

    raise HTTPException(
        status_code=400,
        detail="Target word must appear in the supplied sentence",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/words:lemmatize", response_model=LemmatizeWordResponse)
def lemmatize_word(payload: LemmatizeWordRequest) -> LemmatizeWordResponse:
    cleaned_word = clean_to_single_word(payload.word)
    cleaned_sentence = clean_sentence(payload.sentence)

    doc = nlp(cleaned_sentence)
    if len(doc) == 0:
        raise HTTPException(status_code=400, detail="Unable to process input sentence")

    target_token = find_target_token(doc, cleaned_word)

    return LemmatizeWordResponse(
        original_word=payload.word,
        original_sentence=payload.sentence,
        cleaned_word=cleaned_word,
        cleaned_sentence=cleaned_sentence,
        matched_token=target_token.text,
        lemma=target_token.lemma_,
    )


app.include_router(router)
