---
name: sandbox-first
description: Utiliser ce skill dès qu'une tâche demande d'exécuter une commande, lancer des tests, utiliser git, installer des dépendances ou démarrer un outil local. Exécuter par défaut via la sandbox Docker.
---

# Sandbox First

Quand une tâche nécessite une exécution shell :

1. démarrer la sandbox si nécessaire avec `./scripts/sandbox-up.sh`
2. exécuter la commande via `./scripts/sandbox-run.sh "..."`
3. pour les validations globales, préférer `./scripts/sandbox-test.sh`
4. pour un shell interactif, utiliser `./scripts/sandbox-shell.sh`
5. arrêter la sandbox avec `./scripts/sandbox-down.sh` si demandé

## Règles

- ne pas lancer `python`, `pytest`, `npm`, `node`, `git commit`, `git status`, `make`, ou autres commandes de dev directement sur l'hôte
- préférer la sandbox pour toute commande qui écrit dans le repo ou exécute du code
- les lectures de fichiers se font via les outils de lecture, pas via bash si ce n'est pas nécessaire
- si un accès host est vraiment nécessaire, l'expliquer explicitement avant d'agir

## Exemples

- `./scripts/sandbox-run.sh "git status"`
- `./scripts/sandbox-run.sh "python3 --version"`
- `./scripts/sandbox-run.sh "npm test"`
- `./scripts/sandbox-test.sh`
