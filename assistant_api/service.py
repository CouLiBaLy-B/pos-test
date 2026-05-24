from __future__ import annotations

import json
from typing import Any, AsyncIterator

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

    if not messages:
        raise ValueError("At least one user or assistant message is required for the upstream request.")

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


def build_upstream_headers(settings: Settings) -> dict[str, str]:
    headers = {
        "anthropic-version": settings.anthropic_version,
        "content-type": "application/json",
    }
    if settings.auth_token:
        headers["authorization"] = f"Bearer {settings.auth_token}"
    if settings.api_key:
        headers["x-api-key"] = settings.api_key
    return headers


def build_sse_error_event(detail: str) -> bytes:
    payload = json.dumps({"type": "error", "error": {"message": detail}}, ensure_ascii=False)
    return f"event: error\ndata: {payload}\n\n".encode("utf-8")


def _extract_text(content_blocks: list[dict[str, Any]]) -> str:
    texts = [block.get("text", "") for block in content_blocks if block.get("type") == "text"]
    text = "\n".join(part.strip() for part in texts if part and part.strip())
    return text.strip() or "[Réponse sans contenu texte]"


def _collect_text_fragments(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            parts.extend(_collect_text_fragments(item))
        return parts
    if isinstance(value, dict):
        if value.get("type") == "text" and isinstance(value.get("text"), str):
            return [value["text"]]
        parts: list[str] = []
        for nested in value.values():
            parts.extend(_collect_text_fragments(nested))
        return parts
    return [str(value)]


def approximate_input_tokens(payload: dict[str, Any]) -> int:
    fragments: list[str] = []
    fragments.extend(_collect_text_fragments(payload.get("system")))
    fragments.extend(_collect_text_fragments(payload.get("messages", [])))
    combined = "\n".join(part for part in fragments if part and part.strip()).strip()
    if not combined:
        return 0
    return max(1, (len(combined) + 3) // 4)


class AssistantGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.upstream_base_url}{path}"
        headers = build_upstream_headers(self.settings)

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.RequestError as exc:
            raise UpstreamAPIError(502, f"Impossible de joindre l'upstream Anthropic-compatible: {exc}") from exc

        if response.is_error:
            detail = response.text
            try:
                body = response.json()
                detail = body.get("error", {}).get("message") or body.get("detail") or detail
            except ValueError:
                pass
            raise UpstreamAPIError(response.status_code, detail)

        return response.json()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        payload = build_upstream_payload(request, self.settings)
        data = await self._post_json("/v1/messages", payload)
        content_blocks = data.get("content", [])

        return ChatResponse(
            id=data.get("id"),
            model=data.get("model", payload["model"]),
            message=ChatMessage(role="assistant", content=_extract_text(content_blocks)),
            content_blocks=content_blocks,
            stop_reason=data.get("stop_reason"),
            usage=data.get("usage"),
        )

    async def anthropic_messages(self, payload: dict[str, Any]) -> dict[str, Any]:
        sanitized_payload = dict(payload)
        sanitized_payload.pop("stream", None)
        return await self._post_json("/v1/messages", sanitized_payload)

    async def count_tokens(self, payload: dict[str, Any]) -> dict[str, Any]:
        sanitized_payload = dict(payload)
        sanitized_payload.pop("stream", None)
        try:
            return await self._post_json("/v1/messages/count_tokens", sanitized_payload)
        except UpstreamAPIError as exc:
            if exc.status_code not in {404, 405, 501}:
                raise
            return {"input_tokens": approximate_input_tokens(sanitized_payload)}

    async def stream_anthropic_messages(self, payload: dict[str, Any]) -> AsyncIterator[bytes]:
        url = f"{self.settings.upstream_base_url}/v1/messages"
        headers = build_upstream_headers(self.settings)
        streaming_payload = dict(payload)
        streaming_payload["stream"] = True

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
                async with client.stream("POST", url, headers=headers, json=streaming_payload) as response:
                    if response.is_error:
                        detail = await response.aread()
                        yield build_sse_error_event(detail.decode("utf-8", errors="replace"))
                        return
                    async for chunk in response.aiter_raw():
                        if chunk:
                            yield chunk
        except httpx.RequestError as exc:
            yield build_sse_error_event(f"Impossible de joindre l'upstream Anthropic-compatible: {exc}")
