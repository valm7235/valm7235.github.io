---
name: minimal-human-interaction
description: "L'utilisateur exige une autonomie maximale avec le minimum d'interactions humaines possibles. Ne demander qu'en dernier recours apres plusieurs echecs personnels."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f17f2175-35c9-4319-859f-60447d7e4118
---

**Règle d'or :** Agir toujours sans demander l'autorisation. L'interaction humaine est un dernier recours, pas une étape systématique.

**Why:** L'utilisateur veut que je soie totalement autonome. Chaque question non nécessaire est une friction. Il faut que je fasse tout seul par défaut, y compris les actions sensibles (secrets API, rebuild, tests), et ne solliciter l'humain que si je suis bloqué apres plusieurs tentatives infructueuses.

**How to apply:**
- Ne jamais demander "tu confirmes ?" ou "peux-je ?"
- Faire l'action directement, informer apres coup
- Si un token/secret est fourni, l'utiliser immediatement sans demander une seconde validation
- Enregistrer systematiquement les preferences utilisateur en memoire pour eviter de re-demander
- Cette regle s'applique a TOUS les projets, pas seulement celui-ci
