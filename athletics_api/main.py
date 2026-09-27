"""App-fabrikken. Start: ``uvicorn athletics_api.main:app --host 0.0.0.0 --port $PORT``."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from athletics_api.errors import install_error_handlers
from athletics_api.ratelimit import RateLimitMiddleware, SlidingWindowLimiter
from athletics_api.routes import router
from athletics_api.service import Service
from athletics_api.settings import Settings
from athletics_scoring import __version__


def create_app(settings: Settings | None = None, service: Service | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(
        title="Athletics Points API",
        version=__version__,
        summary="Åpen, transparent beregning av norske friidrettspoeng.",
    )
    app.state.settings = settings
    app.state.service = service or Service()
    install_error_handlers(app)
    app.include_router(router)
    if settings.rate_limit_per_minute > 0:
        app.add_middleware(
            RateLimitMiddleware,
            limiter=SlidingWindowLimiter(settings.rate_limit_per_minute),
            trust_proxy=settings.trust_proxy,
        )
    # Sist lagt til ligger ytterst: også 429-svar får CORS-headere.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    return app


app = create_app()
