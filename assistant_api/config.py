from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "assistant-api"
    app_version: str = "0.2.0"
    upstream_base_url: str = "http://localhost:4000"
    auth_token: str = "sk-local-dummy"
    model: str = "claude-3-5-sonnet-20241022"
    default_max_tokens: int = 2048
    request_timeout: float = 120.0
    default_system_prompt: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    upstream_base_url = os.getenv(
        "ASSISTANT_UPSTREAM_BASE_URL",
        os.getenv("ANTHROPIC_BASE_URL", "http://localhost:4000"),
    ).rstrip("/")

    auth_token = os.getenv(
        "ASSISTANT_AUTH_TOKEN",
        os.getenv("ANTHROPIC_AUTH_TOKEN", "sk-local-dummy"),
    )

    model = os.getenv(
        "ASSISTANT_MODEL",
        os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
    )

    default_max_tokens = int(os.getenv("ASSISTANT_DEFAULT_MAX_TOKENS", "2048"))
    request_timeout = float(os.getenv("ASSISTANT_REQUEST_TIMEOUT", "120"))
    default_system_prompt = os.getenv("ASSISTANT_SYSTEM_PROMPT") or None

    return Settings(
        upstream_base_url=upstream_base_url,
        auth_token=auth_token,
        model=model,
        default_max_tokens=default_max_tokens,
        request_timeout=request_timeout,
        default_system_prompt=default_system_prompt,
    )
