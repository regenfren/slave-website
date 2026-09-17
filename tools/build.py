#!/usr/bin/env python3
"""Build every page of the site in the S.L.A.V.É. brand, English and French.

    python3 tools/build.py            write all pages
    python3 tools/build.py --check    build in memory and fail if a written page is out of date

Copy lives in content/en.json and content/fr.json (captured from the pre-brand site on
2026-09-16, same words and same section order). Edit the copy there, never in the HTML.
This script replaces tools/nav.py and tools/films-pages.py: header, footer and navigation are
written here for every page, and the films.json schools rule from films-pages.py is enforced here.

Brand (Tim, 2026-09-16): the system of the film-led redesign proposal. Jost + Literata, ink / rust /
paper, the logo recoloured with rust rails, 2px corners, no shadows, real photos in one warm colour
film grade (tools/photo-grade.py), the student-film reel as the home header. Two deliberate changes to the old structure,
both Tim's: About the Project sits above the films, and every partner section is logos only.
"""
import html
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://railsoftime.fr/"
PHOTOS = json.loads((ROOT / "assets/brand/photos/map.json").read_text())
# Where the faces are in each graded photo (tools/photo-grade.py -> Vision). Every crop centres on
# this point, so no slot on any screen size cuts a face in half.
FOCAL = json.loads((ROOT / "assets/brand/photos/focal.json").read_text())
_dims = {}

# The reel's cut points (seconds, after the 10% slowdown), written by tools/reel/build.py.
REEL = [tuple(c) for c in json.loads((ROOT / "tools/reel/cuts.json").read_text())]
REEL_FILES = {  # crop -> [(codec, MIME type with codec string)], in preference order
    "wide": [("av1", 'video/mp4; codecs="av01.0.08M.10"'), ("hevc", 'video/mp4; codecs="hvc1.1.6.L120.90"'), ("h264", 'video/mp4; codecs="avc1.640028"')],
    "phone": [("av1", 'video/mp4; codecs="av01.0.04M.10"'), ("hevc", 'video/mp4; codecs="hvc1.1.6.L93.90"'), ("h264", 'video/mp4; codecs="avc1.64001f"')],
}
REEL_SIZE = {"wide": (1600, 680), "phone": (642, 856)}
REEL_SECONDS = 35.2


def reel_sources():
    out = {}
    for crop, files in REEL_FILES.items():
        w, h = REEL_SIZE[crop]
        out[crop] = []
        for codec, mime in files:
            f = ROOT / f"assets/brand/reel/reel-{crop}.{codec}.mp4"
            if f.exists():
                out[crop].append({"src": f"/assets/brand/reel/reel-{crop}.{codec}.mp4", "type": mime, "w": w, "h": h,
                                  "bitrate": int(f.stat().st_size * 8 / REEL_SECONDS)})
    return out


UI = {
    "en": {"skip": "Skip to content", "home": "S.L.A.V.É., home", "menu": "Menu", "now": "Now showing", "pause": "Pause",
           "schools": {"cafa": "CAFA, Beijing", "kedge": "KEDGE, Bordeaux", "cnam": "CNAM, Dax"}, "main": "Main"},
    "fr": {"skip": "Aller au contenu", "home": "S.L.A.V.É., accueil", "menu": "Menu", "now": "À l’écran", "pause": "Pause",
           "schools": {"cafa": "CAFA, Pékin", "kedge": "KEDGE, Bordeaux", "cnam": "CNAM, Dax"}, "main": "Principal"},
}
PAGES = {"home": "", "asso": "asso/", "films": "films/", "dignity": "dignity/", "contact": "contact/", "404": "404.html"}
HERO_IMG = {"asso": "asso", "dignity": "dignity", "contact": "contact"}


def e(s):
    return html.escape(s or "", quote=True)


def dims(src):
    if src not in _dims:
        with Image.open(ROOT / src.lstrip("/")) as im:
            _dims[src] = im.size
    return _dims[src]


def photo(src, alt="", cls="", lazy=True):
    """A real photo, served in the warm film grade (tools/photo-grade.py), cropped around its faces."""
    s = PHOTOS.get(src, src)
    w, h = dims(s)
    f = FOCAL.get(s)
    pos = f' style="object-position:{f[0]}% {f[1]}%"' if f else ""
    return (f'<img src="{e(s)}" alt="{e(alt)}" width="{w}" height="{h}"{pos}'
            f'{" loading=\"lazy\" decoding=\"async\"" if lazy else ""}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>')


