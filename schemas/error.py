from pydantic import BaseModel


class AIPError(BaseModel):
	code: int
	message: str
	status: str


class AIPErrorResponse(BaseModel):
	error: AIPError


def build_aip_error(code: int, status: str, message: str) -> dict:
	return {
		"error": {
			"code": code,
			"message": message,
			"status": status,
		}
	}