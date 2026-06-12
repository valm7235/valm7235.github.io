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

---

## Règles d'application

1. **Détection automatique** : Si la demande contient un ou plusieurs mots-clés de la colonne 1, charge le skill correspondant et applique ses règles.
2. **Combinaison** : Si plusieurs skills correspondent (ex: "crée un logo pour ma présentation" → logo-generator + marp-slides), combine leurs instructions.
3. **Défaut** : Si aucun skill ne correspond, réponds normalement sans forcer l'utilisation d'un skill.
4. **Signalement** : Après avoir appliqué un skill, mentionne brièvement : *"[Skill actif : marp-slides]"* pour que l'utilisateur sache quel skill est en cours.

## Fichiers disponibles dans `.claude/skills/`

- 3gpp-skill.md
- SkillClaw.md
- agentic-seo.md
- ai-life-skills.md
- antivibe.md
- autoskills.md
- engineering-figure-banana.md
- friday-showcase.md
- harness.md
- how.md
- hue.md
- logo-generator-skill.md
- manual-SDD.md
- marp-slides.md
- npxskillui.md
- paper-finder.md
- seedance-skill.md
- skill-based-architecture.md
- spider-king-skill.md
