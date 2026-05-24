# Architecture recommandée

## Vue d'ensemble

Cette branche `feat/sans-litellm` supprime la couche LiteLLM par défaut et s'appuie directement sur l'implémentation **Anthropic Messages API** de vLLM.

```text
Claude Code / Client HTTP
   │
   ├─ Skills (instructions locales, côté Claude Code)
   ├─ MCP (capacités externes, à limiter)
   │
   ▼
Assistant API (FastAPI)
   │
   ▼
vLLM (Anthropic Messages API)
   │
   ▼
Qwen3-Coder-30B-A3B-Instruct-AWQ
```

## Choix structurants

### 1. Modèle

Le choix par défaut du projet est :

- `Qwen/Qwen3-Coder-30B-A3B-Instruct-AWQ`

Pourquoi :

- très bon compromis qualité/vitesse/VRAM sur RTX 4090
- pertinent pour du codage agentique
- support correct du tool calling avec le bon parser

### 2. Parser d'outils

Choix par défaut :

- `qwen3_xml`

Raison : stable pour `Qwen3-Coder-30B-A3B` dans la documentation vLLM officielle.

### 3. Nom de modèle servi

Le dépôt sert maintenant le modèle sous :

- `claude-sonnet-local`

Ce choix évite les `/` dans le nom servi et permet à Claude Code de découvrir le modèle via `/v1/models`.

### 4. Claude Code

Claude Code pointe directement vers `http://localhost:8000` avec :

- `ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-local`
- `ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-sonnet-local`
- `ANTHROPIC_DEFAULT_OPUS_MODEL=claude-sonnet-local`

### 5. MCP Tool Search

Par prudence, `ENABLE_TOOL_SEARCH=false` est utilisé par défaut sur cette branche.

Sur un hôte non first-party, Claude Code désactive déjà automatiquement le tool search si le backend ne gère pas `tool_reference`. Le forcer à `true` peut rendre la session fragile selon le backend.

### 6. API HTTP

Le dépôt inclut une API FastAPI exposée sur le port `8080`.

Cette couche sert à :

- fournir un point d'entrée REST simple pour une UI ou un script
- centraliser le modèle, le prompt système et les timeouts
- dialoguer directement avec un endpoint Anthropic-compatible servi par vLLM
