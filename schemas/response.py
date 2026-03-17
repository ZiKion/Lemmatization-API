from pydantic import BaseModel, Field


class LemmatizeResponse(BaseModel):
	lemma: str = Field(..., description="Lemmatized result")


class LemmatizeInContextResponse(BaseModel):
	lemma: str = Field(..., description="Lemmatized result for located token")
	token: str = Field(..., description="Resolved token from the input text")
	start: int = Field(..., description="Start char offset of resolved token")
	end: int = Field(..., description="End char offset of resolved token")