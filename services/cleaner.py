import re


def clean_word(raw_text: str) -> str:
	text = re.sub(r"\s+", " ", raw_text).strip()
	if not text:
		raise ValueError("Invalid argument: 'word' must be a non-empty string.")

	first_token = text.split(" ")[0]
	cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", first_token)
	if not cleaned:
		raise ValueError("Invalid argument: 'word' must contain at least one valid character.")

	return cleaned