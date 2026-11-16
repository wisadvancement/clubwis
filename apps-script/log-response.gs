/** @OnlyCurrentDoc */
/**
 * Club WIS sponsor pages → "Club WIS 2027: Sponsor Page Responses" sheet.
 *
 * Setup (once):
 *   1. Open the responses sheet → Extensions → Apps Script.
 *   2. Replace the editor's contents with this file and save.
 *   3. Deploy → New deployment → type "Web app".
 *        Execute as: Me    Who has access: Anyone
 *   4. Copy the web app URL into LOG_URL at the top of build.py, rebuild, and push.
 *
 * The page sends only: page slug, company, level, benefits choice, button clicked.
 * Amounts are looked up here, not trusted from the page.
 */
const SITE = 'https://wisadvancement.github.io/clubwis/p/';
const LEVELS = {
  platinum: { name: 'Platinum', amt: 10000, ded: 8800, ad: true },
  gold:     { name: 'Gold',     amt: 5000,  ded: 4150, ad: true },
  silver:   { name: 'Silver',   amt: 2500,  ded: 1700, ad: true },
  bronze:   { name: 'Bronze',   amt: 1250,  ded: 950,  ad: false },
};
const AD_VALUE = 500;
const BENEFITS = {
  all:    { label: 'Nothing (keeps all benefits)',     ded: l => l.ded },
  adonly: { label: 'All benefits except the ad',       ded: l => l.amt - AD_VALUE },
  none:   { label: 'All benefits (full deduction)',    ded: l => l.amt },
};
const ACTIONS = { betterunite: 'Sponsor on BetterUnite', pledge: 'Pledge email' };

function doPost(e) {
  const p = (e && e.parameter) || {};
  const level = LEVELS[p.level];
  const benefit = BENEFITS[p.benefits];
  const action = ACTIONS[p.action];
  const slug = String(p.slug || '');
  if (!level || !benefit || !action || !/^[a-z0-9-]{3,40}$/.test(slug)) return ok_();
  if (p.benefits === 'adonly' && !level.ad) return ok_();

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    SpreadsheetApp.getActive().getSheetByName('Responses').appendRow([
      new Date(),
      "'" + String(p.company || '').slice(0, 80),   // leading ' keeps it as plain text
      level.name,
      level.amt,
      benefit.label,
      benefit.ded(level),
      action,
      SITE + slug + '/',
      p.benefits === 'all' ? '' : false,            // checkbox for Megan once the waiver is confirmed in writing
    ]);
  } finally {
    lock.releaseLock();
  }
  return ok_();
}

function ok_() {
  return ContentService.createTextOutput('ok');
}
