from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from assistant_api.config import Settings, get_settings
from assistant_api.models import ChatRequest, ChatResponse, ConfigResponse, HealthResponse
from assistant_api.service import AssistantGateway, UpstreamAPIError, build_upstream_payload

APP_ROOT = Path(__file__).resolve().parent
UI_PATH = APP_ROOT / "static" / "index.html"
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

app = FastAPI(
    title="Assistant API",
    version="0.3.0",
    description="API REST et passerelle Anthropic-compatible pour dialoguer avec l'assistant local via vLLM.",
)


def get_gateway(settings: Settings = Depends(get_settings)) -> AssistantGateway:
    return AssistantGateway(settings)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(UI_PATH)


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


@app.post("/api/v1/chat/stream", tags=["assistant"])
async def chat_stream(
    request: ChatRequest,
    gateway: AssistantGateway = Depends(get_gateway),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    try:
        payload = build_upstream_payload(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return StreamingResponse(
        gateway.stream_anthropic_messages(payload),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@app.post("/v1/messages", tags=["anthropic-gateway"], response_model=None)
async def anthropic_messages(
    request: Request,
    gateway: AssistantGateway = Depends(get_gateway),
):
    payload: dict[str, Any] = await request.json()
    stream = bool(payload.get("stream"))

    if stream:
        return StreamingResponse(
            gateway.stream_anthropic_messages(payload),
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )

    try:
        data = await gateway.anthropic_messages(payload)
    except UpstreamAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return JSONResponse(data)


@app.post("/v1/messages/count_tokens", tags=["anthropic-gateway"], response_model=None)
async def anthropic_count_tokens(
    request: Request,
    gateway: AssistantGateway = Depends(get_gateway),
):
    payload: dict[str, Any] = await request.json()
    try:
        data = await gateway.count_tokens(payload)
    except UpstreamAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return JSONResponse(data)
