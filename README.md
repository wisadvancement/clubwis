# Club WIS sponsor pages

One personalized sponsorship page per vendor, generated from `vendors.csv`.
The pages collect no data. All payments go through BetterUnite's checkout.

## Add or update vendors
1. Add a row to `vendors.csv`. Leave `slug` blank; the build fills it in once and keeps it.
   - `last_level` / `recommended`: platinum, gold, silver or bronze (`last_level` blank for new sponsors)
   - `logo`: filename of an image you've put in `logos/` (blank = initials monogram)
   - `years`: years sponsoring (`3` = "for the past three years"), or the first year (`2017` = "since 2017"). Blank or 1 = "last spring"
   - `last_level`: blank = first-time sponsor (invitation letter); platinum/gold/silver/bronze = renewal letter. Anything else (e.g. "advertisement") is skipped.
   - `thanks_note`: renewals — **required**, one specific sentence thanking them for last year. New sponsors — optional extra sentence after the invitation.
   - `connection`: optional — a WIS family, alumni or neighbourhood tie. Blank drops the paragraph.
   - `ps`: optional — a personal postscript. Blank drops it.
   - Letter copy is in Suzanna's voice: use British spelling in these fields.
   - `link_<level>`: optional level-specific BetterUnite links (blank = main Club WIS page)
2. Run `python build.py`
3. Commit and push. `links.csv` lists each vendor's URL for Megan's outreach.

## Responses
Clicking "Sponsor on BetterUnite" or "Pledge now" logs the vendor, level, waiver choice and deductible amount to the
*Club WIS 2027: Sponsor Page Responses* Google Sheet, through the Apps Script in `apps-script/log-response.gs`
(setup steps are at the top of that file). It logs the click, not the payment: check BetterUnite for what was paid.

## Privacy
- Root page redirects to wis.edu, so there's no index of vendors.
- Every page has `noindex`; `robots.txt` blocks crawlers.
- Slugs carry a random suffix so URLs can't be guessed.
- Keep gift amounts and personal contact details out of `vendors.csv`: the repo is public.
