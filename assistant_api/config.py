from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


def _normalize_base_url(url: str) -> str:
    normalized = url.rstrip("/")
    if normalized.endswith("/v1"):
        normalized = normalized[:-3]
    return normalized.rstrip("/")


@dataclass(frozen=True)
class Settings:
    app_name: str = "assistant-api"
    app_version: str = "0.3.0"
    upstream_base_url: str = "http://localhost:8000"
    auth_token: str = "dummy"
    api_key: str = "dummy"
    model: str = "claude-sonnet-local"
    default_max_tokens: int = 2048
    request_timeout: float = 120.0
    default_system_prompt: str | None = None
    anthropic_version: str = "2023-06-01"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    upstream_base_url = _normalize_base_url(
        os.getenv(
            "ASSISTANT_UPSTREAM_BASE_URL",
            os.getenv("ANTHROPIC_BASE_URL", "http://localhost:8000"),
        )
    )

    auth_token = os.getenv(
        "ASSISTANT_AUTH_TOKEN",
        os.getenv("ANTHROPIC_AUTH_TOKEN", "dummy"),
    )

    api_key = os.getenv(
        "ASSISTANT_API_KEY",
        os.getenv("ANTHROPIC_API_KEY", auth_token or "dummy"),
    )

    model = os.getenv(
        "ASSISTANT_MODEL",
        os.getenv(
            "ANTHROPIC_DEFAULT_SONNET_MODEL",
            os.getenv(
                "ANTHROPIC_MODEL",
                os.getenv("VLLM_SERVED_MODEL_NAME", "claude-sonnet-local"),
            ),
        ),
    )

    default_max_tokens = int(os.getenv("ASSISTANT_DEFAULT_MAX_TOKENS", "2048"))
    request_timeout = float(os.getenv("ASSISTANT_REQUEST_TIMEOUT", "120"))
    default_system_prompt = os.getenv("ASSISTANT_SYSTEM_PROMPT") or None
    anthropic_version = os.getenv("ASSISTANT_ANTHROPIC_VERSION", "2023-06-01")

    return Settings(
        upstream_base_url=upstream_base_url,
        auth_token=auth_token,
        api_key=api_key,
        model=model,
        default_max_tokens=default_max_tokens,
        request_timeout=request_timeout,
        default_system_prompt=default_system_prompt,
        anthropic_version=anthropic_version,
    )
