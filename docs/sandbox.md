# Sandbox Docker simple

Cette branche inclut une **sandbox d'exécution Docker simple** pour isoler les commandes de développement du poste hôte sans ajouter une microVM complète.

## Ce que fait la sandbox

Le service `assistant-sandbox` :

- monte le dépôt dans `/workspace`
- fournit un shell Linux minimal pour exécuter des commandes
- inclut les outils courants : `bash`, `python3`, `pip`, `node`, `npm`, `git`, `jq`, `ripgrep`, `fd`, `make`, `curl`
- sert de zone d'exécution pratique pour tests, scripts et commandes ponctuelles

## Ce que la sandbox ne fait pas

- elle ne remplace pas encore complètement Claude Code lui-même
- elle ne fournit pas l'isolation forte d'une microVM
- elle partage toujours le kernel hôte via Docker

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
