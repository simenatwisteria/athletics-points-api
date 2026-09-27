"""Felles feilformat (``Error`` i kontrakten) og oversetting fra feiltypene i athletics_scoring."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from athletics_scoring.errors import (
    AmbiguousEventError,
    ImplementMismatchError,
    InvalidCombinedEventError,
    InvalidResultError,
    ScoringError,
    UnknownEventError,
    UnknownSystemError,
    UnknownVersionError,
    UnsupportedManualTimingError,
)

# Rekkefølgen teller: underklasser før basisklassen
# (ImplementMismatchError er en UnknownEventError).
SCORING_ERROR_CODES: tuple[tuple[type[ScoringError], str], ...] = (
    (UnknownSystemError, "unknown_system"),
    (UnknownVersionError, "unknown_version"),
    (ImplementMismatchError, "implement_mismatch"),
    (UnknownEventError, "unknown_event"),
    (AmbiguousEventError, "ambiguous_implement"),
    (InvalidResultError, "invalid_result"),
    (UnsupportedManualTimingError, "unsupported_manual_timing"),
    (InvalidCombinedEventError, "invalid_combined_event"),
)


class ApiError(Exception):
    """Feil som svares med kontraktens feilformat."""

    def __init__(
        self, status: int, code: str, message: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def scoring_error_code(exc: ScoringError) -> str | None:
    """Kontraktens ``code`` for en feil fra pakken. ``None`` betyr uventet feil (500)."""
    for cls, code in SCORING_ERROR_CODES:
        if isinstance(exc, cls):
            return code
    return None


def error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"code": code, "message": message, "details": details}


def error_response(
    status: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        {"error": error_body(code, message, details)}, status_code=status, headers=headers
    )


def _field(loc: tuple[int | str, ...]) -> str:
    parts = [str(p) for p in loc if p not in ("body", "query")]
    return ".".join(parts) or "body"


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, exc: ApiError) -> JSONResponse:
        return error_response(exc.status, exc.code, exc.message, exc.details)

    @app.exception_handler(ScoringError)
    async def _scoring_error(request: Request, exc: ScoringError) -> JSONResponse:
        code = scoring_error_code(exc)
        if code is None:
            return error_response(500, "internal_error", "Uventet feil i beregningsmotoren.")
        return error_response(422, code, str(exc))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        first = errors[0] if errors else {"loc": (), "msg": "ugyldig forespørsel"}
        field = _field(tuple(first.get("loc", ())))
        return error_response(
            422,
            "validation_error",
            f"Ugyldig forespørsel, feltet {field}: {first.get('msg', '')}",
            {"field": field},
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception) -> JSONResponse:
        return error_response(500, "internal_error", "Uventet feil.")
