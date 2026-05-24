from __future__ import annotations

from typing import Any

import httpx

from assistant_api.config import Settings
from assistant_api.models import ChatMessage, ChatRequest, ChatResponse


class UpstreamAPIError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _merge_system_prompts(request: ChatRequest, settings: Settings) -> str | None:
    parts: list[str] = []
    if settings.default_system_prompt:
        parts.append(settings.default_system_prompt)
    if request.system:
        parts.append(request.system)
    parts.extend(message.content for message in request.messages if message.role == "system")
    merged = "\n\n".join(part.strip() for part in parts if part and part.strip())
    return merged or None


def build_upstream_payload(request: ChatRequest, settings: Settings) -> dict[str, Any]:
    messages = [
        {"role": message.role, "content": message.content}
        for message in request.messages
        if message.role in {"user", "assistant"}
    ]

    if request.prompt:
        messages.append({"role": "user", "content": request.prompt})

    payload: dict[str, Any] = {
        "model": request.model or settings.model,
        "max_tokens": request.max_tokens or settings.default_max_tokens,
        "messages": messages,
    }

    system_prompt = _merge_system_prompts(request, settings)
    if system_prompt:
        payload["system"] = system_prompt

    if request.temperature is not None:
        payload["temperature"] = request.temperature

    if request.metadata:
        payload["metadata"] = request.metadata

    return payload


def _extract_text(content_blocks: list[dict[str, Any]]) -> str:
    texts = [block.get("text", "") for block in content_blocks if block.get("type") == "text"]
    text = "\n".join(part.strip() for part in texts if part and part.strip())
    return text.strip() or "[Réponse sans contenu texte]"


class AssistantGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def chat(self, request: ChatRequest) -> ChatResponse:
        payload = build_upstream_payload(request, self.settings)
        url = f"{self.settings.upstream_base_url}/v1/messages"
        headers = {
            "x-api-key": self.settings.auth_token,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.is_error:
            detail = response.text
            try:
                body = response.json()
                detail = body.get("error", {}).get("message") or body.get("detail") or detail
            except ValueError:
                pass
            raise UpstreamAPIError(response.status_code, detail)

        data = response.json()
        content_blocks = data.get("content", [])

        return ChatResponse(
            id=data.get("id"),
            model=data.get("model", payload["model"]),
            message=ChatMessage(role="assistant", content=_extract_text(content_blocks)),
            content_blocks=content_blocks,
            stop_reason=data.get("stop_reason"),
            usage=data.get("usage"),
        )
