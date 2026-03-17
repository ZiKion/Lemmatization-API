from fastapi import APIRouter

from schemas.error import AIPErrorResponse
from schemas.request import LemmatizeInContextRequest, LemmatizeRequest
from schemas.response import LemmatizeInContextResponse, LemmatizeResponse
from services.cleaner import clean_word
from services.context_restorer import restore_lemma_in_context
from services.restorer import restore_lemma


router = APIRouter(tags=["lemmatization"])


@router.post(
	"/api/v1/lemmas",
	response_model=LemmatizeResponse,
	responses={
		400: {
			"model": AIPErrorResponse,
			"description": "Google AIP style INVALID_ARGUMENT error.",
		}
	},
)
def lemmatize(payload: LemmatizeRequest) -> LemmatizeResponse:
	cleaned_word = clean_word(payload.word)
	lemma = restore_lemma(cleaned_word)
	return LemmatizeResponse(lemma=lemma)


@router.post(
	"/api/v1/lemmas:resolve",
	response_model=LemmatizeInContextResponse,
	responses={
		400: {
			"model": AIPErrorResponse,
			"description": "Google AIP style INVALID_ARGUMENT error.",
		}
	},
)
def lemmatize_in_context(payload: LemmatizeInContextRequest) -> LemmatizeInContextResponse:
	return restore_lemma_in_context(payload.sentence, payload.target_word)