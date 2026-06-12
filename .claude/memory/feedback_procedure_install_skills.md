---
name: Procédure obligatoire d'installation de skills
description: Étapes précises et obligatoires à suivre à chaque installation d'un ou plusieurs skills Claude Code. Jamais raccourci, jamais supposé.
type: feedback
originSessionId: 0a148764-db33-4620-8262-ebdeca357610
---
**Règle :** À chaque installation d'un skill (ou d'un lot de skills), exécuter impérativement et dans l'ordre les étapes suivantes. Aucune étape ne doit être sautée.

**Why:** L'utilisateur a exigé explicitement que chaque installation de skill soit traitée avec la même rigueur que ce qui a été fait pour les 19 skills de la vidéo YouTube. Il a insisté sur les tests fonctionnels, la boucle d'auto-correction, et la preuve que tout est opérationnel.

**How to apply:**

### Étape 0 : Vérification de l'architecture existante (en tout premier)
Avant même d'installer un skill, analyser l'architecture actuelle pour garantir qu'elle restera saine après l'installation :
- **Lister les skills déjà installés** : `ls .claude/skills/` et consulter `SKILL-MASTER.md`.
- **Vérifier les conflits de noms** : le nouveau skill ne doit pas écraser un fichier `.md` existant dans `.claude/skills/`.
- **Vérifier les dépendances** : le nouveau skill ne doit pas avoir des dépendances incompatibles avec les skills/outils déjà présents (ex: versions Node/Python conflictuelles).
- **Vérifier la place logique** : le skill doit avoir un nom clair et une description qui ne chevauchent pas un skill existant.
- **Vérifier la taille du contexte** : ajouter trop de skills simultanément peut surcharger le contexte de Claude. Évaluer si une installation par lot est raisonnable.
- **Vérifier le registre** : `SKILL-MASTER.md` doit pouvoir accueillir le nouveau skill sans devenir illisible.
- Si un conflit est détecté : le résoudre AVANT de cloner (renommage, suppression du doublon, ou demande de clarification).

### Étape 1 : Identification des sources
- Récupérer les liens GitHub EXACTS des skills demandés.
- Vérifier que les repos existent réellement avant de cloner.
- Si la source est une vidéo, extraire la description pour obtenir les liens exacts.

### Étape 2 : Clonage
- Créer le dossier `skills/` à la racine du projet si non existant.
- Cloner chaque repo avec `git clone https://github.com/<owner>/<repo>.git`.
- Vérifier que le clone a réussi (dossier présent, fichiers non vides).

### Étape 3 : Détection du fichier skill principal
- Scanner chaque repo cloné pour trouver le fichier skill principal : `SKILL.md`, `skill.md`, `<nom>.skill`, ou `README.md` si aucun skill dédié.
- Identifier si le repo est un skill texte pur ou une application/outil.

### Étape 4 : Copie dans `.claude/skills/`
- Créer `.claude/skills/` si non existant.
- Copier le fichier skill détecté sous `.claude/skills/<nom-du-repo>.md`.
- Si le skill a des références externes (dossier `references/`, images, etc.), les copier aussi.

### Étape 5 : Normalisation du frontmatter YAML
- Vérifier que chaque fichier `.md` dans `.claude/skills/` commence par un frontmatter YAML valide : `---\nname: ...\ndescription: ...\n---`.
- Si le frontmatter est manquant : l'ajouter avec le nom du skill et une description concise.
- Si le frontmatter est incomplet : le compléter.

### Étape 6 : Mise à jour du registre
- Mettre à jour `.claude/skills/SKILL-MASTER.md` avec le nouveau skill (mots-clés de déclenchement + fichier).
- Mettre à jour `CLAUDE.md` si de nouvelles règles globales sont nécessaires.

### Étape 7 : Tests fonctionnels (obligatoire)
Pour chaque skill installé, exécuter au minimum :
1. **Test de structure** : YAML valide, ≥2 sections `##`, ≥3 bullets/items, >500 caractères.
2. **Test de build** (si c'est un outil Node/Python) : `npm install` → `npm run build` / `pip install -r requirements.txt`.
3. **Test d'exécution réelle** : simuler l'utilisation principale du skill (générer un fichier, exécuter une commande, faire une requête HTTP, etc.).
4. **Si échec** : corriger → retester (boucle d'auto-correction). Si blocage externe (API payante sans clé), le documenter honnêtement.

### Étape 8 : Rapport après installation
Suivre la méthodologie obligatoire de CLAUDE.md :
1. Lister exactement les fichiers modifiés/créés.
2. Expliquer ce qui a changé.
3. Expliquer ce qui n'a PAS été fait (et pourquoi).
4. Donner le résultat réel des tests avec preuves (tailles de fichiers, sorties de commande).
5. Classer chaque affirmation : PROUVÉ / PROBABLE / HYPOTHÈSE / NON FAIT.

### Étape 9 : Nettoyage (si demandé)
- Supprimer les fichiers de test temporaires si l'utilisateur le demande.
- Garder les preuves si l'utilisateur veut les conserver.

**Règle d'or :** Ne jamais déclarer un skill "installé" sans avoir passé les étapes 8 et 9. Une installation sans test n'est pas une installation. L'étape 0 (architecture saine) est la plus importante — elle évite les conflits et les réinstallations.
