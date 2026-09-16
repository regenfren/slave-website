#!/usr/bin/env python3
"""Build films/index.html and fr/films/index.html.

Run from the repo root:  python3 tools/films-pages.py

Idempotent. The head, header and footer are lifted from index.html and fr/index.html (the Rails
of Time home) at build time, so nav changes made there carry over automatically. Edit the copy in
the LANGS dict below, not in the generated HTML.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nav  # noqa: E402  (tools/nav.py: the one source of truth for the header + footer links)

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://railsoftime.fr/"

LANGS = {
    "en": {
        "dir": "",
        "title": "Student films - ASSO S.L.A.V.É.",
        "description": "Short films made in class by students at KEDGE, the CNAM and our other partner universities, as part of Rails of Time.",
        "h1": "Student films",
        "h2": "Films by school and cohort",
        "lede": "Short films made in class at our partner universities, as part of Rails of Time. Each cohort builds a scenario over a term, then shoots and edits it themselves.",
    },
    "fr": {
        "dir": "fr/",
        "title": "Films des étudiants - ASSO S.L.A.V.É.",
        "description": "Des courts-métrages réalisés en cours par les étudiants de KEDGE, du CNAM et de nos autres universités partenaires, dans le cadre des Rails du Temps.",
        "h1": "Les films des étudiants",
        "h2": "Les films par école et promotion",
        "lede": "Des courts-métrages réalisés en cours dans nos universités partenaires, dans le cadre des Rails du Temps. Chaque promotion construit un scénario sur un semestre, puis tourne et monte elle-même.",
    },
}


def set_meta(head, prop, value):
    return re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(")', lambda m: m.group(1) + value + m.group(2), head, count=1)


def build(lang: str) -> Path:
    L = LANGS[lang]
    pre = "/fr" if lang == "fr" else ""
    src = (ROOT / L["dir"] / "index.html").read_text(encoding="utf-8")
    head = re.search(r"<head>.*?</head>", src, re.S).group(0)
    header = re.search(r"<header.*?</header>", src, re.S).group(0)
    footer = re.search(r"<footer.*?</footer>", src, re.S).group(0)

    head = re.sub(r"<title>.*?</title>", f"<title>{L['title']}</title>", head, count=1)
    for prop in ("description", "og:title", "og:description", "twitter:title", "twitter:description"):
        head = set_meta(head, prop, L["title"] if prop.endswith("title") else L["description"])
    head = set_meta(head, "og:url", f"{HOST}{L['dir']}films/")
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{HOST}{L["dir"]}films/">', head, count=1)
    head = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{HOST}films/">', head, count=1)
    head = re.sub(r'<link rel="alternate" hreflang="fr" href="[^"]*">', f'<link rel="alternate" hreflang="fr" href="{HOST}fr/films/">', head, count=1)
    head = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{HOST}films/">', head, count=1)
    head = head.replace('<link rel="stylesheet" href="/assets/showcase.css">', '<link rel="stylesheet" href="/assets/films.css">')
    if "schools.css" not in head:
        head = head.replace('<link rel="stylesheet" href="/assets/films.css">', '<link rel="stylesheet" href="/assets/schools.css">\n    <link rel="stylesheet" href="/assets/films.css">')
    if "films.css" not in head:
        head = head.replace("</head>", '    <link rel="stylesheet" href="/assets/films.css">\n</head>')

    body = f"""
<section class="films-hero"><div class="container mx-auto px-4 md:px-8">
  <h1>{L['h1']}</h1>
  <p>{L['lede']}</p>
  <p class="films-count" id="films-count"></p>
</div></section>
<div id="films" class="container mx-auto px-4 md:px-8"><h2 class="films-sr">{L['h2']}</h2></div>
"""
    out = f'<!DOCTYPE html><html lang="{lang}">' + head + "<body>" + header + body + footer + \
        '<script src="/assets/clone.js"></script><script src="/assets/schools.js"></script><script src="/assets/films.js" data-assets="/assets/"></script></body></html>\n'
    out = nav.apply(out, lang, "films/")
    dest = ROOT / L["dir"] / "films" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    return dest


def check_schools():
    """Rule (Tim, 2026-09-15): every school that has a published film carries a logo and a tagline in
    both languages, because the site shows them as the school selector. Fails loudly."""
    d = json.loads((ROOT / "assets" / "films.json").read_text(encoding="utf-8"))
    used = {f["school"] for f in d.get("films", []) if f.get("youtube")}
    bad = []
    for sid in sorted(used):
        s = d["schools"].get(sid, {})
        tag = s.get("tagline") or {}
        missing = [k for k, ok in (("name", bool(s.get("name"))), ("city", bool(s.get("city"))), ("logo", bool(s.get("logo")) and (ROOT / s.get("logo", "")).exists()),
                                    ("tagline.en", bool(tag.get("en"))), ("tagline.fr", bool(tag.get("fr")))) if not ok]
        if missing:
            bad.append(f"{sid}: missing {', '.join(missing)}")
    if bad:
        sys.exit("films.json schools rule broken (name, city, logo file, tagline en+fr for every school with a published film):\n  " + "\n  ".join(bad))


def main():
    check_schools()
    for lang in LANGS:
        print("wrote", build(lang).relative_to(ROOT))
    for lang, L in LANGS.items():
        pre = "/fr" if lang == "fr" else ""
        html = (ROOT / L["dir"] / "films" / "index.html").read_text(encoding="utf-8")
        n = html.count(f'href="{pre}/films/"')
        if n != 2:
            print(f"WARN {L['dir']}films/index.html: films link appears {n} times (expected 2: nav + footer)", file=sys.stderr)


if __name__ == "__main__":
    main()
