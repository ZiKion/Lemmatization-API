from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_lemmatize_success() -> None:
	response = client.post("/api/v1/lemmas", json={"word": "running"})

	assert response.status_code == 200
	assert response.json() == {"lemma": "run"}


def test_lemmatize_irregular_plural_success() -> None:
	response = client.post("/api/v1/lemmas", json={"word": "phenomena"})

	assert response.status_code == 200
	assert response.json() == {"lemma": "phenomenon"}


def test_lemmatize_superlative_worst_success() -> None:
	response = client.post("/api/v1/lemmas", json={"word": "worst"})

	assert response.status_code == 200
	assert response.json() == {"lemma": "bad"}


def test_lemmatize_empty_string_returns_aip_invalid_argument() -> None:
	response = client.post("/api/v1/lemmas", json={"word": "   "})
	body = response.json()

	assert response.status_code == 400
	assert "error" in body
	assert body["error"]["code"] == 400
	assert body["error"]["status"] == "INVALID_ARGUMENT"
	assert isinstance(body["error"]["message"], str)


def test_lemmatize_non_string_returns_aip_invalid_argument() -> None:
	response = client.post("/api/v1/lemmas", json={"word": 123})
	body = response.json()

	assert response.status_code == 400
	assert "error" in body
	assert body["error"]["code"] == 400
	assert body["error"]["status"] == "INVALID_ARGUMENT"
	assert isinstance(body["error"]["message"], str)