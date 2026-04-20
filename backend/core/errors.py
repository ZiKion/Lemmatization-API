from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .aip_exceptions import AIPError
from .logging_trace import REQUEST_ID_HEADER, get_request_id_from_state

HTTP_TO_CANONICAL_STATUS = {
    400: "INVALID_ARGUMENT",
    401: "UNAUTHENTICATED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    409: "ABORTED",
    429: "RESOURCE_EXHAUSTED",
    499: "CANCELLED",
    500: "INTERNAL",
    501: "UNIMPLEMENTED",
    503: "UNAVAILABLE",
    504: "DEADLINE_EXCEEDED",
}


def canonical_status(http_status_code: int) -> str:
    return HTTP_TO_CANONICAL_STATUS.get(http_status_code, "UNKNOWN")


def google_error_response(
    http_status_code: int,
    message: str,
    details: list[dict] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    merged_details = list(details or [])
    if request_id:
        merged_details.append(
            {
                "@type": "type.googleapis.com/google.rpc.RequestInfo",
                "requestId": request_id,
            }
        )

    payload = {
        "error": {
            "code": http_status_code,
            "message": message,
            "status": canonical_status(http_status_code),
            "details": merged_details,
        }
    }
    response = JSONResponse(status_code=http_status_code, content=payload)
    if request_id:
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AIPError)
    async def handle_aip_error(request: Request, exc: AIPError) -> JSONResponse:
        return google_error_response(
            exc.http_status_code,
            exc.message,
            exc.details,
            request_id=get_request_id_from_state(request),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        details = []

        if isinstance(exc.detail, dict):
            details = [exc.detail]
        elif isinstance(exc.detail, list):
            details = [
                item if isinstance(item, dict) else {"value": item}
                for item in exc.detail
            ]
        return google_error_response(
            exc.status_code,
            message,
            details,
            request_id=get_request_id_from_state(request),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        validation_details = [
            {
                "@type": "type.googleapis.com/google.rpc.BadRequest",
                "fieldViolations": [
                    {
                        "field": ".".join(str(part) for part in err.get("loc", [])),
                        "description": err.get("msg", "Invalid value"),
                    }
                    for err in exc.errors()
                ],
            }
        ]
        return google_error_response(
            http_status_code=400,
            message="Request validation failed",
            details=validation_details,
            request_id=get_request_id_from_state(request),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, __: Exception) -> JSONResponse:
        return google_error_response(
            http_status_code=500,
            message="Internal server error",
            request_id=get_request_id_from_state(request),
        )