def url(lang, key):
    path = PAGES[key]
    if key == "404":
        return "/fr/404.html" if lang == "fr" else "/404.html"
    return ("/fr/" if lang == "fr" else "/") + path


def para(text):
    return f"<p>{e(text)}</p>" if text else ""


# ----------------------------------------------------------------- shell
def head(C, key, extra=""):
    h = C["pages"][key]["head"]
    css = {"home": ["/assets/schools.css", "/assets/showcase.css"], "films": ["/assets/schools.css", "/assets/films.css"]}.get(key, [])
    preload = ""
    if key == "home":
        preload = ('<link rel="preload" as="image" href="/assets/brand/reel/poster-phone.webp" media="(max-width: 760px)" fetchpriority="high">'
                   '<link rel="preload" as="image" href="/assets/brand/reel/poster-wide.webp" media="(min-width: 761px)" fetchpriority="high">')
    elif key in HERO_IMG:
        n = HERO_IMG[key]
        preload = (f'<link rel="preload" as="image" href="/assets/brand/hero/{n}-960.webp" media="(max-width: 960px)" fetchpriority="high">'
                   f'<link rel="preload" as="image" href="/assets/brand/hero/{n}-1920.webp" media="(min-width: 961px)" fetchpriority="high">')
    return (
        f'<!DOCTYPE html>\n<html lang="{C["lang"]}"><head>\n'
        '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'
        f'<title>{e(h["title"])}</title>\n' + "\n".join(h["tags"]) + "\n"
        '<meta name="theme-color" content="#0b1117">\n'
        '<link rel="icon" href="/assets/brand/img/favicon-64.png" type="image/png" sizes="64x64">\n'
        '<link rel="apple-touch-icon" href="/assets/brand/img/apple-touch-icon.png">\n'
        '<link rel="preload" href="/assets/brand/fonts/jost-normal-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
        '<link rel="preload" href="/assets/brand/fonts/literata-normal-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
        f'{preload}\n<link rel="stylesheet" href="/assets/brand/fonts.css">\n<link rel="stylesheet" href="/assets/brand/brand.css">\n'
        + "".join(f'<link rel="stylesheet" href="{c}">\n' for c in css) + extra + "</head>\n<body>\n"
    )


def header(C, key):
    lang, N, U = C["lang"], C["nav"], UI[C["lang"]]
    other = "en" if lang == "fr" else "fr"
    here, there = url(lang, key), url(other, key)

    def cur(k):
        return ' aria-current="page"' if k == key else ""

    items = [("home", N["items"][0]), ("dignity", N["items"][1]), ("films", N["items"][2])]
    in_projects = key in ("home", "dignity", "films")
    menu = "".join(f'<a href="{e(a["href"])}"{cur(k)}>{e(a["text"])}</a>' for k, a in items)
    langs = (f'<span class="lang"><span aria-current="true">{lang.upper()}</span><span aria-hidden="true">/</span>'
             f'<a href="{e(there)}" hreflang="{other}" lang="{other}">{other.upper()}</a></span>')
    mobile = (f'<a href="{e(N["asso"]["href"])}">{e(N["asso"]["text"])}</a>' + menu +
              f'<a href="{e(N["contact"]["href"])}">{e(N["contact"]["text"])}</a>' + langs)
    return (
        f'<a class="skip" href="#main">{e(U["skip"])}</a>\n'
        '<header class="site-header"><div class="wrap">'
        f'<a class="brand" href="{url(lang, "home")}" aria-label="{e(U["home"])}"><img src="/assets/brand/img/mark-paper.webp" alt="" width="70" height="40"><span>{e(C["brand"])}</span></a>'
        f'<nav class="nav" aria-label="{e(U["main"])}">'
        f'<a href="{e(N["asso"]["href"])}"{cur("asso")}>{e(N["asso"]["text"])}</a>'
        f'<div class="nav-projects{" is-current" if in_projects else ""}"><button type="button" aria-haspopup="true" aria-expanded="false">{e(N["projects"])}</button>'
        f'<div class="nav-menu">{menu}</div></div>'
        f'{langs}<a class="btn btn-line" href="{e(N["contact"]["href"])}"{cur("contact")}>{e(N["contact"]["text"])}</a>'
        '</nav>'
        f'<button class="burger" type="button" aria-expanded="false" aria-controls="mobile-menu">{e(U["menu"])}</button>'
        f'</div><nav class="mobile-menu" id="mobile-menu" aria-label="{e(U["main"])}">{mobile}</nav></header>\n'
    )


