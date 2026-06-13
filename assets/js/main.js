// Expert IA Suisse — interactions sobres

/* ============================================================
   PAIEMENT STRIPE — INTERRUPTEUR TEST / RÉEL
   Pour encaisser de VRAIS paiements : remplacez 'test' par 'live'
   sur la ligne ci-dessous (un seul mot à changer), puis enregistrez.
     'test' = vos amis peuvent tester avec une carte de test, sans payer.
     'live' = vrais paiements, l'argent arrive sur votre compte Stripe.
   ============================================================ */
var STRIPE_PAYMENT_MODE = 'test';

var STRIPE_LINKS = {
  test: 'https://buy.stripe.com/test_5kQ8wQ1HyfO029wfWzfEk01',
  live: 'https://buy.stripe.com/3cI28sae4dFS8xU11FfEk02'
};

(function () {
  'use strict';

  document.documentElement.classList.add('has-js');

  // Applique le lien de paiement (test/réel) à tous les boutons d'achat
  var payUrl = STRIPE_LINKS[STRIPE_PAYMENT_MODE] || STRIPE_LINKS.test;
  var payButtons = document.querySelectorAll('[data-stripe-pay]');
  for (var i = 0; i < payButtons.length; i++) { payButtons[i].href = payUrl; }

  // Navigation mobile
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Révélation au défilement (désactivée si reduced motion)
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.reveal');
  function revealAll() {
    items.forEach(function (el) { el.classList.add('is-visible'); });
  }
  if (!reduced && 'IntersectionObserver' in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.06, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
    // Filet de sécurité : rien ne reste invisible (ex. bas de page jamais observé)
    setTimeout(revealAll, 2000);
  } else {
    revealAll();
  }
})();
