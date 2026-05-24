from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from assistant_api.config import Settings, _normalize_base_url
from assistant_api.main import app, get_gateway, get_settings
from assistant_api.models import ChatRequest, ChatResponse
from assistant_api.service import (
    approximate_input_tokens,
    build_sse_error_event,
    build_upstream_headers,
    build_upstream_payload,
)


class FakeGateway:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="msg_test_123",
            model=request.model or "claude-sonnet-local",
            message={"role": "assistant", "content": f"Echo: {request.prompt or request.messages[-1].content}"},
            content_blocks=[{"type": "text", "text": f"Echo: {request.prompt or request.messages[-1].content}"}],
            stop_reason="end_turn",
            usage={"input_tokens": 10, "output_tokens": 8},
        )

    async def anthropic_messages(self, payload: dict) -> dict:
        prompt = payload["messages"][-1]["content"]
        return {
            "id": "msg_raw_123",
            "model": payload.get("model", "claude-sonnet-local"),
            "role": "assistant",
            "type": "message",
            "content": [{"type": "text", "text": f"Raw Echo: {prompt}"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 9, "output_tokens": 4},
        }

    async def count_tokens(self, payload: dict) -> dict:
        return {"input_tokens": 42}

    async def stream_anthropic_messages(self, payload: dict):
        prompt = payload["messages"][-1]["content"]
        yield b'event: message_start\ndata: {"type":"message_start","message":{"id":"msg_stream_123","model":"claude-sonnet-local"}}\n\n'
        yield (
            'event: content_block_delta\n'
            f'data: {{"type":"content_block_delta","delta":{{"type":"text_delta","text":"Echo: {prompt}"}}}}\n\n'
        ).encode()
        yield b'event: message_stop\ndata: {"type":"message_stop"}\n\n'



def test_build_upstream_payload_merges_prompt_and_system_messages() -> None:
    settings = Settings(
        upstream_base_url="http://localhost:8000",
        auth_token="dummy",
        api_key="dummy",
        model="claude-sonnet-local",
        default_max_tokens=2048,
        request_timeout=120.0,
        default_system_prompt="Global system prompt",
    )

    request = ChatRequest(
        prompt="Explique le dépôt",
        system="Réponds en français.",
        messages=[
            {"role": "system", "content": "Concentre-toi sur l'architecture."},
            {"role": "user", "content": "Quel est le rôle de vLLM ?"},
        ],
        temperature=0.2,
    )

    payload = build_upstream_payload(request, settings)

    assert payload["model"] == "claude-sonnet-local"
    assert payload["max_tokens"] == 2048
    assert payload["temperature"] == 0.2
    assert payload["system"] == "Global system prompt\n\nRéponds en français.\n\nConcentre-toi sur l'architecture."
    assert payload["messages"] == [
        {"role": "user", "content": "Quel est le rôle de vLLM ?"},
        {"role": "user", "content": "Explique le dépôt"},
    ]



def test_build_upstream_headers_include_bearer_and_api_key() -> None:
    settings = Settings(auth_token="dummy-token", api_key="dummy-key")
    headers = build_upstream_headers(settings)

    assert headers["authorization"] == "Bearer dummy-token"
    assert headers["x-api-key"] == "dummy-key"
    assert headers["anthropic-version"] == "2023-06-01"


@pytest.mark.parametrize(
    ("raw_url", "normalized_url"),
    [
        ("http://localhost:8000", "http://localhost:8000"),
        ("http://localhost:8000/", "http://localhost:8000"),
        ("http://localhost:8000/v1", "http://localhost:8000"),
        ("http://localhost:8000/v1/", "http://localhost:8000"),
    ],
)
def test_normalize_base_url(raw_url: str, normalized_url: str) -> None:
    assert _normalize_base_url(raw_url) == normalized_url



def test_chat_request_rejects_system_only_messages() -> None:
    with pytest.raises(ValueError):
        ChatRequest(messages=[{"role": "system", "content": "Only system."}])



def test_approximate_input_tokens_counts_text_fragments() -> None:
    payload = {
        "system": "Tu es concis.",
        "messages": [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": [{"type": "text", "text": "Salut"}]},
        ],
    }
    assert approximate_input_tokens(payload) >= 1



def test_build_sse_error_event_uses_anthropic_like_error_shape() -> None:
    event = build_sse_error_event("boom").decode()
    assert "event: error" in event
    assert '"message": "boom"' in event



def test_root_ui_is_served() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Assistant local" in response.text
    assert "/api/v1/chat/stream" in response.text



def test_health_endpoint_returns_runtime_config() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        upstream_base_url="http://vllm:8000",
        auth_token="dummy",
        api_key="dummy",
        model="claude-sonnet-local",
        default_max_tokens=2048,
        request_timeout=120.0,
    )
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["upstream_base_url"] == "http://vllm:8000"
    app.dependency_overrides.clear()



def test_chat_endpoint_uses_gateway_dependency() -> None:
    app.dependency_overrides[get_gateway] = lambda: FakeGateway()
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={
            "prompt": "Bonjour assistant",
            "max_tokens": 128,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"]["role"] == "assistant"
    assert body["message"]["content"] == "Echo: Bonjour assistant"
    assert body["stop_reason"] == "end_turn"
    app.dependency_overrides.clear()



def test_chat_stream_endpoint_returns_sse() -> None:
    app.dependency_overrides[get_gateway] = lambda: FakeGateway()
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"prompt": "Bonjour assistant", "max_tokens": 128},
    ) as response:
        content = "".join(response.iter_text())

    assert response.status_code == 200
    assert "event: content_block_delta" in content
    assert "Echo: Bonjour assistant" in content
    app.dependency_overrides.clear()



def test_anthropic_messages_endpoint_returns_message_shape() -> None:
    app.dependency_overrides[get_gateway] = lambda: FakeGateway()
    client = TestClient(app)

    response = client.post(
        "/v1/messages",
        json={
            "model": "claude-sonnet-local",
            "max_tokens": 128,
            "messages": [{"role": "user", "content": "Bonjour"}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "message"
    assert body["content"][0]["text"] == "Raw Echo: Bonjour"
    app.dependency_overrides.clear()



def test_anthropic_count_tokens_endpoint_returns_counts() -> None:
    app.dependency_overrides[get_gateway] = lambda: FakeGateway()
    client = TestClient(app)

    response = client.post(
        "/v1/messages/count_tokens",
        json={
            "model": "claude-sonnet-local",
            "messages": [{"role": "user", "content": "Bonjour"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["input_tokens"] == 42
    app.dependency_overrides.clear()
