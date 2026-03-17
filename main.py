from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from api.routes.lemmatization import router as lemmatization_router
from schemas.error import build_aip_error


app = FastAPI(
	title="Lemmatization API",
	version="2.0.0",
	description="Google AIP styled lemmatization service based on FastAPI and spaCy.",
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
	message = "Invalid request. Expected a non-empty string field 'word'."
	if exc.errors():
		message = f"Invalid argument: {exc.errors()[0].get('msg', message)}"
	return JSONResponse(
		status_code=400,
		content=build_aip_error(code=400, status="INVALID_ARGUMENT", message=message),
	)


@app.exception_handler(ValueError)
async def value_error_exception_handler(_, exc: ValueError) -> JSONResponse:
	return JSONResponse(
		status_code=400,
		content=build_aip_error(code=400, status="INVALID_ARGUMENT", message=str(exc)),
	)


app.include_router(lemmatization_router)


@app.get("/healthz")
def health_check() -> dict[str, str]:
	return {"status": "ok"}
