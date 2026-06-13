#!/usr/bin/env node
/*
 * browser-live — lanceur Chromium avec contournement du certificat du proxy.
 * Usage : node drive.js <url> [--shot fichier.png] [--dump] [--wait ms]
 *
 * Base réutilisable : copier ce fichier pour scripter un parcours sur mesure.
 * Le bloc launch()/newContext() est l'élément clé (flags + ignoreHTTPSErrors).
 */
const fs = require('fs');

function findChromium() {
  const base = '/opt/pw-browsers';
  try {
    const dirs = fs.readdirSync(base).filter(d => /^chromium-\d+$/.test(d))
      .sort((a, b) => parseInt(b.split('-')[1]) - parseInt(a.split('-')[1]));
    for (const d of dirs) {
      const p = `${base}/${d}/chrome-linux64/chrome`;
      if (fs.existsSync(p)) return p;
    }
  } catch (e) {}
  return undefined; // laisse Playwright choisir son binaire par défaut
}

function loadPlaywright() {
  for (const p of ['/opt/node22/lib/node_modules/playwright', 'playwright']) {
    try { return require(p); } catch (e) {}
  }
  throw new Error('Module playwright introuvable');
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function launch() {
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({
    executablePath: findChromium(),
    headless: true,
    args: ['--ignore-certificate-errors', '--no-sandbox', '--disable-setuid-sandbox'],
  });
  const context = await browser.newContext({ ignoreHTTPSErrors: true, locale: 'fr-CH' });
  return { browser, context };
}

module.exports = { launch, findChromium, loadPlaywright, sleep };

// Exécution directe en CLI
if (require.main === module) {
  (async () => {
    const args = process.argv.slice(2);
    const url = args.find(a => !a.startsWith('--'));
    if (!url) { console.error('Usage: node drive.js <url> [--shot f.png] [--dump]'); process.exit(1); }
    const shot = args.includes('--shot') ? args[args.indexOf('--shot') + 1] : null;
    const waitMs = args.includes('--wait') ? parseInt(args[args.indexOf('--wait') + 1]) : 4000;

    const { browser, context } = await launch();
    const page = await context.newPage();
    console.log('→', url);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
    console.log('  titre:', await page.title());
    await sleep(waitMs);
    if (shot) { await page.screenshot({ path: shot, fullPage: true }); console.log('  capture:', shot); }
    if (args.includes('--dump')) {
      const els = await page.evaluate(() => Array.from(document.querySelectorAll('input,button,a,select'))
        .filter(e => e.offsetParent !== null).slice(0, 50)
        .map(e => ({ tag: e.tagName, type: e.type || '', name: e.name || '', id: e.id || '',
          txt: (e.innerText || e.value || '').slice(0, 40) })));
      els.forEach(e => console.log('   ', JSON.stringify(e)));
    }
    await browser.close();
  })().catch(e => { console.error('ERREUR:', e.message); process.exit(1); });
}
