---
name: debug-loop
description: Utiliser ce skill quand un bug, une erreur runtime, un test cassé ou une régression doit être investigué méthodiquement.
---

# Debug Loop

## Boucle recommandée

1. reproduire le problème
2. isoler le point de défaillance
3. formuler une hypothèse unique
4. appliquer une correction minimale
5. relancer le test ou la reproduction
6. confirmer qu'aucune régression évidente n'est introduite

## Règles

- ne pas appliquer 5 changements à la fois
- privilégier les preuves (logs, tests, stacktrace)
- documenter la cause racine quand elle est claire
