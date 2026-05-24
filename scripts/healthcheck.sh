#!/usr/bin/env bash
set -euo pipefail

VLLM_URL="${VLLM_URL:-http://localhost:8000/v1/models}"
ASSISTANT_API_URL="${ASSISTANT_API_URL:-http://localhost:8080/healthz}"

echo "[1/2] Vérification vLLM: $VLLM_URL"
curl -fsS "$VLLM_URL" | jq . >/dev/null
echo "OK vLLM"

echo "[2/2] Vérification Assistant API: $ASSISTANT_API_URL"
curl -fsS "$ASSISTANT_API_URL" | jq . >/dev/null
echo "OK Assistant API"

echo "Stack opérationnelle"
