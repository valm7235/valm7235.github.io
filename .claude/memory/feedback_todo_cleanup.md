---
name: Nettoyage systématique de la todo list en fin de projet
description: L'utilisateur exige que je vide ou mette à jour la todo list (TodoWrite) dès qu'un projet est terminé, pour garder le plan de travail propre.
type: feedback
originSessionId: 56816441-2bd2-42a0-ad40-e76ff079e08e
---
**Règle :** Dès qu'un projet ou une tâche complexe est terminée, je DOIS nettoyer la todo list en la vidant ou en ne gardant que les tâches réellement en cours. Pas de todo list sale ou obsolète entre les projets.

**Why:** L'utilisateur a demandé explicitement : "Prenez note à partir de maintenant de toujours nettoyer votre plan de travail quand vous avez terminé un projet."

**How to apply:**
- À la fin de chaque projet / tâche multi-étapes : appeler `TodoWrite` avec une liste vide `[]` ou mise à jour
- Ne pas laisser de tâches "pending" ou "in_progress" obsolètes dans la liste
- Si une nouvelle tâche démarre immédiatement après, remplacer la liste par les nouvelles tâches plutôt que d'accumuler
