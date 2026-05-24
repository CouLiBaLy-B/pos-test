# API de l'assistant

Cette API expose un point d'entrée HTTP simple pour dialoguer avec l'assistant local sans passer directement par Claude Code.

## Objectif

Permettre à une application web, un script shell ou un autre service local d'envoyer des messages à l'assistant via une interface REST.

## Service

Par défaut, le service est exposé sur :

- `http://localhost:8080`
- interface web minimale : `http://localhost:8080/`
- documentation OpenAPI : `http://localhost:8080/docs`

## Endpoints

### `GET /healthz`

Retourne l'état de l'API.

### `GET /api/v1/config`

Retourne la configuration runtime utile :

- endpoint upstream
- modèle par défaut
- nombre de tokens par défaut

### `POST /api/v1/chat`

Permet d'envoyer un prompt unique ou un historique de messages.

### `POST /api/v1/chat/stream`

Retourne un flux SSE relayant les événements Anthropic renvoyés par vLLM.

### `POST /v1/messages`

Endpoint Anthropic-compatible utile pour brancher d'autres clients locaux ou tester la passerelle.

### `POST /v1/messages/count_tokens`

Compte les tokens d'entrée. Si l'upstream n'implémente pas cet endpoint, l'API renvoie un fallback approximatif.

#### Exemple minimal

```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique-moi comment démarrer ce projet"
  }'
```

#### Exemple conversation

```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "system": "Tu es un assistant de codage concis.",
    "messages": [
      {"role": "user", "content": "Résume l\u0027architecture du dépôt."},
      {"role": "assistant", "content": "Le dépôt orchestre Claude Code et vLLM."},
      {"role": "user", "content": "Ajoute les prochaines étapes."}
    ],
    "max_tokens": 512,
    "temperature": 0.2
  }'
```

## Variables d'environnement

- `ASSISTANT_API_PORT` : port exposé localement, défaut `8080`
- `ASSISTANT_UPSTREAM_BASE_URL` : endpoint Anthropic-compatible cible, défaut `http://vllm:8000` en Docker
- `ASSISTANT_AUTH_TOKEN` : bearer token envoyé à l'upstream
- `ASSISTANT_API_KEY` : header `x-api-key` envoyé à l'upstream
- `ASSISTANT_MODEL` : modèle par défaut
- `ASSISTANT_DEFAULT_MAX_TOKENS` : limite par défaut pour `/api/v1/chat`
- `ASSISTANT_REQUEST_TIMEOUT` : timeout HTTP vers l'upstream
- `ASSISTANT_SYSTEM_PROMPT` : prompt système global optionnel
- `ASSISTANT_ANTHROPIC_VERSION` : version d'API Anthropic transmise, défaut `2023-06-01`

## Interface web minimale

Le endpoint racine `/` sert une petite UI HTML/JS sans dépendances externes.

Elle permet de :

- saisir un prompt système
- chatter en mode standard
- chatter en mode streaming SSE
- visualiser la configuration runtime
