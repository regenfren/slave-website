#!/usr/bin/env python3
"""The site's navigation, applied to every page. Run from the repo root: python3 tools/nav.py

Single source of truth for the header nav, the Projects dropdown and the footer quick links
(the mobile menu is built from the header at runtime by assets/clone.js). Idempotent: re-run it
after adding a page or renaming an entry, instead of editing twelve headers by hand.

Shape (Tim, 2026-09-15): two entries, Asso and Projects; Projects is a dropdown holding
Rails of Time (the home), Right to Dignity and Films. The Contact button stays on the right.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LINK_IDLE = 'class="text-sm font-medium transition-all hover:text-[#0055A4] relative text-[#003D6B] after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-[#EF4444] after:transition-all after:duration-300 hover:after:w-full"'
LINK_ACTIVE = 'class="text-sm font-medium transition-all hover:text-[#0055A4] relative text-[#0055A4] after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-[#EF4444] after:transition-all after:duration-300 hover:after:w-full after:w-full"'
BTN_IDLE = 'class="text-sm font-medium transition-all hover:text-[#0055A4] relative flex items-center gap-1 text-[#003D6B] after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-[#EF4444] after:transition-all after:duration-300 hover:after:w-full"'
BTN_ACTIVE = 'class="text-sm font-medium transition-all hover:text-[#0055A4] relative flex items-center gap-1 text-[#0055A4] after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-[#EF4444] after:transition-all after:duration-300 hover:after:w-full after:w-full"'
ITEM_IDLE = 'class="block px-5 py-3 text-sm font-medium transition-colors text-[#003D6B] hover:bg-[rgba(0,85,164,0.05)] hover:text-[#0055A4]"'
ITEM_ACTIVE = 'class="block px-5 py-3 text-sm font-medium transition-colors bg-[rgba(0,85,164,0.08)] text-[#0055A4]"'
CHEVRON = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-down w-3.5 h-3.5 transition-transform duration-200"><path d="m6 9 6 6 6-6"></path></svg>'

NAV = {
    "en": {"pre": "", "asso": "Asso", "projects": "Projects", "contact": "Contact",
           "items": [("", "Rails of Time"), ("dignity/", "Right to Dignity"), ("films/", "Films")]},
    "fr": {"pre": "/fr", "asso": "Asso", "projects": "Projets", "contact": "Contact",
           "items": [("", "Les Rails du Temps"), ("dignity/", "Droit à la Dignité"), ("films/", "Films")]},
}

# page key -> (dir, file)
PAGES = {"": "index.html", "asso/": "asso/index.html", "films/": "films/index.html",
         "dignity/": "dignity/index.html", "contact/": "contact/index.html", "404": "404.html"}


def nav_html(lang: str, page: str) -> str:
    N = NAV[lang]
    pre = N["pre"]
    in_projects = any(page == p for p, _ in N["items"])
    items = "".join(f'<a {ITEM_ACTIVE if page == p else ITEM_IDLE} href="{pre}/{p}">{label}</a>' for p, label in N["items"])
    return (
        '<nav class="hidden md:flex items-center space-x-8">'
        f'<a {LINK_ACTIVE if page == "asso/" else LINK_IDLE} href="{pre}/asso/">{N["asso"]}</a>'
        f'<div class="relative"><button type="button" aria-haspopup="true" aria-expanded="false" {BTN_ACTIVE if in_projects else BTN_IDLE}>{N["projects"]}{CHEVRON}</button>'
        '<div class="absolute top-full left-1/2 -translate-x-1/2 pt-3 w-56 transition-all duration-200 origin-top opacity-0 scale-95 pointer-events-none">'
        f'<div class="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">{items}</div></div></div>'
        '</nav>'
    )


def footer_links(lang: str):
    N = NAV[lang]
    return [("asso/", N["asso"])] + list(N["items"]) + [("contact/", N["contact"])]


def apply(html: str, lang: str, page: str) -> str:
    html, n = re.subn(r"<nav .*?</nav>", nav_html(lang, page), html, count=1, flags=re.S)
    assert n == 1, "nav not found"
    m = re.search(r'(<h4[^>]*>[^<]*<span[^>]*></span></h4>)<ul class="space-y-4">(<li>.*?</li>)</ul>', html, re.S)
    assert m, "footer quick links not found"
    li = re.search(r"<li>.*?</li>", m.group(2), re.S).group(0)
    pre = NAV[lang]["pre"]
    lis = "".join(re.sub(r'href="[^"]*"', f'href="{pre}/{p}"', re.sub(r"</span>[^<]*</a>", f"</span>{label}</a>", li, count=1), count=1)
                  for p, label in footer_links(lang))
    return html[:m.start(2)] + lis + html[m.end(2):]


def main():
    for lang, d in (("en", ""), ("fr", "fr/")):
        for page, file in PAGES.items():
            p = ROOT / d / file
            if not p.exists():
                continue
            s = p.read_text(encoding="utf-8")
            s2 = apply(s, lang, page)
            if s2 != s:
                p.write_text(s2, encoding="utf-8")
                print("nav:", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