def footer(C, scripts=""):
    F = C["footer"]
    quick = "".join(f'<li><a href="{e(a["href"])}">{e(a["text"])}</a></li>' for a in F["quick"])
    contact = ""
    for c in F["contact"]:
        contact += (f'<li><a href="{e(c["href"])}">{e(c["text"])}</a></li>' if "href" in c
                    else "<li>" + "<br>".join(e(x) for x in c["lines"]) + "</li>")
    legal = "".join(f"<span>{e(x)}</span>" for x in F["legal"])
    return (
        '<footer class="site-footer"><div class="wrap">'
        f'<div><img class="logo" src="/assets/brand/img/logo-paper.webp" alt="{e(F["brand"])}" width="104" height="94" loading="lazy">'
        f'<p class="tag">{e(F["tagline"])}</p><p class="about">{e(F["about"])}</p></div>'
        f'<div><h4>{e(F["quickTitle"])}</h4><ul>{quick}</ul></div>'
        f'<div><h4>{e(F["contactTitle"])}</h4><ul>{contact}</ul></div>'
        f'<p class="legal"><span>{e(F["copyright"])}</span><span>{legal}</span></p>'
        '</div></footer>\n'
        '<script src="/assets/brand/site.js" defer></script>\n' + scripts + "</body></html>\n"
    )


# ----------------------------------------------------------------- shared blocks
def hero(key, P, lang, actions=""):
    n = HERO_IMG[key]
    return (
        f'<section class="hero" aria-labelledby="hero-title"><div class="hero-media">'
        f'<picture><source media="(max-width: 960px)" srcset="/assets/brand/hero/{n}-960.webp">'
        f'<img src="/assets/brand/hero/{n}-1920.webp" alt="" fetchpriority="high"></picture></div>'
        f'<div class="hero-copy"><div class="wrap"><div><h1 id="hero-title">{e(P["h1"])}</h1><p class="lede">{e(P["lede"])}</p>{actions}</div></div></div></section>\n'
    )


def numbered(items):
    return '<ol class="numbered">' + "".join(
        f'<li><span class="n" aria-hidden="true">{e(i["n"])}</span><h3>{e(i["h3"])}</h3>{para(i["p"])}</li>' for i in items) + "</ol>"


def people_groups(T, band=""):
    out = f'<section class="{band}"><div class="wrap"><div class="head"><div><h2>{e(T["h2"])}</h2>{para(T.get("lede"))}</div></div>'
    for g in T["groups"]:
        out += f'<div class="group"><h3>{e(g["h3"])}</h3><ul class="people">'
        for p in g["people"]:
            out += f'<li class="person">{photo(p["img"], "")}<b>{e(p["name"])}</b>' + "".join(f"<span>{e(r)}</span>" for r in p["role"]) + "</li>"
        out += "</ul></div>"
    return out + "</div></section>\n"


def partners(C, h2, band=""):
    logos = "".join(
        f'<a href="{e(l["href"])}" target="_blank" rel="noopener" title="{e(l["name"])}">'
        f'<img src="{e(l["img"])}" alt="{e(l["name"])}" width="{dims(l["img"])[0]}" height="{dims(l["img"])[1]}" loading="lazy"></a>'
        for l in C["partners"])
    return (f'<section class="partners {band}"><div class="wrap"><div class="head"><h2>{e(h2)}</h2></div>'
            f'<div class="logos">{logos}</div></div></section>\n')


def cta(T):
    return (f'<section class="band-ink cta"><div class="wrap"><div><h2>{e(T["h2"])}</h2>{para(T["p"])}'
            f'<div class="actions"><a class="btn btn-rust" href="{e(T["a"]["href"])}">{e(T["a"]["text"])}</a></div></div>'
            '<img class="mark" src="/assets/brand/img/logo-paper.webp" alt="" width="220" height="199" loading="lazy"></div></section>\n')


