---
name: Règles permanentes sécurité / crypto / anti-hallucination
description: Règles strictes à appliquer pour tout code touchant à la sécurité, la cryptographie, l'authentification, les clés, les logs, les paiements ou les données sensibles.
type: feedback
originSessionId: 0a148764-db33-4620-8262-ebdeca357610
---
**Règle :** Appliquer strictement les règles anti-hallucination, sécurité et cryptographie définies dans le fichier CLAUDE.md du projet.

**Why:** L'utilisateur a fourni un ensemble de règles permanentes très strictes concernant la sécurité, la cryptographie et la méthodologie de preuve. Il insiste sur le fait de ne jamais surévaluer ce qui est fait, de ne jamais inventer de primitives crypto, et de toujours classer les affirmations en PROUVÉ / PROBABLE / HYPOTHÈSE / NON FAIT.

**How to apply:**
- Ne jamais affirmer qu'un système est "sécurisé", "production-ready", "conforme", "cryptographiquement sûr", etc. sans preuve vérifiable.
- N'utiliser que des bibliothèques reconnues (libsodium, cryptography, OpenSSL, WebCrypto, Tink, etc.).
- Avant toute modification complexe : lire, résumer, lister hypothèses/risques, proposer un plan, attendre validation si sécurité/auth/crypto/clés/logs/paiements/données sensibles.
- Après modification : lister fichiers modifiés, expliquer ce qui a changé et ce qui n'a PAS été fait, exécuter les tests, donner le résultat réel. Si pas de tests, dire explicitement "Non vérifié par test automatique".
- Classer chaque affirmation technique importante : PROUVÉ / PROBABLE / HYPOTHÈSE / NON FAIT.
- Quand plusieurs solutions existent : proposer 3 options avec avantages/risques/difficulté, recommander la plus robuste, ne coder qu'après choix explicite ou justification claire.
- Le fichier source de vérité est `CLAUDE.md` dans le répertoire de travail.
