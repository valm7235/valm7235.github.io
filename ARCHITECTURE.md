# Architecture du site — Expert IA Suisse

> ⚠️ **Mise à jour du 13 juin 2026 — Refonte complète.** Le site public a été
> reconstruit en **HTML/CSS statique écrit à la main** (voir section « Refonte 2026 »
> en bas de ce document). L'analyse Next.js ci-dessous décrit l'**ancienne**
> architecture ; elle reste pertinente pour les pages du tunnel d'achat
> (`download-secure-2026.html`) qui dépendent encore de `_next/`.

> Analyse réalisée le 12 juin 2026. Les points marqués **[VÉRIFIÉ]** ont été testés
> en production (`https://valm7235.github.io`) ; les points marqués *[hypothèse]*
> sont déduits du code mais non confirmés.

## Vue d'ensemble

Le site est un **export statique Next.js (App Router)** déployé sur GitHub Pages.
Ce n'est pas du HTML écrit à la main : chaque page racine est le résultat compilé
d'une application React. Il n'y a **aucun backend** — pas de serveur, pas de base
de données. Tout ce qui est dynamique (paiement, e-mails) est délégué à des
services externes (Stripe, et probablement un automatiseur type Zapier
*[hypothèse]*).

**Flux commercial :** visiteur → page produit (`produit-pack-prompts.html`) →
bouton d'achat Stripe → redirection vers `confirmation.html` → e-mail avec lien
vers `download-secure-2026.html` → livraison des prompts.

## Concepts clés

- **Export statique Next.js** : les pages `.html` à la racine sont générées par
  `next build` (mode export). Elles référencent les scripts et CSS du dossier
  `_next/static/`.
- **Fichiers `.txt` jumeaux** : chaque page a un double `.txt`
  (ex. `index.html` + `index.txt`). Ce sont les **payloads RSC** (React Server
  Components) — le routeur Next.js côté client les télécharge pour naviguer
  entre pages sans rechargement complet.
- **`_next/static/`** : chunks JavaScript (framework React, code par route dans
  `chunks/app/…`) et CSS Tailwind compilé (`css/67b539445945d696.css`).
- **Stripe Buy Button** : toutes les pages préchargent
  `https://js.stripe.com/v3/buy-button.js`. Le paiement est entièrement géré
  par Stripe (aucune donnée bancaire ne transite par le site).
- **Jekyll et le underscore** : GitHub Pages passe par Jekyll par défaut, qui
  **exclut les dossiers commençant par `_`**. Le fichier `.nojekyll` (ajouté
  dans ce commit) désactive Jekyll pour que `_next/` soit servi.

## Comment ça fonctionne (visiteur → achat → téléchargement)

1. **Arrivée** : le navigateur charge `index.html`, puis les chunks
   `_next/static/chunks/*.js` et le CSS. React « hydrate » la page (elle devient
   interactive).
2. **Navigation** : un clic vers `/produit-pack-prompts` fait télécharger
   `produit-pack-prompts.txt` (payload RSC) — transition instantanée sans
   rechargement. Si JavaScript échoue, le navigateur retombe sur le `.html`.
3. **Achat** : la page produit affiche le bouton Stripe. Stripe encaisse, puis
   redirige vers `/confirmation` (configuré dans le dashboard Stripe
   *[hypothèse]*).
4. **Livraison** : un e-mail envoie un lien vers `/download-secure-2026`
   *[hypothèse : automatisation externe]*. Les fichiers produits vivent dans
   `produit/*.md`.

## Où vivent les choses

