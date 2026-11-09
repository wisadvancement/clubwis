"""Build one Club WIS sponsorship page per row of vendors.csv.

Usage:  python build.py
Output: p/<slug>/index.html for every vendor, plus links.csv (company -> URL)
"""
import csv, html, json, re, secrets, pathlib

SITE = "https://wisadvancement.github.io/clubwis"   # change if the repo name differs
LEVELS = ["platinum", "gold", "silver", "bronze"]
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
        rec = (row.get("recommended", "").strip().lower() or last or "silver")
        assert rec in LEVELS, f"{company}: recommended level must be one of {LEVELS}"
        esc = html.escape(company)
        if last:
            relationship = f"{esc} sponsored at the {last.title()} level last year, and we’d love to have you back."
        else:
            relationship = f"We’d love to welcome {esc} as a sponsor this year."
        note = row.get("custom_note", "").strip()
        vendor = {
            "company": company,
            "first": row.get("first_name", "").strip() or "friends",
            "recommended": rec,
            "tag": "Last year" if last == rec else "Recommended",
            "links": {lv: row.get(f"link_{lv}", "").strip() for lv in LEVELS if row.get(f"link_{lv}", "").strip()},
        }
        page = (TEMPLATE
                .replace("{{COMPANY}}", esc)
                .replace("{{FIRST}}", html.escape(vendor["first"]))
                .replace("{{RELATIONSHIP}}", relationship)
                .replace("{{CUSTOM_NOTE}}", f"<p>{html.escape(note)}</p>" if note else "")
                .replace("{{LOGO}}", logo_html(row, esc))
                .replace("{{LOGO_SLIDE}}", logo_html(row, esc))
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
