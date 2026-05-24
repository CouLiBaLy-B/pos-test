# Assistant codeur local — Claude Code + LiteLLM + vLLM

[![CI](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/ci.yml/badge.svg)](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/ci.yml) [![Release](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/release.yml/badge.svg)](https://github.com/CouLiBaLy-B/pos-test/actions/workflows/release.yml)

Stack locale pour exécuter un assistant de codage **privé** sur une machine NVIDIA (cible principale : **RTX 4090 24 Go**) avec :

- **Claude Code** comme interface agentique
- **LiteLLM** comme proxy de traduction/routage
- **vLLM** comme serveur d'inférence local
- **Qwen3-Coder-30B-A3B-Instruct-AWQ** comme modèle recommandé
- **MCP minimal** pour limiter la consommation de tokens
- **Skills** pour les workflows répétitifs

> Objectif : obtenir un environnement de codage local, raisonnablement rapide, compatible avec des workflows agentiques, sans envoyer le code vers une API distante.

## Architecture

```text
Claude Code / IDE
        │
        ▼
Anthropic Messages API
        │
        ▼
LiteLLM Proxy (:4000)
        │
        ▼
vLLM Server (:8000)
        │
        ▼
Qwen3-Coder-30B-A3B-Instruct-AWQ
```

## Pourquoi ce choix

- **Modèle recommandé** : `Qwen/Qwen3-Coder-30B-A3B-Instruct-AWQ`
- **Parser d'outils recommandé** : `qwen3_xml`
- **Proxy recommandé** : LiteLLM, tant que votre stack Claude Code attend un endpoint compatible Anthropic
- **Contrainte principale** : garder peu de MCP actifs pour éviter le coût contexte/tokens

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
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── Makefile
├── docker-compose.yml
├── requirements-dev.txt
├── CHANGELOG.md
├── config/
│   ├── claude/settings.json
│   └── litellm/config.yaml
├── docs/
│   ├── architecture.md
│   ├── models.md
│   └── security.md
├── scripts/
│   ├── bootstrap.sh
│   ├── healthcheck.sh
│   ├── run-tests.sh
│   ├── apply-branch-protection.sh
│   ├── setup-claude.sh
│   ├── start.sh
│   └── stop.sh
├── tests/
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

Éditez ensuite les variables si nécessaire.

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

### 6. Utiliser Claude Code

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=sk-local-dummy
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
claude
```

## Commandes utiles

```bash
make up            # démarre vLLM + LiteLLM
make down          # arrête la stack
make restart       # redémarre
make logs          # affiche les logs
make health        # vérifie les endpoints
make setup-claude  # installe settings + skills dans ~/.claude
make test          # lance les tests et validations locales
make protect-branch # applique la protection GitHub sur main
```

## Gouvernance GitHub

Le dépôt inclut maintenant :

- `CODEOWNERS` pour imposer un propriétaire par défaut
- des templates d'issues Bug / Feature
- un template de pull request
- un script `scripts/apply-branch-protection.sh` pour rejouer la configuration de protection de branche

Exemple :

```bash
GITHUB_TOKEN=ghp_xxx make protect-branch
```

Protection prévue pour `main` :

- pull requests obligatoires
- 1 review minimum
- code owner review requise
- branche linéaire
- résolution des conversations requise
- force-push et suppression interdits

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

La CD publie une archive du projet lors d'un tag `v*` ou via déclenchement manuel.

## Notes importantes

- Ce repo **ne stocke aucun secret**.
- Le token GitHub ne doit pas être commité, ni placé en dur dans des scripts.
- Si vous avez partagé un token dans une conversation, **révoquez-le et recréez-en un nouveau**.
- Le repo contient une config **pragmatique** pour démarrer ; adaptez les limites mémoire/contexte à votre machine.

## Suite logique

1. Lancer la stack.
2. Tester un prompt simple dans Claude Code.
3. Activer seulement les MCP vraiment nécessaires.
4. Ajuster les skills à votre workflow de dev.

