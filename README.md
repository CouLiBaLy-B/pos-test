# Assistant codeur local — Claude Code + vLLM (branche sans LiteLLM)

[![CI](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/ci.yml/badge.svg)](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/ci.yml) [![Release](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/release.yml/badge.svg)](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/release.yml)

Cette branche `feat/sans-litellm` propose une stack locale pour exécuter un assistant de codage **privé** sur une machine NVIDIA (cible principale : **RTX 4090 24 Go**) avec :

- **Claude Code** comme interface agentique
- **vLLM** comme serveur d'inférence local **Anthropic-compatible**
- **Assistant API** comme API REST locale
- **Qwen3-Coder-30B-A3B-Instruct-AWQ** comme modèle recommandé
- **MCP minimal** pour limiter la consommation de tokens
- **Skills** pour les workflows répétitifs

> Objectif : obtenir un environnement de codage local, raisonnablement rapide, compatible avec des workflows agentiques, sans envoyer le code vers une API distante et sans dépendre de LiteLLM par défaut.

## Architecture

```text
Claude Code / Client HTTP
        │
        ▼
Assistant API (:8080)
        │
        ▼
vLLM Server (:8000)
        │
        ▼
Qwen3-Coder-30B-A3B-Instruct-AWQ
```

## Pourquoi cette variante

- **vLLM implémente l'API Anthropic Messages**, donc Claude Code peut pointer directement dessus
- **moins de composants** à opérer qu'une stack avec proxy supplémentaire
- **moins d'ambiguïtés** entre format Anthropic et format OpenAI
- plus simple à auditer et à déboguer localement

## Structure du repo

```text
.
├── README.md
├── .env.example
├── .gitignore
├── .github/
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── config.yml
│   │   └── feature_request.yml
│   ├── labeler.yml
│   ├── labels.json
│   └── workflows/
│       ├── ci.yml
│       ├── pr-labeler.yml
│       └── release.yml
├── assistant_api/
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── service.py
│   └── static/index.html
├── Dockerfile.sandbox
├── Dockerfile.api
├── Makefile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── CHANGELOG.md
├── config/
│   └── claude/settings.json
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── audit-vllm-claude.md
│   ├── merge-ready.md
│   ├── models.md
│   ├── sandbox.md
│   ├── roadmap-v0.2.0.md
│   └── security.md
├── scripts/
│   ├── bootstrap.sh
│   ├── healthcheck.sh
│   ├── run-tests.sh
│   ├── sandbox-down.sh
│   ├── sandbox-run.sh
│   ├── sandbox-shell.sh
│   ├── sandbox-test.sh
│   ├── sandbox-up.sh
│   ├── apply-branch-protection.sh
│   ├── sync-labels.sh
│   ├── setup-claude.sh
│   ├── start.sh
│   └── stop.sh
├── tests/
│   ├── test_assistant_api.py
│   └── test_repository.py
└── skills/
    ├── debug-loop/SKILL.md
    ├── feature-dev/SKILL.md
    ├── git-workflow/SKILL.md
    └── write-tests/SKILL.md
```

## Démarrage rapide

### 1. Pré-requis

- Linux avec pilotes NVIDIA fonctionnels
- Docker + Docker Compose
- NVIDIA Container Toolkit
- `claude` installé localement
- `git`, `curl`, `jq`
- idéalement `gh`, `rg`, `fd`, `make`

### 2. Copier la config

```bash
cp .env.example .env
```

### 3. Lancer la stack

```bash
make up
```

### 4. Vérifier l'état

```bash
make health
```

### 5. Installer la config Claude Code + Skills

```bash
make setup-claude
```

### 6. Utiliser l'API de l'assistant

Une fois la stack lancée :

```bash
http://localhost:8080/      # Interface web minimale
http://localhost:8080/docs  # OpenAPI / Swagger
```

Exemple rapide :

```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique-moi comment démarrer ce projet"
  }'
```

Streaming SSE :

```bash
curl -N -X POST http://localhost:8080/api/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique-moi la structure"
  }'
```

Passerelle Anthropic-compatible :

