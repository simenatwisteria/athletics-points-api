"""Innstillinger fra miljøvariabler."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_CORS_ALLOWED_ORIGINS = ("https://5kamp.minfriidrett.no",)
DEFAULT_RATE_LIMIT_PER_MINUTE = 600


@dataclass(frozen=True, slots=True)
class Settings:
    cors_allowed_origins: tuple[str, ...] = DEFAULT_CORS_ALLOWED_ORIGINS
    """Opphav som får CORS-headere. Ingen jokertegn."""
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE
    """Forespørsler per klient-IP i et glidende vindu på 60 sekunder (B-4). 0 slår av grensen."""
    trust_proxy: bool = False
    """Bruk ``X-Forwarded-For`` som klient-IP. Bare bak en proxy vi stoler på (Railway)."""

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        env = os.environ if env is None else env
        origins = env.get("CORS_ALLOWED_ORIGINS")
        return cls(
            cors_allowed_origins=DEFAULT_CORS_ALLOWED_ORIGINS
            if origins is None
            else tuple(o.strip() for o in origins.split(",") if o.strip() and o.strip() != "*"),
            rate_limit_per_minute=int(
                env.get("RATE_LIMIT_PER_MINUTE", DEFAULT_RATE_LIMIT_PER_MINUTE)
            ),
            trust_proxy=env.get("TRUST_PROXY", "0").strip().lower() in {"1", "true", "yes"},
        )
