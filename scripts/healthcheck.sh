#!/usr/bin/env bash
set -euo pipefail

VLLM_URL="${VLLM_URL:-http://localhost:8000/v1/models}"
LITELLM_URL="${LITELLM_URL:-http://localhost:4000/health/readiness}"

echo "[1/2] Vérification vLLM: $VLLM_URL"
curl -fsS "$VLLM_URL" | jq . >/dev/null
echo "OK vLLM"

echo "[2/2] Vérification LiteLLM: $LITELLM_URL"
curl -fsS "$LITELLM_URL" | jq . >/dev/null || curl -fsS "$LITELLM_URL" >/dev/null
echo "OK LiteLLM"

echo "Stack opérationnelle"