# ----------------------------------------------------------------- pages
def page_home(C):
    P, lang, U = C["pages"]["home"], C["lang"], UI[C["lang"]]
    H, A = P["hero"], P["about"]
    cuts = json.dumps([[t, f, U["schools"][s]] for t, f, s in REEL], ensure_ascii=False)
    first = REEL[0]
    out = head(C, "home") + header(C, "home") + '<main id="main">\n'
    out += (
        f'<section class="hero hero-home" aria-labelledby="hero-title"><div class="hero-media">'
        '<picture><source media="(max-width: 760px)" srcset="/assets/brand/reel/poster-phone.webp">'
        '<img src="/assets/brand/reel/poster-wide.webp" alt="" width="1920" height="816" fetchpriority="high"></picture>'
        '<video muted loop playsinline preload="none" aria-hidden="true" '
        f"data-sources='{e(json.dumps(reel_sources()))}' data-credits='{e(cuts)}'></video></div>"
        f'<div class="hero-copy"><div class="wrap"><div><h1 id="hero-title">{e(H["h1"])}</h1><p class="lede">{e(H["lede"])}</p>'
        f'<div class="actions"><a class="btn btn-rust" href="{e(H["cta"]["href"])}">{e(H["cta"]["text"])}</a></div></div>'
        f'<div class="credit" aria-live="polite">{e(U["now"])}<strong data-film>{e(first[1])}</strong><span data-school>{e(U["schools"][first[2]])}</span><br>'
        f'<button type="button">{e(U["pause"])}</button></div></div></div></section>\n'
    )
    paras = A["paras"]
    out += (f'<section id="about"><div class="wrap intro"><h2 class="h2">{e(A["h2"])}</h2><div class="body">'
            f'<p class="lead">{e(paras[0])}</p><div class="cols">{"".join(para(p) for p in paras[1:])}</div></div></div></section>\n')
    F = P["films"]
    out += (f'<section class="rot-films" id="films" aria-labelledby="rot-films-title"><div class="wrap">'
            f'<div class="rot-films-head"><div><h2 id="rot-films-title">{e(F["h2"])}</h2>{para(F["lede"])}</div>'
            f'<a class="rot-films-all" href="{e(F["all"]["href"])}">{e(F["all"]["text"])}</a></div>'
            f'<div class="rot-stage" id="rot-films" data-search="{e(F["search"])}"></div></div></section>\n')
    O = P["objectives"]
    out += f'<section class="band-2"><div class="wrap"><div class="head"><h2>{e(O["h2"])}</h2></div>{numbered(O["items"])}</div></section>\n'
    L = P["outline"]
    out += f'<section><div class="wrap"><div class="head"><div><h2>{e(L["h2"])}</h2>{para(L["lede"])}</div></div><div class="phases">'
    for ph in L["phases"]:
        out += (f'<article class="phase"><span class="label">{e(ph["label"])}</span><h3>{e(ph["h3"])}</h3>{para(ph["p"])}'
                + (f"<blockquote><p>{e(ph['quote'])}</p></blockquote>" if ph["quote"] else "")
                + f'<h4>{e(ph["involvedTitle"])}</h4><ul class="plain-list">' + "".join(f"<li>{e(x)}</li>" for x in ph["involved"]) + "</ul></article>")
    out += "</div></div></section>\n"
    out += people_groups(P["team"], "band-2")
    out += partners(C, P["partners"]["h2"])
    out += cta(P["cta"])
    return out + "</main>\n" + footer(C, '<script src="/assets/schools.js" defer></script>\n<script src="/assets/showcase.js" defer></script>\n')


def page_asso(C):
    P, lang = C["pages"]["asso"], C["lang"]
    H = P["hero"]
    acts = ('<div class="actions">' + f'<a class="btn btn-rust" href="{e(H["ctas"][0]["href"])}">{e(H["ctas"][0]["text"])}</a>'
            + f'<a class="btn btn-line" href="{e(H["ctas"][1]["href"])}">{e(H["ctas"][1]["text"])}</a></div>')
    out = head(C, "asso") + header(C, "asso") + '<main id="main">\n' + hero("asso", H, lang, acts)
    A = P["about"]
    out += (f'<section id="about"><div class="wrap"><div class="about-grid"><div class="body"><h2 class="h2">{e(A["h2"])}</h2>'
            + "".join(para(p) for p in A["paras"]) + '</div>'
            f'<figure>{photo(A["img"]["src"], A["img"]["alt"])}<figcaption>{e(A["caption"])}</figcaption></figure></div>'
            f'<details class="history"><summary><b>{e(A["history"]["title"])}</b><span>{e(A["history"]["hint"])}</span></summary>'
            f'<div class="body">{"".join(para(p) for p in A["history"]["paras"])}</div></details></div></section>\n')
    PI = P["pillars"]
    out += (f'<section class="band-2"><div class="wrap"><div class="head"><div><h2>{e(PI["h2"])}</h2>{para(PI["lede"])}</div></div><ul class="pillars">'
            + "".join(f'<li><span class="letter" aria-hidden="true">{e(i["letter"])}</span><h3>{e(i["h3"])}</h3>{para(i["p"])}</li>' for i in PI["items"])
            + "</ul></div></section>\n")
    FE = P["featured"]
    out += f'<section class="band-ink" id="featured"><div class="wrap"><div class="head"><div><h2>{e(FE["h2"])}</h2>{para(FE["lede"])}</div></div><div class="duo">'
    for it in FE["items"]:
        out += (f'<article>{photo(it["img"]["src"], it["img"]["alt"])}<h3>{e(it["h3"])}</h3>{para(it["p"])}'
                f'<a class="btn btn-ink" href="{e(it["a"]["href"])}">{e(it["a"]["text"])}</a></article>')
    out += "</div></div></section>\n"
    out += people_groups(P["team"])
    out += partners(C, P["partners"]["h2"], "band-2")
    out += cta(P["cta"])
    return out + "</main>\n" + footer(C)


