from fastapi import FastAPI

from .api.routes.word_routes import router as word_router
from .core.errors import register_exception_handlers
from .core.logging_trace import register_request_trace_and_logging_middleware
from .core.nlp import nlp

app = FastAPI(
    title="Lemmatization API",
    version="0.1.0",
    description=(
        "Context-aware English lemmatization API powered by spaCy. / "
        "基于 spaCy 的英文语境词形还原 API。"
    ),
)

register_request_trace_and_logging_middleware(app)
register_exception_handlers(app)
app.include_router(word_router)


@app.get(
    "/health",
    tags=["System / 系统"],
    summary="Health check / 健康检查",
    description="Simple liveness check for the API process / 用于确认 API 进程存活的简单检查",
)
def health() -> dict[str, str]:
    return {"status": "ok"}
