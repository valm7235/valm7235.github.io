# Instructions projet

## Skills installés — Utilisation automatique

Ce projet dispose de **19 skills** installés dans `.claude/skills/`.

### Procédure obligatoire avant chaque réponse technique
1. **Consulter le SKILL-MASTER.md** (`.claude/skills/SKILL-MASTER.md`) pour identifier si la demande correspond à un skill.
2. **Si correspondance** : charger le skill identifié et appliquer ses règles **automatiquement**, sans demander confirmation à l'utilisateur.
3. **Si plusieurs correspondances** : combiner les instructions des skills pertinents.
4. **Si aucune correspondance** : répondre normalement.
5. **Signaler** : mentionner brièvement le skill actif en début de réponse (ex: *"[Skill actif : marp-slides]"*).

### Liste des skills disponibles
- **marp-slides** — Présentations MARP
- **logo-generator-skill** — Génération de logos
- **hue** — Design system / tokens visuels
- **engineering-figure-banana** — Figures scientifiques de publication
- **seedance-skill** — Animations et motion graphics
- **autoskills** — Installation automatique de skills
- **how** — Analyse d'architecture de codebase
- **skill-based-architecture** — Génération de skills projet-spécifiques
- **antivibe** — Explications éducatives de code AI
- **manual-SDD** — Spec-Driven Development
- **agentic-seo** — Optimisation SEO automatique
- **paper-finder** — Recherche de papiers scientifiques
- **3gpp-skill** — Expertise télécom 3GPP (5G/6G)
- **spider-king-skill** — Scraping web avancé
- **ai-life-skills** — Organisation personnelle / Obsidian
- **friday-showcase** — Référence assistant IA 24/7
- **harness** — Création d'équipes d'agents IA
- **npxskillui** — Interface graphique de gestion des skills
- **SkillClaw** — Évolution automatique des skills

### Règles d'or
- **Ne jamais ignorer un skill pertinent** — l'utilisateur veut une utilisation automatique et transparente.
- **Ne pas surcharger** — si la tâche est simple et qu'aucun skill n'apporte de valeur, ne pas forcer l'utilisation.
- **Apprentissage continu** — après chaque session, si un nouveau pattern récurrent est identifié, proposer de mettre à jour le SKILL-MASTER.md.
