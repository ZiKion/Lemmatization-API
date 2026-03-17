from functools import lru_cache

import spacy
from spacy.language import Language


@lru_cache(maxsize=1)
def _load_nlp() -> Language:
	try:
		return spacy.load("en_core_web_sm")
	except OSError as exc:
		raise RuntimeError(
			"spaCy model 'en_core_web_sm' is not installed. "
			"Please run: python -m spacy download en_core_web_sm"
		) from exc


# Eager load on startup import. This guarantees a single shared model instance.
NLP = _load_nlp()