```bash
curl -X POST http://localhost:8080/v1/messages \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "claude-sonnet-local",
    "max_tokens": 512,
    "messages": [{"role": "user", "content": "Dis bonjour"}]
  }'
```

### 7. Utiliser Claude Code directement avec vLLM

```bash
export ANTHROPIC_BASE_URL=http://localhost:8000
export ANTHROPIC_AUTH_TOKEN=dummy
export ANTHROPIC_API_KEY=dummy
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-local
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-sonnet-local
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-sonnet-local
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
export ENABLE_TOOL_SEARCH=false
claude
```

## Commandes utiles

```bash
make up             # démarre vLLM + Assistant API
make down           # arrête la stack
make restart        # redémarre
make logs           # affiche les logs
make health         # vérifie les endpoints
make setup-claude   # installe settings + skills dans ~/.claude
make test           # lance les tests et validations locales
make protect-branch # applique la protection GitHub sur la branche ciblée
make sync-labels    # crée ou met à jour les labels GitHub du repo
make sandbox-up     # démarre la sandbox Docker simple
make sandbox-shell  # ouvre un shell dans la sandbox
make sandbox-run    # exécute une commande dans la sandbox
make sandbox-test   # exécute la validation dans la sandbox
make sandbox-down   # arrête la sandbox
```

## Audit et cohérence de la branche

Cette branche est aussi préparée pour être **merge-ready** vers `develop`. Le plan de merge est documenté dans `docs/merge-ready.md`.


Le rapport d'audit est disponible dans `docs/audit-vllm-claude.md`.

Cette branche corrige notamment :

- l'incohérence entre le nom de branche et la stack réellement lancée
- la configuration Claude Code pour un backend non first-party
- le nom de modèle servi pour la découverte côté Claude Code
- la robustesse de l'API HTTP locale

## Gouvernance GitHub

Cette base de dépôt inclut la protection de branches, les fichiers communautaires GitHub et un étiquetage automatique des PR.

### Workflow de branches

Le dépôt suit maintenant un flux simple :

- `main` : branche protégée, stable, orientée release
- `develop` : branche d'intégration protégée
- branches de travail : `feat/...`, `fix/...`, `chore/...` ouvertes en PR vers `develop`

Exemples :

```bash
# protéger develop
GITHUB_BRANCH=develop GITHUB_TOKEN=ghp_xxx make protect-branch

# synchroniser les labels du dépôt
GITHUB_TOKEN=ghp_xxx make sync-labels
```

### Fichiers et automatisations GitHub

Le dépôt inclut maintenant :

- `CODEOWNERS` pour imposer un propriétaire par défaut
- des templates d'issues Bug / Feature
- un template de pull request plus détaillé
- un labeler automatique pour les pull requests
- un catalogue de labels versionné dans `.github/labels.json`
- un script `scripts/apply-branch-protection.sh` pour rejouer la configuration de protection de branche
- des règles de review avec **code owner review** sur les branches protégées

## Tests

Installer les dépendances de test :

```bash
pip install -r requirements-dev.txt
```

Puis lancer la validation locale :

```bash
make test
```

La CI GitHub exécute :

- la syntaxe Bash des scripts
- la validation du `docker-compose.yml`
- la suite `pytest`

## Roadmap

La feuille de route initiale est documentée dans `docs/roadmap-v0.2.0.md`.

## API

La documentation détaillée de l'API est disponible dans `docs/api.md`.

L'API expose maintenant :

- `/api/v1/chat`
- `/api/v1/chat/stream`
- `/v1/messages`
- `/v1/messages/count_tokens`
- `/` pour une interface web minimale

## Sandbox Docker simple

La documentation détaillée de la sandbox est disponible dans `docs/sandbox.md`.

Cette sandbox sert à exécuter des commandes dans un conteneur dédié monté sur `/workspace` sans faire tourner toute la boucle agentique directement sur l'hôte.

## Notes importantes

- Ce repo **ne stocke aucun secret**.
- Le token GitHub ne doit pas être commité, ni placé en dur dans des scripts.
- Si vous avez partagé un token dans une conversation, **révoquez-le et recréez-en un nouveau**.
- Le repo contient une config **pragmatique** pour démarrer ; adaptez les limites mémoire/contexte à votre machine.