| Chemin | Rôle |
|---|---|
| `index.html` / `index.txt` | Landing page + payload RSC |
| `produit-pack-prompts.html` | Page de vente (Stripe) |
| `confirmation.html`, `confirmation-final.html` | Pages post-paiement |
| `download-secure-2026.html` | Page d'accès au téléchargement |
| `blog.html`, `blog/*.html` | Index + 4 articles de blog |
| `guides.html`, `guides/*.html` | Index + 7 guides piliers SEO |
| `cgv.html`, `mentions-legales.html`, `confidentialite.html`, `terms.html`, `privacy.html`, `legal.html` | Pages légales (FR + doublons EN) |
| `contact.html` | Page contact |
| `404.html` | Page d'erreur personnalisée |
| `produit/*.md` | **Le produit vendu** (3 prompts + guide d'utilisation) |
| `_next/static/chunks/` | JavaScript compilé (React, code par route) |
| `_next/static/css/` | CSS Tailwind compilé |
| `.nojekyll` | Désactive Jekyll pour que `_next/` soit servi |
| `navbar.js`, `styles-optimized.css` | Anciens fichiers, non référencés par les pages Next.js |
| `index-backup.html`, `index-corrige.html`, `index-optimized.html`, `test-navigation.html`, `navigation-simple.html` | Fichiers de test/sauvegarde, à nettoyer |
| `.claude/` | Configuration Claude Code (skills, hooks, MCP) — pas une partie du site |

## Pièges et points d'attention

1. **[VÉRIFIÉ — corrigé par ce commit] `_next/` renvoyait 404 en production.**
   Sans `.nojekyll`, Jekyll excluait le dossier `_next/` : le CSS
   (`_next/static/css/67b539445945d696.css`) et tous les chunks JS renvoyaient
   404, donc le site s'affichait sans styles ni interactivité. Le fichier vide
   `.nojekyll` corrige cela. ⚠️ Effet de bord : Jekyll désactivé signifie que
   **tous** les fichiers du dépôt sont servis, y compris `.claude/` (le dépôt
   étant public, ils étaient déjà visibles sur GitHub).
2. **[VÉRIFIÉ] Le produit payant est accessible gratuitement.**
   `https://valm7235.github.io/produit/conseiller-fiscal-prompt.md` répond 200 :
   quiconque connaît ou devine l'URL télécharge les prompts sans payer. Le
   « lien sécurisé » `download-secure-2026` n'a aucune validation côté serveur
   (impossible sans backend) — c'est de la sécurité par obscurité. Pour une
   vraie protection : livrer le contenu dans l'e-mail post-achat ou via un
   service de fichiers à liens expirants, et retirer `produit/` du dépôt.
3. **Doublons de pages légales** : `cgv`/`terms`/`legal` et
   `confidentialite`/`privacy` se recouvrent, sans balises
   `<link rel="canonical">` — risque de contenu dupliqué pour le SEO.
4. **Deux index de blog** : `blog.html` (Next.js) et `blog/index.html` (HTML
   artisanal, plus ancien) coexistent et peuvent diverger.
5. **Fichiers de test à la racine** : `index-backup.html`, `index-corrige.html`,
   `index-optimized.html`, `test-navigation.html`, `navigation-simple.html` (et
   leurs `.txt`) sont publiés et indexables. À supprimer ou archiver.
6. **Pas de `sitemap.xml` ni `robots.txt`** : pénalisant pour un site dont la
   stratégie repose sur le SEO (guides piliers).
7. **Pas de source Next.js dans le dépôt** : seul l'export compilé est versionné.
   Le projet source (composants React, `next.config.js`) vit ailleurs — toute
   modification de contenu doit se faire là-bas puis être ré-exportée, sinon
   elle sera écrasée au prochain déploiement.

---

## Refonte 2026 — Nouvelle architecture (13 juin 2026)

Le site public a été entièrement reconstruit pour ressembler à un site de grand
cabinet de fiduciaire / d'avocats : sobre, institutionnel, crédible.

### Stack
- **HTML statique écrit à la main**, plus aucune dépendance Next.js/React pour
  les pages publiques. Plus léger, plus rapide, plus facile à maintenir.
- **CSS unique** : `assets/css/main.css` (design system complet, variables,
  responsive, dark navy). **JS unique** : `assets/js/main.js` (menu mobile +
  révélations au défilement avec filet de sécurité).
- **Polices** : Newsreader (serif, titres) + Inter (texte) via Google Fonts.

### Direction artistique
- **Palette** : marine institutionnel (`#0a1e3c`), bleu royal (`#2563eb`),
  blanc et brume claire. Conserve l'ADN bleu de l'ancien site, mais plus profond
  et plus haut de gamme.
- **Signature** : un bandeau « chiffres officiels 2026 » sous le héro (TVA 8,1 %,
  pilier 3a 7'258 CHF, 26 cantons, nLPD) — chaque chiffre **sourcé** vers le site
  officiel correspondant (AFC, ch.ch, PFPDT). C'est ce qui distingue un site
  crédible d'une page marketing.
- **Domaines numérotés I/II/III** comme les practice groups d'un cabinet.

### Données vérifiées (juin 2026)
Toutes les données chiffrées ont été vérifiées à des sources officielles :
- TVA : taux normal **8,1 %** (AFC, depuis le 1.1.2024).
- Pilier 3a : max **7'258 CHF** (salarié 2e pilier) / **36'288 CHF** (indépendant
  sans caisse) pour 2026.
- AVS indépendants : taux max **10 %**, cotisation min **530 CHF/an**.
- TVA : seuil d'assujettissement **100'000 CHF** de CA.
- nLPD en vigueur depuis le **1.9.2023**.
- Modèles d'IA cités mis à jour : GPT-5.5, Claude Opus 4.8, Gemini 3.1 Pro.

### Inventaire des pages
- **Accueil** (`index.html`) : héro, chiffres clés, 3 domaines, problème/solution,
  3 scénarios, tarif (Stripe), FAQ, CTA.
- **Produit** (`produit-pack-prompts.html`), **Contact**, **Blog** (4 articles),
  **Guides** (7 guides) — tous réécrits avec contenu rédigé et vérifié.
- **Légal** : `mentions-legales`, `cgv`, `confidentialite` (conforme nLPD).
- **Tunnel** : `confirmation`, `confirmation-final` (rebrandés),
  `download-secure-2026` (inchangé, ancienne stack).
- **404** rebrandée. **Redirections** depuis les anciennes URL anglaises
  (`privacy`→`confidentialite`, `terms`→`cgv`, `legal`→`mentions-legales`).
- **SEO** : `sitemap.xml`, `robots.txt`.

### Skills Claude Code utilisés
Skills officiels Anthropic installés dans `.claude/skills/` pour cette refonte :
`frontend-design` (direction artistique), `theme-factory`, `web-artifacts-builder`,
`webapp-testing` (vérification via Chrome DevTools).

### Point de sécurité toujours ouvert
Le produit payant (`produit/*.md` et `download-secure-2026.html`) reste
téléchargeable par quiconque connaît l'URL : un site statique ne peut pas vérifier
le paiement. La livraison par e-mail reste la solution recommandée.

---

## Migration & parité de contenu (13 juin 2026, suite)

**Découverte clé :** le vrai site client était `expert-ia-suisse.ch`, hébergé sur
Firebase (Google Cloud, `35.219.200.3`), et non ce dépôt GitHub Pages. Firebase
Studio fermant, le site a été **migré vers GitHub Pages**.

### Parité de contenu atteinte
Le contenu du site Firebase a été crawlé (skill `browser-live`) et répliqué dans
le design cabinet. Pages ajoutées : `/particulier-impots`, `/independant-fiscalite`,
`/pro-fiduciaire-avocat`, `/offre` (canonique ; `produit-pack-prompts` redirige
vers elle), `/exemples`, `/sources-officielles`. Navigation et pied de page unifiés
(Particuliers/Indépendants/Professionnels · Guides · Blog · Sources officielles ·
Contact · Obtenir le pack → /offre).

### Migration DNS (via API Infomaniak)
Domaine Infomaniak id `2059077`. Les enregistrements A apex et `www` ont été
basculés de `35.219.200.3` (Firebase) vers les 4 IP GitHub Pages
(`185.199.108-111.153`). Enregistrements e-mail (MX, SPF, DKIM, DMARC) **inchangés**.
`CNAME` = `expert-ia-suisse.ch` dans le dépôt. HTTPS activé automatiquement après
propagation.

### Stripe (mode test)
Produit renommé « Pack Expert IA Suisse » (était « Conseiller IA »). Prix confirmé
499 CHF (devise unique CHF). Le nom d'affichage du compte « ExpetIA Suisse »
(faute de frappe) doit être corrigé dans le Dashboard Stripe (non modifiable via
clé test).

### Clés / secrets
Fournis via variables d'environnement du conteneur (jamais committés) :
`STRIPE_SECRET_KEY` (test), `INFOMANIAK_API_TOKEN`, `GITHUB_TOKEN`. La méthode
correcte — ne jamais coller un secret dans le chat.
