"""Build one Club WIS sponsorship page per row of vendors.csv.

Usage:  python build.py
Output: p/<slug>/index.html for every vendor, plus links.csv (company -> URL)
"""
import csv, html, json, re, secrets, pathlib

SITE = "https://wisadvancement.github.io/clubwis"   # change if the repo name differs
LEVELS = ["platinum", "gold", "silver", "bronze"]
# Apps Script web app URL that logs button clicks to the responses sheet (see apps-script/). Blank = no logging.
LOG_URL = "https://script.google.com/macros/s/AKfycbzTCr3nESVydYtNYm0pWtOHgDPiYCji6v7qtDyoZH7Tdi5m6RtcPtnjqM5nIvRy_pW3/exec"
ROOT = pathlib.Path(__file__).parent
TEMPLATE = (ROOT / "template.html").read_text(encoding="utf-8")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30]


def initials(name):
    words = [w for w in re.split(r"\s+", name) if w and w[0].isalnum()]
    return "".join(w[0] for w in words[:2]).upper() or "★"


def logo_html(row, esc_company):
    if row.get("logo", "").strip():
        src = html.escape("../../logos/" + row["logo"].strip())
        return f'<div class="logo has-img"><img src="{src}" alt="{esc_company} logo"></div>'
    return f'<div class="logo" aria-hidden="true">{html.escape(initials(row["company"]))}</div>'


WORDS = ["", "", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def years_phrase(raw):
    """'3' -> 'for the past three years'; '2017' -> 'since 2017'; blank or 1 -> 'last spring'."""
    try:
        n = int(raw)
    except ValueError:
        return "last spring"
    if n >= 1900:
        return f"since {n}"
    if n < 2:
        return "last spring"
    return f"for the past {WORDS[n] if n < len(WORDS) else n} years"


def sentence(text):
    text = text.strip()
    if text and text[-1] not in ".!?”\"":
        text += "."
    return html.escape(text)


def main():
    rows = list(csv.DictReader(open(ROOT / "vendors.csv", encoding="utf-8-sig")))
    changed = False
    out_links = []
    for row in rows:
        company = row["company"].strip()
        if not company:
            continue
        # Keep a stable, unguessable slug: generate once, then write it back to the CSV.
        if not row.get("slug", "").strip():
            row["slug"] = f"{slugify(company)}-{secrets.token_hex(3)}"
            changed = True
        last = row.get("last_level", "").strip().lower()
        # No recommended level and no last level = open ask: nothing preselected, sponsor picks.
        rec = row.get("recommended", "").strip().lower() or (last if last in LEVELS else "")
        assert not rec or rec in LEVELS, f"{company}: recommended level must be blank or one of {LEVELS}"
        esc = html.escape(company)
        thanks_note = row.get("thanks_note", "").strip()
        if last and last not in LEVELS:
            print(f"SKIP   {company:35s} last_level '{last}' isn't a sponsorship level (page left as is)")
            if (ROOT / "p" / row["slug"] / "index.html").exists():
                out_links.append({"company": company, "url": f"{SITE}/p/{row['slug']}/"})
            continue
        if last:
            # Renewal letter: requires one specific sentence of thanks.
            if not thanks_note:
                print(f"SKIP   {company:35s} needs a thanks_note (page left as is)")
                if (ROOT / "p" / row["slug"] / "index.html").exists():
                    out_links.append({"company": company, "url": f"{SITE}/p/{row['slug']}/"})
                continue
            thanks = f"Thank you for standing with WIS {years_phrase(row.get('years', '').strip())}. {sentence(thanks_note)}"
        else:
            # New-sponsor letter: an invitation; thanks_note is an optional extra sentence.
            thanks = (f"I would like to invite {esc} to join us as an event sponsor this spring. "
                      "Washington International School is a PreK–12 bilingual international school "
                      "with campuses in Georgetown and Cleveland Park.")
            if thanks_note:
                thanks += " " + sentence(thanks_note)
        # Optional: drop out entirely when blank.
        connection = row.get("connection", "").strip()
        ps = row.get("ps", "").strip()
        back = " back" if last else ""
        ask = (f"We would be delighted to welcome{back} {esc} as a {rec.title()} Patron." if rec
               else f"We would be delighted to welcome {esc} as a Club WIS sponsor.")
        if last:
            ask += " Below you can see how your business would appear on the night and choose the level that suits you."
        else:
            ask += " Below you can learn more, see how your business would appear on the night, and — hopefully — partner with us!"
        for lv in LEVELS:
            link = row.get(f"link_{lv}", "").strip()
            assert not link or link.startswith("https://app.betterunite.com/"), f"{company}: link_{lv} must be a BetterUnite https link"
        vendor = {
            "company": company,
            "first": row.get("first_name", "").strip() or "friends",
            "recommended": rec or None,
            "tag": "Last year" if last == rec else "Recommended",
            "slug": row["slug"],
            "links": {lv: row.get(f"link_{lv}", "").strip() for lv in LEVELS if row.get(f"link_{lv}", "").strip()},
        }
        page = (TEMPLATE
                .replace("{{COMPANY}}", esc)
                .replace("{{FIRST}}", html.escape(vendor["first"]))
                .replace("{{THANKS}}", thanks)
                .replace("{{REMAINS}}", "remains" if last else "is")
                .replace("{{EVENT_INTRO}}", "our spring benefit returns as" if last else "we host our annual spring benefit,")
                .replace("{{CONNECTION}}", f"\n    <p>{sentence(connection)}</p>" if connection else "")
                .replace("{{ASK}}", ask)
                .replace("{{PS}}", f"\n    <p class=\"ps\">P.S. {sentence(ps)}</p>" if ps else "")
                .replace("{{LOGO}}", logo_html(row, esc))
                .replace("{{LOGO_SLIDE}}", logo_html(row, esc))
                .replace("{{LOG_URL}}", json.dumps(LOG_URL))
                .replace("{{VENDOR_JSON}}", json.dumps(vendor, ensure_ascii=False).replace("</", "<\\/")))
        assert "{{" not in page, f"{company}: unfilled placeholder"
        dest = ROOT / "p" / row["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(page, encoding="utf-8")
        out_links.append({"company": company, "url": f"{SITE}/p/{row['slug']}/"})
        print(f"built  {company:35s} {SITE}/p/{row['slug']}/")

    if changed:
        with open(ROOT / "vendors.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader(); w.writerows(rows)
    with open(ROOT / "links.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company", "url"])
        w.writeheader(); w.writerows(out_links)


if __name__ == "__main__":
    main()
