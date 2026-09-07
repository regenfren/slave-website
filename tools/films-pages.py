#!/usr/bin/env python3
"""Build films.html and fr/films.html, and keep the "Student films" link in every page's nav.

Run from the repo root:  python3 tools/films-pages.py

Idempotent. The header and footer of the films pages are lifted from projects.html and
fr/projects.html at build time, so nav changes made there carry over automatically.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "association.html", "projects.html", "dignity.html", "contact.html", "404.html"]

ACTIVE_LINK = 'class="block px-5 py-3 text-sm font-medium transition-colors bg-[rgba(0,85,164,0.08)] text-[#0055A4]"'
IDLE_LINK = 'class="block px-5 py-3 text-sm font-medium transition-colors text-[#003D6B] hover:bg-[rgba(0,85,164,0.05)] hover:text-[#0055A4]"'

LANGS = {
    "en": {
        "dir": "", "assets": "assets/", "nav": "Student films",
        "title": "Student films - ASSO S.L.A.V.É.",
        "description": "Short films made in class by students at KEDGE, the CNAM and our other partner universities, as part of Rails of Time.",
        "h1": "Student films",
        "lede": "Short films made in class at our partner universities, as part of Rails of Time. Each cohort builds a scenario over a term, then shoots and edits it themselves.",
    },
    "fr": {
        "dir": "fr/", "assets": "../assets/", "nav": "Films des étudiants",
        "title": "Films des étudiants - ASSO S.L.A.V.É.",
        "description": "Des courts-métrages réalisés en cours par les étudiants de KEDGE, du CNAM et de nos autres universités partenaires, dans le cadre des Rails du Temps.",
        "h1": "Les films des étudiants",
        "lede": "Des courts-métrages réalisés en cours dans nos universités partenaires, dans le cadre des Rails du Temps. Chaque promotion construit un scénario sur un semestre, puis tourne et monte elle-même.",
    },
}


def patch_nav(path: Path, label: str) -> bool:
    """Add the films link to the Projects dropdown, the footer quick links and (nothing else)."""
    html = path.read_text(encoding="utf-8")
    orig = html
    if 'href="films.html"' not in html:
        # dropdown: after the Right to Dignity entry
        html = re.sub(
            r'(<a class="block px-5 py-3[^"]*" href="dignity\.html">[^<]*</a>)',
            lambda m: m.group(1) + f'<a {IDLE_LINK} href="films.html">{label}</a>',
            html, count=1,
        )
        # footer quick links: after the Right to Dignity <li>
        html = re.sub(
            r'(<li><a class="text-white/80[^"]*" href="dignity\.html">.*?</a></li>)',
            lambda m: m.group(1) + m.group(1).replace('href="dignity.html"', 'href="films.html"').replace(
                re.sub(r"<[^>]+>", "", m.group(1)).strip(), label),
            html, count=1, flags=re.S,
        )
    if html != orig:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def patch_clone_js() -> bool:
    p = ROOT / "assets" / "clone.js"
    js = p.read_text(encoding="utf-8")
    if "'films.html'" in js:
        return False
    js = js.replace("'dignity.html','contact.html'", "'dignity.html','films.html','contact.html'", 1)
    p.write_text(js, encoding="utf-8")
    return True


def build(lang: str) -> Path:
    L = LANGS[lang]
    src = (ROOT / L["dir"] / "projects.html").read_text(encoding="utf-8")
    head = re.search(r"<head>.*?</head>", src, re.S).group(0)
    header = re.search(r"<header.*?</header>", src, re.S).group(0)
    footer = re.search(r"<footer.*?</footer>", src, re.S).group(0)

    head = re.sub(r"<title>.*?</title>", f"<title>{L['title']}</title>", head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + L["description"] + m.group(2), head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + L["title"] + m.group(2), head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + L["description"] + m.group(2), head, count=1)
    head = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + L["title"] + m.group(2), head, count=1)
    head = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + L["description"] + m.group(2), head, count=1)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + "https://railsoftime.fr/" + L["dir"] + "films.html" + m.group(2), head, count=1)
    head = head.replace(
        f'<link rel="stylesheet" href="{L["assets"]}clone-fixes.css">',
        f'<link rel="stylesheet" href="{L["assets"]}clone-fixes.css">\n    <link rel="stylesheet" href="{L["assets"]}films.css">',
    )
    if "films.css" not in head:
        head = head.replace("</head>", f'    <link rel="stylesheet" href="{L["assets"]}films.css">\n</head>')

    # active state: Films instead of Rails of Time in the dropdown
    header = header.replace(f'{ACTIVE_LINK} href="projects.html"', f'{IDLE_LINK} href="projects.html"')
    header = header.replace(f'{IDLE_LINK} href="films.html"', f'{ACTIVE_LINK} href="films.html"')

    body = f"""
<section class="films-hero"><div class="container mx-auto px-4 md:px-8">
  <h1>{L['h1']}</h1>
  <p>{L['lede']}</p>
  <p class="films-count" id="films-count"></p>
</div></section>
<div id="films" class="container mx-auto px-4 md:px-8"></div>
"""
    out = f'<!DOCTYPE html><html lang="{lang}">' + head + "<body>" + header + body + footer + \
        f'<script src="{L["assets"]}clone.js"></script><script src="{L["assets"]}films.js" data-assets="{L["assets"]}"></script></body></html>\n'
    dest = ROOT / L["dir"] / "films.html"
    dest.write_text(out, encoding="utf-8")
    return dest


def main():
    changed = []
    for lang, L in LANGS.items():
        for page in PAGES:
            p = ROOT / L["dir"] / page
            if p.exists() and patch_nav(p, L["nav"]):
                changed.append(str(p.relative_to(ROOT)))
    if patch_clone_js():
        changed.append("assets/clone.js")
    for lang in LANGS:
        changed.append(str(build(lang).relative_to(ROOT)))
    print("wrote/patched:", ", ".join(changed) if changed else "nothing")
    # sanity: every page carries the films link once
    for lang, L in LANGS.items():
        for page in PAGES:
            p = ROOT / L["dir"] / page
            if p.exists():
                n = p.read_text(encoding="utf-8").count('href="films.html"')
                if n != 2:
                    print(f"WARN {p.relative_to(ROOT)}: films link appears {n} times (expected 2: dropdown + footer)", file=sys.stderr)


if __name__ == "__main__":
    main()
