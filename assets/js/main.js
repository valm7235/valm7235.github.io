// Expert IA Suisse — interactions sobres
(function () {
  'use strict';

  document.documentElement.classList.add('has-js');

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
