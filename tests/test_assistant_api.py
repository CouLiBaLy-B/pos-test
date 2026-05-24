from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from assistant_api.config import Settings, _normalize_base_url
from assistant_api.main import app, get_gateway, get_settings
from assistant_api.models import ChatRequest, ChatResponse
from assistant_api.service import build_upstream_headers, build_upstream_payload


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
