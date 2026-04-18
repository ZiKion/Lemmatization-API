import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# spaCy universal POS tags (17): ADJ, ADP, ADV, AUX, CCONJ, DET, INTJ,
# NOUN, NUM, PART, PRON, PROPN, PUNCT, SCONJ, SYM, VERB, X
POS_CASES = [
    ("ADJ", "happier", "The happier child smiled.", "happy", True),
    ("ADV", "better", "She feels better today.", "well", True),
    ("ADP", "under", "We walked under the bridge.", "under", False),
    ("AUX", "was", "It was broken.", "be", True),
    ("CCONJ", "and", "Bread and butter.", "and", False),
    ("DET", "the", "The cat slept.", "the", False),
    ("INTJ", "wow", "Wow, that was great!", "wow", False),
    ("NOUN", "mice", "The mice escaped.", "mouse", True),
    ("NOUN", "saw", "The saw is sharp.", "saw", False),
    ("NUM", "three", "Three cats slept.", "three", False),
    ("PART", "to", "I want to go.", "to", False),
    ("PRON", "they", "They arrived early.", "they", False),
    ("PROPN", "London", "London is rainy.", "London", False),
    ("PUNCT", "!", "Wow!", "!", False),
    ("SCONJ", "because", "I stayed because it rained.", "because", False),
    ("SYM", "$", "$100 was expensive.", "$", False),
    ("VERB", "running", "They are running in the park.", "run", True),
    ("VERB", "saw", "I saw the movie.", "see", True),
]


@pytest.mark.parametrize("pos_tag,word,sentence,expected_lemma,should_change", POS_CASES)
def test_lemmatize_contextual_cases(
    pos_tag: str,
    word: str,
    sentence: str,
    expected_lemma: str,
    should_change: bool,
) -> None:
    response = client.post("/v1/words:lemmatize", json={"word": word, "sentence": sentence})
    assert response.status_code == 200

    data = response.json()
    assert data["cleaned_word"] == word
    assert data["cleaned_sentence"] == sentence
    assert data["matched_token"].lower() == word.lower()
    assert data["lemma"] == expected_lemma
    assert (data["lemma"] != data["cleaned_word"]) is should_change


def test_lemmatize_rejects_multiple_words_after_cleaning() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": " running  fast ", "sentence": "They are running fast."},
    )
    assert response.status_code == 400


def test_lemmatize_rejects_empty_input_after_cleaning() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "   \t\n  ", "sentence": "They are running fast."},
    )
    assert response.status_code == 400


def test_lemmatize_rejects_empty_sentence_after_cleaning() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "   \t\n  "},
    )
    assert response.status_code == 400


def test_lemmatize_rejects_missing_target_word_in_sentence() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "They are walking fast."},
    )
    assert response.status_code == 400
