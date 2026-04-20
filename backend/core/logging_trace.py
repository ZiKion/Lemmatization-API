import json
import logging
import time
from typing import Any
import uuid

from fastapi import FastAPI, Request

REQUEST_ID_HEADER = "X-Request-Id"

logger = logging.getLogger("lemmatization_api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False


def extract_request_id(request: Request) -> str:
    header_value = request.headers.get(REQUEST_ID_HEADER, "").strip()
    return header_value if header_value else str(uuid.uuid4())


def get_request_id_from_state(request: Request) -> str:
    request_id = getattr(request.state, "request_id", "").strip()
    return request_id if request_id else extract_request_id(request)


def emit_json_log(level: str, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    if level == "error":
        logger.error(text)
    else:
        logger.info(text)


def register_request_trace_and_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_trace_and_logging_middleware(request: Request, call_next):
        request_id = extract_request_id(request)
        request.state.request_id = request_id
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            emit_json_log(
                "error",
                {
                    "event": "request_failed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id
        emit_json_log(
            "info",
            {
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
