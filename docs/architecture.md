# Architecture recommandée

## Vue d'ensemble

Cette stack part du principe que l'interface agentique reste **Claude Code**, mais que l'inférence est **locale**.

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
LiteLLM Proxy
   │
   ▼
vLLM
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

Raison : plus stable pour les cas de tool calling longs que `qwen3_coder` dans les retours terrain cités.

### 3. Proxy

Le repo garde **LiteLLM** comme couche d'adaptation entre l'interface attendue par Claude Code et l'API servie par vLLM.

### 4. MCP

Recommandation : commencer avec **2 MCP seulement** :

- `filesystem`
- `playwright`

Puis n'ajouter le reste qu'en cas de besoin réel.

### 5. Skills

Les skills servent à déplacer la logique répétitive hors des prompts ponctuels.

Le repo inclut 4 skills de base :

- `feature-dev`
- `write-tests`
- `debug-loop`
- `git-workflow`

## Limites connues

- Le comportement exact varie selon la version de Claude Code, LiteLLM et vLLM.
- Les modèles locaux restent plus fragiles que des modèles frontière pour les tâches très longues.
- Plus le nombre de MCP actifs augmente, plus le contexte grossit et moins l'expérience est fluide.

## API HTTP

Le dépôt inclut désormais une API FastAPI exposée sur le port `8080`.

Cette couche sert à :

- fournir un point d'entrée REST simple pour une UI ou un script
- centraliser le modèle, le prompt système et les timeouts
- garder la compatibilité avec un upstream Anthropic-compatible via LiteLLM
