from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class LemmatizeRequest(BaseModel):
	word: Annotated[
		str,
		StringConstraints(strict=True, strip_whitespace=True, min_length=1),
	] = Field(..., description="Input word to lemmatize")


class LemmatizeInContextRequest(BaseModel):
	sentence: Annotated[
		str,
		StringConstraints(strict=True, strip_whitespace=False, min_length=1),
	] = Field(..., description="Sentence context")
	target_word: Annotated[
		str,
		StringConstraints(strict=True, strip_whitespace=True, min_length=1),
	] = Field(..., description="Word to locate and lemmatize in sentence")