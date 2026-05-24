# Roadmap v0.2.0

## Objectif

Faire passer le dépôt d'un bootstrap fonctionnel à une base d'équipe plus robuste pour un assistant codeur local orienté production personnelle.

## Priorités

### 1. Expérience développeur

- finaliser le workflow `develop -> main`
- renforcer la revue de code et les conventions de PR
- automatiser l'étiquetage GitHub
- fournir des scripts d'administration du dépôt

### 2. Fiabilité de la stack locale

- ajouter des checks de santé plus complets pour vLLM et l'API locale
- documenter les cas d'échec de tool calling
- ajouter des variantes de configuration selon la VRAM disponible

### 3. Sécurité et isolation

- documenter un mode microVM / sandbox plus détaillé
- réduire encore la surface des permissions Claude Code
- formaliser la rotation des secrets et tokens

### 4. Qualité logicielle

- enrichir les tests de configuration
- ajouter une validation des fichiers GitHub communautaires
- préparer une stratégie de smoke tests non GPU pour CI

## Backlog proposé

- documenter la variante historique avec LiteLLM comme fallback optionnel
- support de modèles alternatifs plus légers
- stack MCP optionnelle par profil (`minimal`, `browser`, `db`)
- guide de troubleshooting RTX 4090
- exemple d'installation sur Ubuntu 24.04

## Définition de terminé

La milestone `v0.2.0` sera considérée comme terminée lorsque :

- `develop` et `main` seront protégées
- les labels GitHub standards seront synchronisés
- la PR template sera suffisamment détaillée pour guider les contributions
- la roadmap et le changelog seront alignés
