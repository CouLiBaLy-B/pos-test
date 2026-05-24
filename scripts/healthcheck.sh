#!/usr/bin/env bash
set -euo pipefail

VLLM_URL="${VLLM_URL:-http://localhost:8000/v1/models}"
LITELLM_URL="${LITELLM_URL:-http://localhost:4000/health/readiness}"
ASSISTANT_API_URL="${ASSISTANT_API_URL:-http://localhost:8080/healthz}"

echo "[1/3] Vérification vLLM: $VLLM_URL"
curl -fsS "$VLLM_URL" | jq . >/dev/null
echo "OK vLLM"

echo "[2/3] Vérification LiteLLM: $LITELLM_URL"
curl -fsS "$LITELLM_URL" | jq . >/dev/null || curl -fsS "$LITELLM_URL" >/dev/null
echo "OK LiteLLM"

echo "[3/3] Vérification Assistant API: $ASSISTANT_API_URL"
curl -fsS "$ASSISTANT_API_URL" | jq . >/dev/null
echo "OK Assistant API"

echo "Stack opérationnelle"
