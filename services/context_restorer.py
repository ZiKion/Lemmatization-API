from core.config import NLP
from schemas.response import LemmatizeInContextResponse
from services.restorer import restore_token_lemma


def restore_lemma_in_context(sentence: str, target_word: str) -> LemmatizeInContextResponse:
	doc = NLP(sentence)
	if len(doc) == 0:
		raise ValueError("Invalid argument: unable to process 'sentence'.")

	token = None
	for item in doc:
		if item.is_space:
			continue
		if item.text.lower() == target_word.lower():
			token = item
			break

	if token is None:
		raise ValueError("Invalid argument: 'target_word' was not found in 'sentence'.")

	start = token.idx
	end = token.idx + len(token.text)
	lemma = restore_token_lemma(token)

	return LemmatizeInContextResponse(
		lemma=lemma,
		token=token.text,
		start=start,
		end=end,
	)