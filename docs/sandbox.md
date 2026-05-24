# Sandbox Docker simple

Cette branche inclut une **sandbox d'exécution Docker simple** pour isoler les commandes de développement du poste hôte sans ajouter une microVM complète.

## Ce que fait la sandbox

Le service `assistant-sandbox` :

- monte le dépôt dans `/workspace`
- exécute les commandes avec le **même UID/GID que l'utilisateur hôte** pour éviter les fichiers root-owned
- fournit un shell Linux minimal pour exécuter des commandes
- inclut les outils courants : `bash`, `python3`, `pip`, `node`, `npm`, `git`, `jq`, `ripgrep`, `fd`, `make`, `curl`
- sert de zone d'exécution pratique pour tests, scripts et commandes ponctuelles

## Ce que la sandbox ne fait pas

- elle ne remplace pas encore complètement Claude Code lui-même
- elle ne fournit pas l'isolation forte d'une microVM
- elle partage toujours le kernel hôte via Docker
- elle reste une isolation pragmatique, pas une sandbox durcie type microVM

## Permissions et sécurité

La sandbox applique quelques garde-fous simples :

- exécution en **utilisateur non-root** via `user: HOST_UID:HOST_GID`
- `no-new-privileges:true`
- `cap_drop: [ALL]`
- `tmpfs: /tmp`
- `HOME=/tmp`

Les scripts `sandbox-*` injectent automatiquement `HOST_UID=$(id -u)` et `HOST_GID=$(id -g)` pour conserver des permissions cohérentes sur les fichiers du workspace.

## Service Docker

Le service est défini avec le profil Compose `sandbox`, ce qui évite de le démarrer systématiquement avec `make up`.

## Commandes utiles

### Démarrer la sandbox

```bash
make sandbox-up
```

### Ouvrir un shell interactif

```bash
make sandbox-shell
```

### Lancer une commande dans la sandbox

```bash
make sandbox-run CMD="python3 --version && node --version"
```

### Lancer les tests dans la sandbox

```bash
make sandbox-test
```

### Arrêter la sandbox

```bash
make sandbox-down
```

## Exemple de workflow

```bash
make sandbox-up
make sandbox-run CMD="python3 -m pip install -r requirements-dev.txt"
make sandbox-run CMD="pytest -q"
make sandbox-shell
```

## Claude Code en mode sandbox-first

Le projet peut lancer Claude Code avec :

```bash
make claude-sandbox
```

Ce wrapper :

- démarre la sandbox si nécessaire
- lance `claude`
- s'appuie sur `config/claude/settings.json` pour n'autoriser côté Bash que les wrappers `sandbox-*`

En pratique, cela signifie que Claude Code doit utiliser par défaut :

- `./scripts/sandbox-up.sh`
- `./scripts/sandbox-run.sh`
- `./scripts/sandbox-test.sh`
- `./scripts/sandbox-shell.sh`
- `./scripts/sandbox-down.sh`

et non des commandes host directes comme `python`, `pytest`, `npm`, `node`, `make` ou `git`.
