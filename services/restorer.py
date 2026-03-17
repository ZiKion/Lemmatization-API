from core.config import NLP
from lemminflect import getLemma
from spacy.tokens import Token


def _candidate_upos(token_pos: str) -> list[str]:
	if token_pos == "ADJ":
		return ["ADJ", "ADV", "NOUN", "VERB"]
	if token_pos == "ADV":
		return ["ADV", "ADJ", "NOUN", "VERB"]
	if token_pos == "VERB":
		return ["VERB", "NOUN", "ADJ", "ADV"]
	if token_pos in {"NOUN", "PROPN"}:
		return ["NOUN", "ADJ", "ADV", "VERB"]
	return ["NOUN", "ADJ", "ADV", "VERB"]


def _fallback_lemma(word: str, token_pos: str) -> str | None:
	for upos in _candidate_upos(token_pos):
		lemmas = getLemma(word, upos=upos)
		for lemma in lemmas:
			if lemma and lemma != word:
				return lemma

	return None


def _resolve_lemma(word: str, token_pos: str, token_tag: str, token_lemma: str) -> str:
	fallback = _fallback_lemma(word, token_pos)

	# Comparative/superlative forms are frequently ambiguous; prefer fallback dictionaries.
	if token_tag in {"JJR", "JJS", "RBR", "RBS"} and fallback:
		return fallback

	# Keep spaCy result when it already found a different lemma.
	if token_lemma and token_lemma != word:
		return token_lemma

	# Recover irregular nouns mis-tagged as proper nouns (e.g. phenomena -> phenomenon).
	if token_pos == "PROPN" and fallback:
		return fallback

	# Plural nouns should singularize when lookup has a confident alternative.
	if token_tag in {"NNS", "NNPS"} and fallback:
		return fallback

	# If model lemma is empty, fallback can still provide a useful base form.
	if not token_lemma and fallback:
		return fallback

	return word


def restore_token_lemma(token: Token) -> str:
	return _resolve_lemma(token.text, token.pos_, token.tag_, token.lemma_)


def restore_lemma(cleaned_word: str) -> str:
	doc = NLP(cleaned_word)
	if len(doc) == 0:
		raise ValueError("Invalid argument: unable to process 'word'.")

	return restore_token_lemma(doc[0])