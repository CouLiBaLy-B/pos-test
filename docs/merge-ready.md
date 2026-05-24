# Merge-ready plan pour `feat/sans-litellm`

## Objectif

Préparer un merge propre vers `develop` avec un périmètre clair, des tests verts et une documentation alignée.

## Contenu couvert par la branche

- intégration directe `Claude Code -> vLLM`
- suppression de LiteLLM dans le runtime par défaut
- Assistant API enrichie avec :
  - endpoint REST `/api/v1/chat`
  - streaming SSE `/api/v1/chat/stream`
  - compatibilité Anthropic `/v1/messages`
  - endpoint `/v1/messages/count_tokens`
  - interface web minimale `/`
- sandbox Docker simple `assistant-sandbox` pour l'exécution isolée de commandes

## Checklist avant merge

- [x] CI verte
- [x] tests locaux verts
- [x] README mis à jour
- [x] docs API mises à jour
- [x] audit technique rédigé
- [x] PR ouverte contre `develop`

## Recommandation de merge

1. Review de la PR de branche feature vers `develop`
2. Validation manuelle sur la machine cible RTX 4090
3. Merge squash recommandé pour garder un historique lisible
4. Smoke test après merge sur `develop`

## Smoke tests suggérés

```bash
make up
make health
curl http://localhost:8080/healthz
curl http://localhost:8080/api/v1/config
curl -X POST http://localhost:8080/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Dis bonjour"}'
```

## Notes PR

La PR associée doit mentionner explicitement :

- la suppression de LiteLLM sur cette branche
- le nouveau nom servi `claude-sonnet-local`
- les nouveaux endpoints SSE et Anthropic-compatible
