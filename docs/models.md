# Notes sur les modèles

## Modèle par défaut

### Qwen3-Coder-30B-A3B-Instruct-AWQ

Pourquoi il est choisi ici :

- tient dans une enveloppe compatible avec une RTX 4090 24 Go avec quantification adaptée
- suffisamment bon pour du refactor, génération de fichiers, tests et itérations agentiques
- bon compromis pour une stack locale sérieuse

## Paramètres vLLM retenus

- `--enable-auto-tool-choice`
- `--tool-call-parser qwen3_xml`
- `--enable-prefix-caching`
- `--enable-chunked-prefill`
- `--max-model-len 65536`
- `--gpu-memory-utilization 0.90`
- `--dtype float16`

## Quand changer de modèle

Changez si :

- vous manquez de VRAM
- vous ciblez surtout de la complétion simple plutôt que du tool use
- vous voulez un contexte plus long ou une latence différente

## Rappel pratique

Si les appels d'outils échouent silencieusement :

1. vérifier le parser
2. vérifier que le modèle gère bien le tool calling
3. réduire la complexité du prompt
4. désactiver des MCP inutiles
