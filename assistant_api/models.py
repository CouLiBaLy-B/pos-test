from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    prompt: str | None = Field(default=None, min_length=1)
    messages: list[ChatMessage] = Field(default_factory=list)
    system: str | None = None
    model: str | None = None
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_input(self) -> "ChatRequest":
        if not self.prompt and not self.messages:
            raise ValueError("Either 'prompt' or 'messages' must be provided.")
        return self


class ChatResponse(BaseModel):
    id: str | None = None
    model: str
    message: ChatMessage
    content_blocks: list[dict[str, Any]] = Field(default_factory=list)
    stop_reason: str | None = None
    usage: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    version: str
    upstream_base_url: str
    default_model: str


class ConfigResponse(BaseModel):
    upstream_base_url: str
    model: str
    default_max_tokens: int
    has_system_prompt: bool
