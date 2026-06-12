---
name: Prompting Claude Code HF — Apprentissage progressif
description: Ce fichier documente ce qui fonctionne et ce qui ne fonctionne pas lors de la communication avec Claude Code HF via CloudCLI Chat. A LIRE avant chaque interaction.
type: feedback
originSessionId: d608dca0-6798-40a0-adff-59bb352829f3
---
## Contexte

**Claude Code HF** = instance Claude Code CLI tournant dans CloudCLI sur le HF Space `vmu7235/2.0claude-kimi-hf-space`.
- UI : CloudCLI v1.32.0 (tabs Chat / Shell / Files / Source Control)
- Backend : Claude Code CLI v2.1.140 avec validation client-side du model name
- Terminal : xterm.js avec rendu Canvas (DOM extraction impossible, screenshots obligatoires)
- Claude Code CLI dans Shell tab : peut executer des commandes shell via `!command`

---

## Regles d'or (apprises a ce jour)

### 1. Ce qui fonctionne pour faire repondre Claude Code HF
- **Moonshot direct** : `ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic` + `model=claude-3-5-sonnet-20241022` → Chat repond
- **LiteLLM proxy local** : `ANTHROPIC_BASE_URL=http://localhost:4000` + LiteLLM demarre avec config correcte → Chat repond
- **Sans backend** : Chat bloque en "Processing" (timeout API) — comportement normal, pas un bug UI

### 2. Ce qui ne fonctionne PAS
- **Here-doc `<< 'EOF'`** dans CloudCLI Shell → cree des fichiers VIDES. Toujours utiliser `echo '...' > file` en une seule ligne.
- **Taper des commandes sans `!`** dans une session Claude Code CLI active → interprete comme un message utilisateur, pas une commande shell.
- **Claude Code CLI en retry** : quand il affiche "Unable to connect to API (ConnectionRefused)", les commandes `!` sont mises en file d'attente (queued). Il faut attendre la fin du retry (10 attempts) ou interrompre avec Escape.
- **Dom extraction xterm.js** : `document.querySelector('.xterm-rows')` retourne vide (Canvas rendering). Seuls les screenshots sont fiables.

### 3. Patterns de prompts efficaces avec Claude Code HF (Chat tab)

#### Structure recommandee
1. **Contexte court** : "Tu es dans un container HF Space."
2. **Instruction claire et atomique** : une seule action par message quand possible.
3. **Commandes exactes** : fournir les commandes shell litterales a executer.
4. **Demander le resultat** : "Rapporte le output exact de chaque commande."

#### Exemple de prompt fonctionnel (a valider)
```
Tu es dans un container HF Space. Verifie si le fichier /workspace/litellm_config.yaml existe et affiche son contenu.
!cat /workspace/litellm_config.yaml
Rapporte le resultat exact.
```

### 4. Fallback / changement de provider — PROTOCOLE DE SECURITE

**JAMAIS de changement direct sans test prealable.**

Protocole :
1. **Demander a Claude de TESTER d'abord** la nouvelle config sans l'activer
2. **Verifier avec `curl`** que le nouveau endpoint repond
3. **Preuve irréfutable** : screenshot du test curl OK avant changement
4. **Rollback immediat pret** : sauvegarder l'ancienne config avant modification
5. **Activer le changement** uniquement apres preuve de fonctionnement
6. **Verifier apres changement** : envoyer "Bonjour" et confirmer la reponse < 10s

### 5. Gestion de la memoire de Claude Code HF

Claude Code HF (comme tout LLM) devient moins performant quand le contexte est trop long.

**Strategies :**
- **Messages concis** : eviter les prompts de 500+ lignes. Decouper en etapes.
- **Resumer le contexte** : si une nouvelle session est necessaire, commencer par un resume de 5-10 lignes.
- **Nouvelle session** : quand la conversation depasse ~10-15 echanges, creer une nouvelle session CloudCLI avec le contexte resume.
- **Eviter les historiques inutiles** : ne pas laisser trainer des sessions bloquees ou sans reponse.

---

## Journal d'apprentissage (mettre a jour apres CHAQUE interaction)

### 2026-05-15 — Session initiale
- Le Chat tab fonctionne quand le backend API est accessible (preuve 22:34:32).
- Le Chat tab bloque en "Processing" quand le backend est down (comportement normal).
- `ConnectionRefused` = Claude Code CLI pointe vers localhost:4000 mais LiteLLM n'est pas demarre.
- Les commandes `!` dans Shell sont queued quand Claude Code CLI est en retry.
- Escape n'interrompt pas toujours le retry immediatement.

### [A REMPLIR apres chaque nouvelle interaction]
- Date :
- Ce qui a fonctionne :
- Ce qui n'a pas fonctionne :
- Nouvelle regle deduite :
- Prompt utilise (resume) :
- Reponse de Claude Code HF (resume) :

---

## Checklist avant de prompter Claude Code HF

- [ ] Lire ce fichier de memoire pour appliquer les dernieres lecons
- [ ] S'assurer que le backend API est accessible (Moonshot direct ou LiteLLM demarre)
- [ ] Formuler un prompt court, clair, avec commandes exactes
- [ ] Si changement de provider : prevoir un test + rollback
- [ ] Prevoir la prise de screenshot comme preuve
- [ ] Si la conversation est longue : resumer ou nouvelle session
