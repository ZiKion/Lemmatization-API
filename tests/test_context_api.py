from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_context_endpoint_selected_text_mode_distinguishes_adjective() -> None:
	response = client.post(
		"/api/v1/lemmas:resolve",
		json={
			"sentence": "This is a better choice.",
			"target_word": "better",
		},
	)

	assert response.status_code == 200
	body = response.json()
	assert body["token"] == "better"
	assert body["lemma"] == "good"


def test_context_endpoint_selected_text_mode_distinguishes_adverb() -> None:
	response = client.post(
		"/api/v1/lemmas:resolve",
		json={
			"sentence": "She sings better than him.",
			"target_word": "better",
		},
	)

	assert response.status_code == 200
	body = response.json()
	assert body["token"] == "better"
	assert body["lemma"] == "well"


def test_context_endpoint_sentence_mode_for_worst() -> None:
	response = client.post(
		"/api/v1/lemmas:resolve",
		json={
			"sentence": "This is the worst case.",
			"target_word": "worst",
		},
	)

	assert response.status_code == 200
	body = response.json()
	assert body["token"] == "worst"
	assert body["lemma"] == "bad"


def test_context_endpoint_sentence_mode_for_plural_noun() -> None:
	response = client.post(
		"/api/v1/lemmas:resolve",
		json={
			"sentence": "Cats were running fast.",
			"target_word": "Cats",
		},
	)

	assert response.status_code == 200
	body = response.json()
	assert body["token"] == "Cats"
	assert body["lemma"] == "cat"


def test_context_endpoint_keeps_regular_singular_noun_bore() -> None:
	response = client.post(
		"/api/v1/lemmas:resolve",
		json={
			"sentence": "It was a bore to listen to him.",
			"target_word": "bore",
		},
	)

	assert response.status_code == 200
	body = response.json()
	assert body["token"] == "bore"
	assert body["lemma"] == "bore"


def test_context_endpoint_invalid_locator_mode_returns_aip_error() -> None:
	response = client.post(
		"/api/v1/lemmas:resolve",
		json={
			"sentence": "Some text",
			"target_word": "missing",
		},
	)

	assert response.status_code == 400
	body = response.json()
	assert body["error"]["status"] == "INVALID_ARGUMENT"