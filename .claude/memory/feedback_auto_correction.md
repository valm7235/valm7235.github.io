---
name: Préférence boucle d'auto-correction
description: L'utilisateur exige une boucle d'auto-correction systématique : tester, simuler, corriger, jusqu'à ce que ça marche parfaitement. Si ça ne marche pas, trouver une solution alternative avec simulation réelle après correction.
type: feedback
originSessionId: 0a148764-db33-4620-8262-ebdeca357610
---
**Règle :** À chaque fois que je crée quelque chose (code, config, etc.), je DOIS tester et simuler comme si j'étais l'utilisateur. Si ça ne fonctionne pas, je corrige immédiatement et je RETESTE. Boucle jusqu'à ce que ça marche parfaitement. Si une approche échoue, je dois trouver une solution alternative et la tester aussi. La simulation réelle après correction est obligatoire.

**Why:** L'utilisateur a demandé explicitement : "toujours faire une boucle d'auto-correction. Quand quelque chose ne fonctionne pas ou quoi que ce soit, que vous avez créé ou je ne sais quoi, prenez toujours le réflexe de tester comme si c'était moi qui utilisais cette chose, en faisant une simulation. Si ça ne fonctionne pas, vous créez une boucle d'auto-correction à chaque fois." Et aussi : "vos règles (honnêteté, preuves) vous obligent à dire la vérité mais aussi a toujours essayer de trouvez une solution alternative avec simulation réel apres correction et boucle d'autocorrection."

**How to apply:**
- Après chaque création de fichier/code : exécuter/tester/valider immédiatement
- Simuler le parcours utilisateur (golden path + edge cases)
- Si erreur → corriger → retester → répéter jusqu'à succès
- Si l'approche principale échoue : trouver une approche alternative, l'implémenter, et la tester aussi
- Ne jamais livrer sans avoir vérifié que ça fonctionne réellement
- Pour le code : lancer les tests, vérifier les types, tester le build
- Pour la config : vérifier la syntaxe, tester la commande concernée
- Signaler honnêtement si un test échoue et que je ne peux pas le résoudre seul
- La simulation réelle après correction est obligatoire : "ça ne marche pas → je corrige → je simule l'utilisation réelle → ça marche → je continue"
