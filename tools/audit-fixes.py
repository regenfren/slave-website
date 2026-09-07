#!/usr/bin/env python3
"""Apply the 2026-09-07 audit fixes to every page. Idempotent; run from the repo root.

- Google Fonts links -> local assets/fonts.css (+ preload of the two body faces)
- favicon -> assets/favicon-64.png, apple-touch-icon
- canonical + hreflang (en/fr/x-default) on every page
- home: the brand line above the real title was a second <h1>; it is a <p> now
- contact: labels associated with their inputs (for/id); the dead href="#" card is a <div>
- robots.txt + sitemap.xml
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://railsoftime.fr/"
PAGES = ["index.html", "association.html", "projects.html", "dignity.html", "contact.html", "films.html", "404.html"]
SITEMAP_PAGES = [p for p in PAGES if p != "404.html"]


def canon(dirprefix: str, page: str) -> str:
    return HOST + dirprefix + ("" if page == "index.html" else page)


def fix_page(path: Path, dirprefix: str) -> list[str]:
    a = "../assets/" if dirprefix else "assets/"
    s = path.read_text(encoding="utf-8")
    orig = s
    done = []

    # fonts: drop the Google links, add local css + preloads (before site.css)
    s2 = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.g[^"]*"[^>]*>', "", s)
    s2 = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">', "", s2)
    if "fonts.css" not in s2:
        # the site.css tag carries crossorigin before href; match it by href, whatever the attribute order
        s2 = re.sub(rf'(<link[^>]*href="{re.escape(a)}site\.css"[^>]*>)',
            lambda m: (f'<link rel="preload" href="{a}fonts/hanken-grotesk-normal-400-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
                       f'    <link rel="preload" href="{a}fonts/fraunces-normal-400-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
                       f'    <link rel="stylesheet" href="{a}fonts.css">\n    ' + m.group(1)), s2, count=1)
        if "fonts.css" not in s2:
            raise SystemExit(f"{path}: could not find the site.css link to hang fonts.css on")
    if s2 != s:
        done.append("fonts"); s = s2

    # favicon + apple touch icon
    s2 = s.replace(f'<link rel="icon" href="{a}logo.png" type="image/png">',
                   f'<link rel="icon" href="{a}favicon-64.png" type="image/png" sizes="64x64">\n    <link rel="apple-touch-icon" href="{a}apple-touch-icon.png">')
    if s2 != s:
        done.append("favicon"); s = s2

    # canonical + hreflang
    page = path.name
    if 'rel="canonical"' not in s and page != "404.html":
        en, fr = canon("", page), canon("fr/", page)
        tags = (f'<link rel="canonical" href="{canon(dirprefix, page)}">\n'
                f'    <link rel="alternate" hreflang="en" href="{en}">\n'
                f'    <link rel="alternate" hreflang="fr" href="{fr}">\n'
                f'    <link rel="alternate" hreflang="x-default" href="{en}">\n')
        s = s.replace("<title>", tags + "    <title>", 1)
        done.append("canonical+hreflang")

    # home: brand line is not the page title
    if page == "index.html":
        s2 = re.sub(r'<h1( class="text-4xl md:text-5xl font-bold text-white mb-4"[^>]*>)(ASSO S\.L\.A\.V\.É\.)</h1>', r'<p\1\2</p>', s, count=1)
        if s2 != s:
            done.append("second h1 -> p"); s = s2

    # contact: labels + dead link
    if page == "contact.html":
        n = 0
        def lab(m):
            nonlocal n
            n += 1
            label, ctrl = m.group(1), m.group(2)
            if 'for="' in label:
                return m.group(0)
            label = label.replace("<label ", f'<label for="contact-f{n}" ', 1)
            ctrl = re.sub(r"<(input|textarea)", rf'<\1 id="contact-f{n}" name="contact-f{n}"', ctrl, count=1)
            return label + ctrl
        s2 = re.sub(r'(<label[^>]*>.*?</label>)(\s*<(?:input|textarea)[^>]*>)', lab, s, flags=re.S)
        if s2 != s:
            done.append(f"{n} labels associated"); s = s2
        s2 = re.sub(r'<a href="#" (class="flex items-center gap-4 p-5 bg-white[^"]*")>(.*?)</a>', r'<div \1>\2</div>', s, count=1, flags=re.S)
        if s2 != s:
            done.append("href=# card -> div"); s = s2

    if s != orig:
        path.write_text(s, encoding="utf-8")
    return done


def main():
    for dirprefix in ("", "fr/"):
        for page in PAGES:
            p = ROOT / dirprefix / page
            if p.exists():
                d = fix_page(p, dirprefix)
                print(f"{dirprefix}{page}: {', '.join(d) if d else 'no change'}")
    # clone-fixes.css: the @import is replaced by fonts.css
    css = ROOT / "assets" / "clone-fixes.css"
    t = css.read_text(encoding="utf-8")
    t2 = re.sub(r"@import url\('https://fonts\.googleapis\.com[^)]*'\);\n", "/* fonts: see assets/fonts.css (self-hosted) */\n", t)
    if t2 != t:
        css.write_text(t2, encoding="utf-8"); print("clone-fixes.css: @import removed")
    # robots + sitemap
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {HOST}sitemap.xml\n", encoding="utf-8")
    urls = []
    for page in SITEMAP_PAGES:
        for dirprefix in ("", "fr/"):
            urls.append(f'  <url><loc>{canon(dirprefix, page)}</loc>'
                        f'<xhtml:link rel="alternate" hreflang="en" href="{canon("", page)}"/>'
                        f'<xhtml:link rel="alternate" hreflang="fr" href="{canon("fr/", page)}"/></url>')
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    print(f"robots.txt + sitemap.xml ({len(urls)} urls)")


if __name__ == "__main__":
    main()
