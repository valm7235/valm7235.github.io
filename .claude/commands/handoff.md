# /handoff

Met à jour le système de passation durable du projet HF avant chaque fin de session ou changement de discussion.

---

## Quand utiliser

- Avant de quitter une session de travail sur le projet HF.
- Après avoir terminé une tâche significative (fix, test, validation).
- Avant de passer à un autre sujet.
- À la demande explicite de l'utilisateur.

---

## Instructions d'exécution

### Étape 1 — Lire l'état actuel
Lis les fichiers de passation existants :
- `C:\Users\valm7\claude-kimi-test\HF_CLOUD_PASSATION_NEXT.md`
- `C:\Users\valm7\claude-kimi-test\NEXT_ACTION.md`
- `C:\Users\valm7\claude-kimi-test\EVIDENCE_INDEX.md`

### Étape 2 — Analyser le travail effectué durant cette session
Identifie :
- Ce qui a été fait (avec preuves : screenshots, logs, commits)
- Ce qui a échoué (avec diagnostic)
- Ce qui a été décidé (architectural, stratégique)
- Ce qui reste bloqué

### Étape 3 — Mettre à jour HF_CLOUD_PASSATION_NEXT.md
Met à jour les sections suivantes :
- **Date de passation** (date/heure actuelle)
- **État actuel réel** (tableau critères)
- **Ce qui a été fait** (cases à cocher)
- **Problèmes rencontrés** (nouveaux ou mis à jour)
- **Fixes appliqués** (nouveaux ou mis à jour)
- **Phase 3 restante** (cases à cocher)
- **Ce qui reste à faire précisément** (liste numérotée)

Règles strictes :
- Ne jamais inventer de preuve.
- Si une preuve est retrouvée : mentionner le fichier/commit/screenshot.
- Si elle n'est pas retrouvée : marquer "À VÉRIFIER".
- Si ce n'est pas fait : marquer "NON FAIT".
- Ne pas modifier la section "Tokens et secrets" sauf si l'utilisateur le demande explicitement.

### Étape 4 — Mettre à jour NEXT_ACTION.md
Remplace le contenu par la prochaine action exacte :
- Maximum 10 lignes.
- Action concrète, vérifiable, sans ambiguïté.
- Doit inclure la méthode de vérification (quoi constitue un succès).

### Étape 5 — Mettre à jour EVIDENCE_INDEX.md
Pour chaque élément du projet, classer :
- **PROUVÉ** : preuve retrouvée et vérifiable (screenshot, log, commit, URL)
- **À VÉRIFIER** : preuve manquante, obsolète, ou nécessitant revalidation
- **NON FAIT** : non encore réalisé

Ajouter les nouvelles preuves découvertes durant la session avec leur localisation exacte.

### Étape 6 — Générer le mini-prompt de reprise
Dans `HF_CLOUD_PASSATION_NEXT.md`, section 15, régénérer le mini-prompt en incluant :
- L'état actuel synthétisé (3-4 lignes)
- La prochaine étape claire
- Les tokens et URLs nécessaires
- Le rappel d'utiliser `/handoff`
- L'interdiction de rapport final avant 100%

### Étape 7 — Validation finale
Avant de finir, vérifier :
- [ ] Aucune preuve inventée
- [ ] Aucun token tronqué ou modifié sans autorisation
- [ ] NEXT_ACTION.md a maximum 10 lignes
- [ ] EVIDENCE_INDEX.md utilise uniquement PROUVÉ / À VÉRIFIER / NON FAIT
- [ ] Le mini-prompt est complet et fonctionnel

### Étape 8 — Répondre à l'utilisateur
Répondre avec :
- Date et heure de la passation
- Résumé des mises à jour effectuées
- Prochaine action confirmée
- Nombre de preuves PROUVÉ / À VÉRIFIER / NON FAIT

---

## Règles absolues

1. **Ne jamais inventer de preuve.** Si tu n'as pas vu le screenshot, le log ou le commit, c'est "À VÉRIFIER".
2. **Interdiction de rapport final** tant que 100% des critères du `HF_CLONE_HANDOFF.md` ne sont pas validés PROUVÉ.
3. **Un seul critère échoue = STOP.** Ne pas passer à l'étape suivante sans preuve.
4. **Ne pas modifier le setup Windows local.** Ce projet est cloud-only.
5. **Ne pas pousser, ne pas déployer** lors de la mise à jour de la passation (sauf si l'action elle-même est un push/déploiement).
6. **Conserver les tokens complets** tels qu'ils figurent dans le fichier existant, sauf instruction explicite de l'utilisateur.

---

## Format de réponse attendu

```
Passation mise à jour le [DATE] à [HEURE].

Fichiers modifiés :
- HF_CLOUD_PASSATION_NEXT.md
- NEXT_ACTION.md
- EVIDENCE_INDEX.md

Résumé des changements :
- [Ce qui a changé]

Preuves :
- PROUVÉ : [N] | À VÉRIFIER : [N] | NON FAIT : [N]

Prochaine action :
[Action de NEXT_ACTION.md]
```
