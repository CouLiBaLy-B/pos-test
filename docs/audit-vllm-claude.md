# Audit vLLM + Claude Code

## Objet

Audit de la branche `feat/sans-litellm` pour aligner le code avec une intégration directe **Claude Code → vLLM**.

## Constats corrigés

### 1. Incohérence de branche

La branche s'appelait `sans-litellm` mais la stack active passait encore par LiteLLM.

**Correction** : suppression de LiteLLM de `docker-compose.yml` et des réglages runtime par défaut.

### 2. Nom de modèle servi fragile

Le nom servi `qwen3-coder` n'était pas aligné avec la découverte de modèles côté Claude Code.

**Correction** : adoption de `claude-sonnet-local` comme `served-model-name`.

### 3. Réglages Claude Code non robustes

La config utilisait `ANTHROPIC_MODEL` et forçait `ENABLE_TOOL_SEARCH=true` malgré un backend non first-party.

**Correction** :

- bascule vers `ANTHROPIC_DEFAULT_*_MODEL`
- activation de la gateway discovery
- `ENABLE_TOOL_SEARCH=false` par défaut

### 4. Assistant API trop dépendante de LiteLLM

L'API FastAPI pointait vers LiteLLM et utilisait une stratégie d'auth insuffisamment compatible.

**Correction** :

- upstream direct vers vLLM
- normalisation de base URL
- envoi de `Authorization: Bearer` et `x-api-key`
- meilleure gestion des erreurs réseau

### 5. Validation incomplète des requêtes API

Une requête contenant seulement des messages `system` pouvait passer la validation locale puis échouer plus loin.

**Correction** : validation stricte d'au moins un message `user`/`assistant` ou d'un `prompt`.

## Recommandations restantes

- tester le backend réel avec le modèle choisi sur la machine cible
- vérifier le comportement tool use en conditions longues
- n'activer `ENABLE_TOOL_SEARCH=true` qu'après validation explicite du backend vLLM utilisé
