from __future__ import annotations

from fastapi.testclient import TestClient

from assistant_api.config import Settings
from assistant_api.main import app, get_gateway, get_settings
from assistant_api.models import ChatRequest, ChatResponse
from assistant_api.service import AssistantGateway, build_upstream_payload


class FakeGateway:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="msg_test_123",
            model=request.model or "claude-3-5-sonnet-20241022",
            message={"role": "assistant", "content": f"Echo: {request.prompt or request.messages[-1].content}"},
            content_blocks=[{"type": "text", "text": f"Echo: {request.prompt or request.messages[-1].content}"}],
            stop_reason="end_turn",
            usage={"input_tokens": 10, "output_tokens": 8},
        )


def test_build_upstream_payload_merges_prompt_and_system_messages() -> None:
    settings = Settings(
        upstream_base_url="http://localhost:4000",
        auth_token="sk-local-dummy",
        model="claude-3-5-sonnet-20241022",
        default_max_tokens=2048,
        request_timeout=120.0,
        default_system_prompt="Global system prompt",
    )

    request = ChatRequest(
        prompt="Explique le dépôt",
        system="Réponds en français.",
        messages=[
            {"role": "system", "content": "Concentre-toi sur l'architecture."},
            {"role": "user", "content": "Quel est le rôle de LiteLLM ?"},
        ],
        temperature=0.2,
    )

    payload = build_upstream_payload(request, settings)

    assert payload["model"] == "claude-3-5-sonnet-20241022"
    assert payload["max_tokens"] == 2048
    assert payload["temperature"] == 0.2
    assert payload["system"] == "Global system prompt\n\nRéponds en français.\n\nConcentre-toi sur l'architecture."
    assert payload["messages"] == [
        {"role": "user", "content": "Quel est le rôle de LiteLLM ?"},
        {"role": "user", "content": "Explique le dépôt"},
    ]


def test_health_endpoint_returns_runtime_config() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        upstream_base_url="http://litellm:4000",
        auth_token="sk-local-dummy",
        model="claude-3-5-sonnet-20241022",
        default_max_tokens=2048,
        request_timeout=120.0,
    )
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["upstream_base_url"] == "http://litellm:4000"
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
