---
name: skill-master
version: 1.0.0
description: "Skill maître d'auto-sélection. Contient la matrice de tous les skills installés et les mots-clés de déclenchement. Claude Code doit consulter cette matrice AVANT chaque réponse technique pour identifier et appliquer le skill le plus pertinent."
triggers:
  - phrase: "/skill"
  - phrase: "utilise le skill"
  - phrase: "quel skill"
  - phrase: "auto-skill"
---

# Skill Master — Matrice d'auto-sélection

## Instruction système
Avant chaque réponse technique dans ce projet, consulte cette matrice. Si la demande de l'utilisateur correspond à un ou plusieurs skills ci-dessous, applique les règles de ce(s) skill(s) **automatiquement** sans demander confirmation.

---

## Matrice des skills (mots-clés → skill)

| Mots-clés / Contexte | Skill à appliquer | Fichier |
|---|---|---|
| présentation, slides, marp, deck, diapositive | **marp-slides** | `.claude/skills/marp-slides/SKILL.md` |
| logo, branding, identité visuelle, générer un logo | **logo-generator-skill** | `.claude/skills/logo-generator-skill/SKILL.md` |
| design system, couleurs, typographie, theme, UI kit | **hue** | `.claude/skills/hue/SKILL.md` |
| figure scientifique, graphique publication, papier recherche, schéma académique | **engineering-figure-banana** | `.claude/skills/engineering-figure-banana/SKILL.md` |
| animation, vidéo, motion graphics, seedance | **seedance-skill** | `.claude/skills/seedance-skill/SKILL.md` |
| installer skill, auto-install, setup skills | **autoskills** | `.claude/skills/autoskills/SKILL.md` |
| architecture, explique le code, comment ça marche, critique design | **how** | `.claude/skills/how/SKILL.md` |
| structure projet, générer skill projet, conventions codebase | **skill-based-architecture** | `.claude/skills/skill-based-architecture/SKILL.md` |
| explique ce code, pourquoi AI a écrit, apprendre, deep dive | **antivibe** | `.claude/skills/antivibe/SKILL.md` |
| spec-driven, SDD, spécifications, plan avant code | **manual-SDD** | `.claude/skills/manual-sdd/SKILL.md` |
| SEO, référencement, audit site, optimiser Google | **agentic-seo** | `.claude/skills/agentic-seo/SKILL.md` |
| papier scientifique, recherche académique, arxiv, trouver article | **paper-finder** | `.claude/skills/paper-finder/SKILL.md` |
| télécom, 5G, 6G, 3GPP, réseau mobile, GSM | **3gpp-skill** | `.claude/skills/3gpp-skill/SKILL.md` |
| scraper, extraire données, reverse engineering, spider | **spider-king-skill** | `.claude/skills/spider-king-skill/SKILL.md` |
| organisation personnelle, vault, obsidian, résumé vidéo | **ai-life-skills** | `.claude/skills/ai-life-skills/SKILL.md` |
| assistant IA, showcase, exemple assistant, friday | **friday-showcase** | `.claude/skills/friday-showcase/SKILL.md` |
| équipe agents, agent team, orchestration, harness | **harness** | `.claude/skills/harness/SKILL.md` |
| interface skills, UI skills, npx skillui | **npxskillui** | `.claude/skills/npxskillui/SKILL.md` |
| évolution skill, améliorer skill, skill claw | **SkillClaw** | `.claude/skills/skillclaw/SKILL.md` |

| brainstormer, concevoir, design fonctionnalité, avant de coder | **brainstorming** | `.claude/skills/brainstorming/SKILL.md` |
| agents parallèles, dispatcher, paralléliser | **dispatching-parallel-agents** | `.claude/skills/dispatching-parallel-agents/SKILL.md` |
| exécuter plan, suivre le plan | **executing-plans** | `.claude/skills/executing-plans/SKILL.md` |
| terminer branche, finir feature, merger | **finishing-a-development-branch** | `.claude/skills/finishing-a-development-branch/SKILL.md` |
| recevoir review, répondre review | **receiving-code-review** | `.claude/skills/receiving-code-review/SKILL.md` |
| demander review, code review | **requesting-code-review** | `.claude/skills/requesting-code-review/SKILL.md` |
| développement par sous-agents | **subagent-driven-development** | `.claude/skills/subagent-driven-development/SKILL.md` |
| debug, déboguer, bug mystérieux, diagnostic | **systematic-debugging** | `.claude/skills/systematic-debugging/SKILL.md` |
| TDD, test d'abord, test-driven | **test-driven-development** | `.claude/skills/test-driven-development/SKILL.md` |
| worktree, branches parallèles git | **using-git-worktrees** | `.claude/skills/using-git-worktrees/SKILL.md` |
| superpowers, quels skills process | **using-superpowers** | `.claude/skills/using-superpowers/SKILL.md` |
| vérifier avant de finir, verification complète | **verification-before-completion** | `.claude/skills/verification-before-completion/SKILL.md` |
| écrire un plan, plan d'implémentation | **writing-plans** | `.claude/skills/writing-plans/SKILL.md` |
| écrire un skill, créer skill | **writing-skills** | `.claude/skills/writing-skills/SKILL.md` |

---

## Règles d'application

1. **Détection automatique** : Si la demande contient un ou plusieurs mots-clés de la colonne 1, charge le skill correspondant et applique ses règles.
2. **Combinaison** : Si plusieurs skills correspondent (ex: "crée un logo pour ma présentation" → logo-generator + marp-slides), combine leurs instructions.
3. **Défaut** : Si aucun skill ne correspond, réponds normalement sans forcer l'utilisation d'un skill.
4. **Signalement** : Après avoir appliqué un skill, mentionne brièvement : *"[Skill actif : marp-slides]"* pour que l'utilisateur sache quel skill est en cours.

## Fichiers disponibles dans `.claude/skills/`

- 3gpp-skill/SKILL.md
- agentic-seo/SKILL.md
- ai-life-skills/SKILL.md
- antivibe/SKILL.md
- autoskills/SKILL.md
- brainstorming/SKILL.md
- dispatching-parallel-agents/SKILL.md
- engineering-figure-banana/SKILL.md
- executing-plans/SKILL.md
- finishing-a-development-branch/SKILL.md
- friday-showcase/SKILL.md
- harness/SKILL.md
- how/SKILL.md
- hue/SKILL.md
- logo-generator-skill/SKILL.md
- manual-sdd/SKILL.md
- marp-slides/SKILL.md
- npxskillui/SKILL.md
- paper-finder/SKILL.md
- receiving-code-review/SKILL.md
- requesting-code-review/SKILL.md
- seedance-skill/SKILL.md
- skill-based-architecture/SKILL.md
- skillclaw/SKILL.md
- spider-king-skill/SKILL.md
- subagent-driven-development/SKILL.md
- systematic-debugging/SKILL.md
- test-driven-development/SKILL.md
- using-git-worktrees/SKILL.md
- using-superpowers/SKILL.md
- verification-before-completion/SKILL.md
- writing-plans/SKILL.md
- writing-skills/SKILL.md
