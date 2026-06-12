# Architecture du site — Expert IA Suisse

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
