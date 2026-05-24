from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from assistant_api.config import Settings, get_settings
from assistant_api.models import ChatRequest, ChatResponse, ConfigResponse, HealthResponse
from assistant_api.service import AssistantGateway, UpstreamAPIError

app = FastAPI(
    title="Assistant API",
    version="0.2.0",
    description="API REST minimale pour dialoguer avec l'assistant local via vLLM et l'API Anthropic Messages.",
)


def get_gateway(settings: Settings = Depends(get_settings)) -> AssistantGateway:
    return AssistantGateway(settings)


@app.get("/healthz", response_model=HealthResponse, tags=["system"])
def healthz(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        upstream_base_url=settings.upstream_base_url,
        default_model=settings.model,
    )


@app.get("/api/v1/config", response_model=ConfigResponse, tags=["assistant"])
def read_config(settings: Settings = Depends(get_settings)) -> ConfigResponse:
    return ConfigResponse(
        upstream_base_url=settings.upstream_base_url,
        model=settings.model,
        default_max_tokens=settings.default_max_tokens,
        has_system_prompt=bool(settings.default_system_prompt),
    )


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["assistant"])
async def chat(
    request: ChatRequest,
    gateway: AssistantGateway = Depends(get_gateway),
) -> ChatResponse:
    try:
        return await gateway.chat(request)
    except UpstreamAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