def page_dignity(C):
    P, lang = C["pages"]["dignity"], C["lang"]
    out = head(C, "dignity") + header(C, "dignity") + '<main id="main">\n' + hero("dignity", P["hero"], lang)
    O = P["objectives"]
    out += f'<section class="band-2"><div class="wrap"><div class="head"><h2>{e(O["h2"])}</h2></div>{numbered(O["items"])}</div></section>\n'
    AR = P["areas"]
    out += f'<section><div class="wrap"><div class="head"><div><h2>{e(AR["h2"])}</h2>{para(AR["lede"])}</div></div><div class="rows">'
    for it in AR["items"]:
        pics = "".join(photo(i["src"], i["alt"]) for i in it["imgs"])
        out += (f'<article class="row"><div class="pics{" one" if len(it["imgs"]) == 1 else ""}">{pics}</div>'
                f'<div><h3>{e(it["h3"])}</h3>{para(it["p"])}<ul class="plain-list">' + "".join(f"<li>{e(b)}</li>" for b in it["bullets"]) + "</ul></div></article>")
    out += "</div></div></section>\n"
    FU = P["furniture"]
    out += (f'<section class="band-2"><div class="wrap"><div class="head"><div><h2>{e(FU["h2"])}</h2>{para(FU["lede"])}</div></div><div class="trio">'
            + "".join(f'<figure>{photo(i["src"], i["label"])}<figcaption>{e(i["label"])}</figcaption></figure>' for i in FU["items"])
            + "</div></div></section>\n")
    ON = P["ongoing"]
    out += f'<section><div class="wrap"><div class="head"><h2>{e(ON["h2"])}</h2></div><div class="duo">'
    for it in ON["items"]:
        out += (f'<article>{photo(it["img"]["src"], it["img"]["alt"])}<h3>{e(it["h3"])}</h3>{para(it["p"])}'
                '<ul class="plain-list">' + "".join(f"<li>{e(b)}</li>" for b in it["bullets"]) + "</ul></article>")
    out += "</div></div></section>\n"
    G = P["gallery"]
    out += (f'<section class="band-ink"><div class="wrap"><div class="head"><h2>{e(G["h2"])}</h2></div>'
            f'<div class="strip" tabindex="0" role="region" aria-label="{e(G["h2"])}">' + "".join(photo(i["src"], i["alt"]) for i in G["imgs"]) + "</div></div></section>\n")
    S = P["scope"]
    out += f'<section class="band-2"><div class="wrap"><div class="scope"><h2>{e(S["h3"])}</h2>{"".join(para(p) for p in S["paras"])}</div></div></section>\n'
    out += cta(P["cta"])
    return out + "</main>\n" + footer(C)


