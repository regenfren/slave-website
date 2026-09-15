#!/usr/bin/env python3
"""One-shot restructure, 2026-09-15 (Tim + Daria check-in). Run once from the repo root.

What it does, per language (EN at the root, FR under fr/):
- /            <- the old projects.html (Rails of Time), plus a "Student films" stage after the hero
- /asso/       <- the old index.html (home) with the association page folded in: the About block
                  becomes intro + team photo + a collapsible "History & Values"
- /films/, /dignity/, /contact/  <- folder-per-page, so URLs carry no .html
- every old *.html address becomes a redirect stub (meta refresh + canonical, noindex)
- nav is flat (Rails of Time, Films, Asso, Right to Dignity, Contact); asset paths are absolute

Refuses to run twice: asso/index.html existing means the move already happened.
films/index.html is NOT written here; run tools/films-pages.py afterwards.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://railsoftime.fr/"

if (ROOT / "asso" / "index.html").exists():
    sys.exit("asso/index.html already exists: the restructure has run. Nothing done.")

LINK_IDLE = 'class="text-sm font-medium transition-all hover:text-[#0055A4] relative text-[#003D6B] after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-[#EF4444] after:transition-all after:duration-300 hover:after:w-full"'
LINK_ACTIVE = 'class="text-sm font-medium transition-all hover:text-[#0055A4] relative text-[#0055A4] after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-[#EF4444] after:transition-all after:duration-300 hover:after:w-full after:w-full"'

PLAY_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" class="w-5 h-5"><path d="M8 5v14l11-7z"/></svg>'
CHEVRON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'

L = {
    "en": {
        "dir": "", "pre": "",
        "nav": [("", "Rails of Time"), ("films/", "Films"), ("asso/", "Asso"), ("dignity/", "Right to Dignity")],
        "contact": "Contact",
        "home_title": "Rails of Time - ASSO S.L.A.V.É.",
        "home_desc": "Rails of Time is an inter-university project by ASSO S.L.A.V.É.: students design itineraries, shoot short films and tell the living stories of the places shaping France's territories.",
        "asso_title": "ASSO S.L.A.V.É. - Savoir • Langue • Art • Voyage • Échange",
        "asso_desc": "ASSO S.L.A.V.É. is an intellectual laboratory bringing together people from diverse backgrounds around creative, educational, and sustainable projects.",
        "dignity_title": "Right to Dignity - ASSO S.L.A.V.É.",
        "contact_title": "Contact - ASSO S.L.A.V.É.",
        "hero_cta": "Watch the student films",
        "films_h2": "Student films",
        "films_lede": "Short films made in class at our partner universities. Each cohort builds a scenario over a term, then shoots and edits it themselves.",
        "films_all": "See all films",
        "films_search": "Search a film, a team or a school",
        "history_title": "History &amp; Values",
        "history_hint": "Founded in 2007 at Université Bordeaux Montaigne. How the association got here.",
        "moved": "This page moved to",
    },
    "fr": {
        "dir": "fr/", "pre": "/fr",
        "nav": [("", "Les Rails du Temps"), ("films/", "Films"), ("asso/", "Asso"), ("dignity/", "Droit à la Dignité")],
        "contact": "Contact",
        "home_title": "Les Rails du Temps - ASSO S.L.A.V.É.",
        "home_desc": "Les Rails du Temps est un projet inter-universitaire de l'ASSO S.L.A.V.É. : des étudiants conçoivent des itinéraires, tournent des courts-métrages et racontent les histoires vivantes des lieux qui façonnent les territoires français.",
        "asso_title": "ASSO S.L.A.V.É. - Savoir • Langue • Art • Voyage • Échange",
        "asso_desc": "ASSO S.L.A.V.É. est un laboratoire intellectuel réunissant des personnes de tous horizons autour de projets créatifs, éducatifs et durables.",
        "dignity_title": "Droit à la Dignité - ASSO S.L.A.V.É.",
        "contact_title": "Contact - ASSO S.L.A.V.É.",
        "hero_cta": "Voir les films des étudiants",
        "films_h2": "Les films des étudiants",
        "films_lede": "Des courts-métrages réalisés en cours dans nos universités partenaires. Chaque promotion construit un scénario sur un semestre, puis tourne et monte elle-même.",
        "films_all": "Voir tous les films",
        "films_search": "Chercher un film, une équipe ou une école",
        "history_title": "Histoire &amp; Valeurs",
        "history_hint": "Fondée en 2007 à l'Université Bordeaux Montaigne. Comment l'association en est arrivée là.",
        "moved": "Cette page a déménagé :",
    },
}

# old relative link -> new path (relative to the language root)
OLD_TO_NEW = {"index.html": "", "association.html": "asso/", "projects.html": "", "dignity.html": "dignity/",
              "films.html": "films/", "contact.html": "contact/"}


def read(lang, name):
    return (ROOT / L[lang]["dir"] / name).read_text(encoding="utf-8")


def sections(html):
    body = html[html.find("<body"):]
    return re.split(r"(?=<section )", body)


def nav_html(lang, active):
    links = "".join(f'<a {LINK_ACTIVE if p == active else LINK_IDLE} href="{L[lang]["pre"]}/{p}">{label}</a>'
                    for p, label in L[lang]["nav"])
    return f'<nav class="hidden md:flex items-center space-x-8">{links}</nav>'


def common(html, lang, page, title, desc):
    """Nav, footer links, absolute assets, internal links, head metadata. `page` is '' | 'asso/' | ..."""
    pre = L[lang]["pre"]
    # assets -> absolute
    html = re.sub(r'(href|src)="(?:\.\./)?assets/', r'\1="/assets/', html)
    # internal links (root-relative within the language)
    for old, new in OLD_TO_NEW.items():
        html = html.replace(f'href="{old}"', f'href="{pre}/{new}"')
    # nav
    html, n = re.subn(r"<nav .*?</nav>", nav_html(lang, page), html, count=1, flags=re.S)
    assert n == 1, "nav not found"
    # footer quick links: keep the <li> template, rebuild the list
    m = re.search(r'(<h4[^>]*>[^<]*<span[^>]*></span></h4>)<ul class="space-y-4">(<li>.*?</li>)</ul>', html, re.S)
    assert m, "footer quick links not found"
    li = re.search(r"<li>.*?</li>", m.group(2), re.S).group(0)
    items = list(L[lang]["nav"]) + [("contact/", L[lang]["contact"])]
    lis = "".join(re.sub(r'href="[^"]*"', f'href="{pre}/{p}"', re.sub(r"</span>[^<]*</a>", f"</span>{label}</a>", li, count=1), count=1)
                  for p, label in items)
    html = html[:m.start(2)] + lis + html[m.end(2):]
    # brand header wordmark is a <button>; clone.js sends it home. Nothing to do here.
    # head
    en, fr = HOST + page, HOST + "fr/" + page
    here = HOST + L[lang]["dir"] + page
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), html, count=1)
    for prop in ("og:title", "twitter:title"):
        html = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(")', lambda m: m.group(1) + title + m.group(2), html, count=1)
    for prop in ("og:description", "twitter:description"):
        html = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + here + m.group(2), html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{here}">', html, count=1)
    html = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{en}">', html, count=1)
    html = re.sub(r'<link rel="alternate" hreflang="fr" href="[^"]*">', f'<link rel="alternate" hreflang="fr" href="{fr}">', html, count=1)
    html = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{en}">', html, count=1)
    if not re.search(r"<html[^>]*\blang=", html):
        html = re.sub(r"<html", f'<html lang="{lang}"', html, count=1)
    return html


def build_home(lang):
    """/ = the Rails of Time page + hero CTA + films stage."""
    T = L[lang]
    html = read(lang, "projects.html")
    # the empty strip under the hero
    strip = '<section class="py-12 bg-[#F8F7F4] border-b border-gray-200"><div class="container mx-auto px-4 text-center"></div></section>'
    assert strip in html, "empty strip not found"
    films = (
        f'<section class="rot-films" id="films" aria-labelledby="rot-films-title"><div class="container mx-auto px-4 md:px-8">'
        f'<div class="rot-films-head"><div><h2 id="rot-films-title">{T["films_h2"]}</h2><p>{T["films_lede"]}</p></div>'
        f'<a class="rot-films-all" href="{T["pre"]}/films/">{T["films_all"]}</a></div>'
        f'<div class="rot-stage" id="rot-films" data-search="{T["films_search"]}"></div>'
        f'</div></section>'
    )
    html = html.replace(strip, films, 1)
    # hero CTA, after the hero paragraph
    hero_p = re.search(r'<p class="text-xl text-white/90 max-w-3xl"[^>]*>.*?</p>', html, re.S)
    assert hero_p, "hero paragraph not found"
    cta = (f'<div class="flex flex-col sm:flex-row gap-5 mt-10"><a class="bg-gradient-to-r from-[#EF4444] to-[#DC2626] text-white text-lg font-bold px-12 py-5 rounded-full hover:-translate-y-1 hover:scale-105 transition-all duration-300 inline-flex items-center justify-center gap-3" href="#films" style="box-shadow: rgba(192, 105, 63, 0.4) 0px 8px 24px;">{PLAY_SVG}{T["hero_cta"]}</a></div>')
    html = html[:hero_p.end()] + cta + html[hero_p.end():]
    html = common(html, lang, "", T["home_title"], T["home_desc"])
    html = html.replace('<link rel="stylesheet" href="/assets/clone-fixes.css">',
                        '<link rel="stylesheet" href="/assets/clone-fixes.css">\n    <link rel="stylesheet" href="/assets/showcase.css">', 1)
    assert "showcase.css" in html
    html, n = re.subn(r'(<script src="/assets/clone\.js"[^>]*>\s*</script>)', r'\1<script src="/assets/showcase.js" defer=""></script>', html, count=1)
    assert n == 1, "clone.js tag not found"
    return html


def build_asso(lang):
    """/asso/ = the old home with the association page folded into its About block."""
    T = L[lang]
    home = read(lang, "index.html")
    asso = read(lang, "association.html")
    hs = sections(home)
    about_old = hs[3]
    assert "ASSO S.L.A.V.É.</h2>" in about_old and about_old.startswith('<section class="py-28'), "home About block not where expected"
    a_secs = sections(asso)
    intro = re.search(r'<div class="space-y-6 text-lg[^"]*">(.*?)</div>', a_secs[3], re.S).group(1)
    history = re.search(r'<div class="mt-20 space-y-6[^"]*">(.*?)</div>', a_secs[4], re.S).group(1)
    assert intro.count("<p>") == 2 and history.count("<p") == 7, (intro.count("<p>"), history.count("<p"))
    eyebrow = re.search(r'<div class="inline-block px-5 py-2 rounded-full[^>]*>.*?</div>', about_old, re.S).group(0)
    figure = re.search(r"<figure.*?</figure>", about_old, re.S).group(0)
    about_new = (
        '<section class="py-28 bg-[#F8F7F4]" id="about"><div class="container mx-auto px-4 md:px-8"><div class="max-w-6xl mx-auto">'
        '<div class="grid lg:grid-cols-2 gap-16 items-center"><div class="fade-in-up animate-fade-in-up">'
        f'{eyebrow}<h2 class="text-4xl md:text-5xl font-extrabold text-[#003D6B] mb-6">ASSO S.L.A.V.É.</h2>'
        f'<div class="space-y-5 text-lg text-[#6B7280] leading-relaxed">{intro}</div></div>{figure}</div>'
        f'<details class="slave-history" id="history"><summary><span class="slave-history-title">{T["history_title"]}</span>'
        f'<span class="slave-history-hint">{T["history_hint"]}</span><span class="slave-history-chevron" aria-hidden="true">{CHEVRON_SVG}</span></summary>'
        f'<div class="slave-history-body">{history}</div></details>'
        '</div></div></section>'
    )
    html = home.replace(about_old, about_new, 1)
    # hero: "Learn About Us" now scrolls to the block below instead of leaving the page
    html, n = re.subn(r'href="association\.html"( style="box-shadow: rgba\(255, 255, 255, 0\.2\))', r'href="#about"\1', html, count=1)
    assert n == 1, "hero secondary CTA not found"
    return common(html, lang, "asso/", T["asso_title"], T["asso_desc"])


def build_plain(lang, old, page, title):
    html = read(lang, old)
    desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
    return common(html, lang, page, title, desc)


def stub(lang, new):
    T = L[lang]
    target = f'{T["pre"]}/{new}'
    return (f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><title>{HOST}{T["dir"]}{new}</title>'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{HOST}{T["dir"]}{new}">'
            f'<meta http-equiv="refresh" content="0; url={target}">'
            f'<script>location.replace("{target}"+location.search+location.hash)</script></head>'
            f'<body><p>{T["moved"]} <a href="{target}">railsoftime.fr{target}</a></p></body></html>\n')


def main():
    out = {}
    for lang in L:
        d = ROOT / L[lang]["dir"]
        out[d / "index.html"] = build_home(lang)
        out[d / "asso" / "index.html"] = build_asso(lang)
        out[d / "dignity" / "index.html"] = build_plain(lang, "dignity.html", "dignity/", L[lang]["dignity_title"])
        out[d / "contact" / "index.html"] = build_plain(lang, "contact.html", "contact/", L[lang]["contact_title"])
        # 404 keeps its file name (GitHub Pages convention) and its own title; only chrome + links change
        html = read(lang, "404.html")
        t = re.search(r"<title>(.*?)</title>", html).group(1)
        desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
        out[d / "404.html"] = common(html, lang, "", t, desc)
        for old, new in OLD_TO_NEW.items():
            if old != "index.html":
                out[d / old] = stub(lang, new)
    for p, s in out.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(s, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
