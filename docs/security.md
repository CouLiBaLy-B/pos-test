# Sécurité

## Principes de base

- ne jamais commiter de token, mot de passe ou clé privée
- préférer `.env` non versionné
- limiter les permissions des outils
- isoler l'exécution du code généré quand c'est possible

## Recommandation forte

Pour les workflows agentiques exécutant du code généré, préférer une isolation plus forte qu'un conteneur standard quand c'est faisable :

- microVM / sandbox dédiée
- réseau filtré
- workspace monté explicitement

## GitHub tokens

Si un token a été partagé dans un chat, un terminal enregistré, une capture d'écran ou un commit :

1. le **révoquer immédiatement**
2. en générer un nouveau
3. réduire son scope au strict minimum
4. privilégier un token à durée de vie courte ou un mécanisme plus sûr
