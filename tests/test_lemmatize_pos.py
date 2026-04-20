import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def assert_google_error(response, expected_status_code: int, expected_message: str | None = None) -> None:
    assert response.status_code == expected_status_code
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == expected_status_code
    assert data["error"]["status"] == "INVALID_ARGUMENT"
    assert isinstance(data["error"]["details"], list)

    if expected_message is not None:
        assert data["error"]["message"] == expected_message


def assert_response_has_request_id_header(response) -> str:
    request_id = response.headers.get("X-Request-Id")
    assert isinstance(request_id, str)
    assert request_id.strip() != ""
    return request_id


# spaCy universal POS tags (17): ADJ, ADP, ADV, AUX, CCONJ, DET, INTJ,
# NOUN, NUM, PART, PRON, PROPN, PUNCT, SCONJ, SYM, VERB, X
POS_CASES = [
    ("ADJ", "happier", "The happier child smiled.", 0, "happy", True),
    ("ADV", "better", "She feels better today.", 0, "well", True),
    ("ADP", "under", "We walked under the bridge.", 0, "under", False),
    ("AUX", "was", "It was broken.", 0, "be", True),
    ("CCONJ", "and", "Bread and butter.", 0, "and", False),
    ("DET", "the", "The cat slept.", 0, "the", False),
    ("INTJ", "wow", "Wow, that was great!", 0, "wow", False),
    ("NOUN", "mice", "The mice escaped.", 0, "mouse", True),
    ("NOUN", "saw", "The saw is sharp.", 0, "saw", False),
    ("NUM", "three", "Three cats slept.", 0, "three", False),
    ("PART", "to", "I want to go.", 0, "to", False),
    ("PRON", "they", "They arrived early.", 0, "they", False),
    ("PROPN", "London", "London is rainy.", 0, "London", False),
    ("PUNCT", "!", "Wow!", 0, "!", False),
    ("SCONJ", "because", "I stayed because it rained.", 0, "because", False),
    ("SYM", "$", "$100 was expensive.", 0, "$", False),
    ("VERB", "running", "They are running in the park.", 0, "run", True),
    ("VERB", "saw", "I saw the movie.", 0, "see", True),
]


@pytest.mark.parametrize(
    "pos_tag,word,sentence,word_occurrence_index,expected_lemma,should_change",
    POS_CASES,
)
def test_lemmatize_contextual_cases(
    pos_tag: str,
    word: str,
    sentence: str,
    word_occurrence_index: int,
    expected_lemma: str,
    should_change: bool,
) -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={
            "word": word,
            "sentence": sentence,
            "word_occurrence_index": word_occurrence_index,
        },
    )
    assert response.status_code == 200
    assert_response_has_request_id_header(response)

    data = response.json()
    assert data["cleaned_word"] == word
    assert data["cleaned_sentence"] == sentence
    assert data["matched_word_count"] >= 1
    assert data["matched_word_occurrence_index"] == word_occurrence_index
    assert data["matched_token"].lower() == word.lower()
    assert data["lemma"] == expected_lemma
    assert (data["lemma"] != data["cleaned_word"]) is should_change


def test_lemmatize_rejects_multiple_words_after_cleaning() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": " running  fast ", "sentence": "They are running fast.", "word_occurrence_index": 0},
    )
    assert_google_error(response, 400, "Input must contain exactly one word after cleaning")


def test_lemmatize_rejects_empty_input_after_cleaning() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "   \t\n  ", "sentence": "They are running fast.", "word_occurrence_index": 0},
    )
    assert_google_error(response, 400, "Input cannot be empty")


def test_lemmatize_rejects_empty_sentence_after_cleaning() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "   \t\n  ", "word_occurrence_index": 0},
    )
    assert_google_error(response, 400, "Sentence cannot be empty")


def test_lemmatize_rejects_missing_target_word_in_sentence() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "They are walking fast.", "word_occurrence_index": 0},
    )
    assert_google_error(response, 400, "Target word must appear in the supplied sentence")


def test_lemmatize_rejects_word_occurrence_index_out_of_range() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "They are running fast.", "word_occurrence_index": 99},
    )
    assert_google_error(response, 400)


def test_lemmatize_rejects_word_occurrence_index_mismatch() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "They are jogging fast.", "word_occurrence_index": 0},
    )
    assert_google_error(response, 400, "Target word must appear in the supplied sentence")


def test_lemmatize_rejects_missing_required_field_with_google_error() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "word_occurrence_index": 0},
    )

    assert_google_error(response, 400, "Request validation failed")
    header_request_id = assert_response_has_request_id_header(response)
    details = response.json()["error"]["details"]
    assert len(details) >= 2
    assert details[0]["@type"] == "type.googleapis.com/google.rpc.BadRequest"
    assert len(details[0]["fieldViolations"]) >= 1
    request_info = details[-1]
    assert request_info["@type"] == "type.googleapis.com/google.rpc.RequestInfo"
    assert request_info["requestId"] == header_request_id


def test_lemmatize_defaults_to_zero_when_index_omitted_and_single_match() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "running", "sentence": "They are running in the park."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["matched_word_count"] == 1
    assert data["matched_word_occurrence_index"] == 0
    assert data["lemma"] == "run"


def test_lemmatize_rejects_omitted_index_when_multiple_matches() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "saw", "sentence": "He saw a saw and sawdust."},
    )

    assert_google_error(
        response,
        400,
        "Multiple matched tokens found; please provide word_occurrence_index explicitly",
    )


def test_lemmatize_propagates_incoming_request_id() -> None:
    incoming_request_id = "req-fixed-123"
    response = client.post(
        "/v1/words:lemmatize",
        headers={"X-Request-Id": incoming_request_id},
        json={
            "word": "running",
            "sentence": "They are running in the park.",
            "word_occurrence_index": 0,
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == incoming_request_id


def test_lemmatize_can_target_second_duplicate_keyword_by_index() -> None:
    response = client.post(
        "/v1/words:lemmatize",
        json={"word": "saw", "sentence": "He saw a saw and sawdust.", "word_occurrence_index": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["matched_token"] == "saw"
    assert data["matched_token_index"] == 3
    assert data["matched_word_count"] == 2
    assert data["matched_word_occurrence_index"] == 1
    assert data["lemma"] == "saw"
