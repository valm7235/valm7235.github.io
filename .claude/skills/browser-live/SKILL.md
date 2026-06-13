---
name: browser-live
description: Pilote un vrai navigateur Chromium (Playwright) avec contournement du certificat du proxy réseau de l'environnement web. À utiliser pour tester de bout en bout des parcours réels — paiement Stripe (mode test), formulaires, redirections, tunnels — quand le navigateur du MCP échoue sur ERR_CERT_AUTHORITY_INVALID pour les domaines HTTPS externes (GitHub Pages, Stripe, etc.).
---

# browser-live — navigation réelle avec contournement de certificat

## Quand l'utiliser
Dans l'environnement d'exécution distant (Claude Code on the web), le proxy réseau
présente des **certificats SSL invalides** pour les domaines HTTPS externes. Les
navigateurs MCP (`chrome-devtools`, `playwright`) échouent alors sur
`net::ERR_CERT_AUTHORITY_INVALID` dès qu'on quitte `localhost`.

Ce skill lance un Chromium **avec** `--ignore-certificate-errors` et
`ignoreHTTPSErrors: true`, ce qui permet d'atteindre n'importe quel site externe
(production GitHub Pages, `js.stripe.com`, `buy.stripe.com`, …) et de dérouler un
parcours complet comme un vrai utilisateur.

## Comment « voir » et agir
Pas de flux vidéo : on agit sur le **DOM réel** (sélecteurs, `data-testid`, `name`)
et on **capture des PNG** qu'on relit. Privilégier les sélecteurs stables aux
coordonnées. Les iframes cross-origin (ex. bouton Stripe) sont accessibles via
`page.frames()`.

## Utilisation rapide
```bash
node .claude/skills/browser-live/scripts/drive.js <url> [--shot fichier.png] [--dump]
```
- `--shot` : capture pleine page.
- `--dump` : liste les `input`/`button` visibles (utile pour repérer les champs).

Pour un scénario sur mesure, copier `scripts/drive.js` comme base : il contient le
lanceur correctement configuré (chemin du binaire Chromium, flags, contexte).

## Détails techniques
- Binaire Chromium installé par la session (cf. hook SessionStart) :
  `/opt/pw-browsers/chromium-1226/chrome-linux64/chrome` — le script le détecte
  automatiquement, avec repli sur le dernier `chromium-*` disponible.
- Module Playwright global : `/opt/node22/lib/node_modules/playwright`.
- Toujours `--no-sandbox` dans ce conteneur.

## Tester un paiement Stripe (mode test)
1. Le bouton Stripe se charge dans une iframe `buy-button-app` (shadow DOM du
   composant `<stripe-buy-button>`). Cliquer
   `[data-testid="hosted-buy-button"]` dans cette iframe.
2. Le checkout s'ouvre dans un **nouvel onglet** → `context.waitForEvent('page')`.
3. Carte de test : `4242 4242 4242 4242`, exp `12 / 34`, CVC `123`.
   (Voir https://stripe.com/docs/testing pour 3DS, refus, etc.)
4. Champs clés : `#email`, `#cardNumber`, `#cardExpiry`, `#cardCvc`,
   `#billingName`, `#billingPostalCode`, `#billingCountry` (select).
   Remplissage **best-effort** : certains champs d'adresse sont masqués
   (`HiddenInput`) tant que le pays n'est pas choisi — sélectionner le pays
   d'abord. Soumettre via `[data-testid="hosted-payment-submit-button"]`.
5. Vérifier la **redirection** vers l'URL de succès (configurée dans le Dashboard
   Stripe), pas seulement l'absence d'erreur.

Ne jamais utiliser de vraie carte / clé live sans autorisation explicite et par
transaction. Le mode test (`sk_test_`/`pk_test_`, cartes `4242…`) est l'outil de
simulation prévu à cet effet.