def page_contact(C):
    P, lang = C["pages"]["contact"], C["lang"]
    out = head(C, "contact") + header(C, "contact") + '<main id="main">\n' + hero("contact", P["hero"], lang)
    Fo = P["form"]
    fields = ""
    for i, f in enumerate(Fo["fields"], 1):
        fid = f"contact-f{i}"
        req = " required" if f["required"] else ""
        ctrl = (f'<textarea id="{fid}" name="{e(f["name"])}" placeholder="{e(f["placeholder"])}"{req}></textarea>' if f["type"] == "textarea"
                else f'<input id="{fid}" name="{e(f["name"])}" type="{e(f["type"])}" placeholder="{e(f["placeholder"])}"{req}>')
        fields += f'<div class="field"><label for="{fid}">{e(f["label"])}</label>{ctrl}</div>'
    info = ""
    for it in P["info"]["items"]:
        v = f'<a href="{e(it["href"])}">{e(it["value"])}</a>' if it.get("href") else e(it["value"])
        info += f"<div><dt>{e(it['label'])}</dt><dd>{v}</dd></div>"
    legal = "".join(f"<div><dt>{e(k.rstrip(' :').rstrip(':'))}</dt><dd>{e(v)}</dd></div>" for k, v in P["legal"]["rows"])
    out += (f'<section><div class="wrap contact-grid">'
            f'<div><h2>{e(Fo["h2"])}</h2><form class="form" data-static novalidate>{fields}'
            f'<button class="btn btn-solid" type="submit">{e(Fo["button"])}</button><p class="form-note" aria-live="polite"></p></form></div>'
            f'<div><h2>{e(P["info"]["h2"])}</h2><dl class="facts">{info}</dl>'
            f'<h2>{e(P["legal"]["h2"])}</h2><dl class="facts">{legal}</dl>'
            f'<div class="since"><h3>{e(P["since"]["h3"])}</h3>{para(P["since"]["p"])}</div></div>'
            "</div></section>\n")
    return out + "</main>\n" + footer(C)


def page_films(C):
    P = C["pages"]["films"]
    out = head(C, "films") + header(C, "films") + '<main id="main">\n'
    out += (f'<section class="page-top films-hero"><div class="wrap"><h1>{e(P["hero"]["h1"])}</h1>{para(P["hero"]["lede"])}'
            '<p class="films-count" id="films-count"></p></div></section>\n'
            f'<div id="films" class="wrap"><h2 class="films-sr">{e(P["h2sr"])}</h2></div>\n')
    return out + "</main>\n" + footer(C, '<script src="/assets/schools.js"></script>\n<script src="/assets/films.js" data-assets="/assets/"></script>\n')


def page_404(C):
    P = C["pages"]["404"]
    out = head(C, "404") + header(C, "404") + '<main id="main">\n'
    out += (f'<section class="page-top notfound"><div class="wrap"><img class="mark" src="/assets/brand/img/logo-paper.webp" alt="" width="120" height="109">'
            f'<h1>{e(P["h1"])}</h1><h2>{e(P["h2"])}</h2>{para(P["p"])}'
            f'<div class="actions"><a class="btn btn-rust" href="{e(P["home"]["href"])}">{e(P["home"]["text"])}</a>'
            f'<button class="btn btn-line" type="button" data-back>{e(P["back"])}</button></div></div></section>\n')
    return out + "</main>\n" + footer(C)


BUILDERS = {"home": page_home, "asso": page_asso, "films": page_films, "dignity": page_dignity, "contact": page_contact, "404": page_404}


def check_schools():
    """films-pages.py's rule, kept: every school with a published film has name, city, logo file and a tagline in both languages."""
    d = json.loads((ROOT / "assets/films.json").read_text(encoding="utf-8"))
    used = {f["school"] for f in d.get("films", []) if f.get("youtube")}
    bad = []
    for sid in sorted(used):
        s = d["schools"].get(sid, {})
        tag = s.get("tagline") or {}
        missing = [k for k, ok in (("name", bool(s.get("name"))), ("city", bool(s.get("city"))),
                                    ("logo", bool(s.get("logo")) and (ROOT / s.get("logo", "")).exists()),
                                    ("tagline.en", bool(tag.get("en"))), ("tagline.fr", bool(tag.get("fr")))) if not ok]
        if missing:
            bad.append(f"{sid}: missing {', '.join(missing)}")
    if bad:
        sys.exit("films.json schools rule broken:\n  " + "\n  ".join(bad))


def target(lang, key):
    base = ROOT / ("fr" if lang == "fr" else "")
    return base / PAGES[key] if key == "404" else base / PAGES[key] / "index.html"


def main():
    check_schools()
    stale = []
    for lang in ("en", "fr"):
        C = json.loads((ROOT / f"content/{lang}.json").read_text(encoding="utf-8"))
        for key, build in BUILDERS.items():
            html_out = build(C)
            dest = target(lang, key)
            if "--check" in sys.argv:
                if not dest.exists() or dest.read_text(encoding="utf-8") != html_out:
                    stale.append(str(dest.relative_to(ROOT)))
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(html_out, encoding="utf-8")
                print("wrote", dest.relative_to(ROOT))
    if stale:
        sys.exit("out of date, run python3 tools/build.py:\n  " + "\n  ".join(stale))


if __name__ == "__main__":
    main()
