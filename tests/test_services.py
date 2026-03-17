import pytest

from services.cleaner import clean_word
from services import restorer


def test_clean_word_trims_and_takes_first_token() -> None:
	assert clean_word("   running   quickly   ") == "running"


def test_clean_word_strips_edge_punctuation() -> None:
	assert clean_word("***running!!!") == "running"


def test_clean_word_raises_on_blank_input() -> None:
	with pytest.raises(ValueError, match="non-empty string"):
		clean_word("   ")


def test_restore_lemma_returns_lemma(monkeypatch: pytest.MonkeyPatch) -> None:
	class _Token:
		text = "running"
		pos_ = "VERB"
		tag_ = "VBG"
		lemma_ = "run"

	class _Doc:
		def __len__(self) -> int:
			return 1

		def __getitem__(self, index: int) -> _Token:
			assert index == 0
			return _Token()

	def _fake_nlp(_: str) -> _Doc:
		return _Doc()

	monkeypatch.setattr(restorer, "NLP", _fake_nlp)
	assert restorer.restore_lemma("running") == "run"


def test_restore_lemma_uses_fallback_for_irregular_plural(monkeypatch: pytest.MonkeyPatch) -> None:
	class _Token:
		text = "phenomena"
		lemma_ = "phenomena"
		pos_ = "PROPN"
		tag_ = "NNP"

	class _Doc:
		def __len__(self) -> int:
			return 1

		def __getitem__(self, index: int) -> _Token:
			assert index == 0
			return _Token()

	def _fake_nlp(_: str) -> _Doc:
		return _Doc()

	monkeypatch.setattr(restorer, "NLP", _fake_nlp)
	assert restorer.restore_lemma("phenomena") == "phenomenon"


def test_restore_lemma_uses_fallback_when_spacy_lemma_is_empty(monkeypatch: pytest.MonkeyPatch) -> None:
	class _Token:
		text = "running"
		lemma_ = ""
		pos_ = "NOUN"
		tag_ = "NN"

	class _Doc:
		def __len__(self) -> int:
			return 1

		def __getitem__(self, index: int) -> _Token:
			assert index == 0
			return _Token()

	def _fake_nlp(_: str) -> _Doc:
		return _Doc()

	monkeypatch.setattr(restorer, "NLP", _fake_nlp)
	assert restorer.restore_lemma("running") == "run"


def test_restore_lemma_uses_fallback_for_worst(monkeypatch: pytest.MonkeyPatch) -> None:
	class _Token:
		text = "worst"
		lemma_ = "worst"
		pos_ = "ADV"
		tag_ = "RBS"

	class _Doc:
		def __len__(self) -> int:
			return 1

		def __getitem__(self, index: int) -> _Token:
			assert index == 0
			return _Token()

	def _fake_nlp(_: str) -> _Doc:
		return _Doc()

	monkeypatch.setattr(restorer, "NLP", _fake_nlp)
	assert restorer.restore_lemma("worst") == "bad"


def test_restore_lemma_keeps_regular_singular_noun(monkeypatch: pytest.MonkeyPatch) -> None:
	class _Token:
		text = "bore"
		lemma_ = "bore"
		pos_ = "NOUN"
		tag_ = "NN"

	class _Doc:
		def __len__(self) -> int:
			return 1

		def __getitem__(self, index: int) -> _Token:
			assert index == 0
			return _Token()

	def _fake_nlp(_: str) -> _Doc:
		return _Doc()

	monkeypatch.setattr(restorer, "NLP", _fake_nlp)
	assert restorer.restore_lemma("bore") == "bore"


def test_restore_lemma_raises_when_doc_is_empty(monkeypatch: pytest.MonkeyPatch) -> None:
	class _Doc:
		def __len__(self) -> int:
			return 0

	def _fake_nlp(_: str) -> _Doc:
		return _Doc()

	monkeypatch.setattr(restorer, "NLP", _fake_nlp)
	with pytest.raises(ValueError, match="unable to process"):
		restorer.restore_lemma("running")