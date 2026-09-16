# Changelog

Newest first. One entry per shipped change; the commit says how, this says what and why.

## 2026-09-16

- **Five colours.** The site painted 72 distinct colours: the original French blue and red, the
  brown and terracotta laid over them, plus purple on "Dignity", cool Tailwind greys, three browns
  and four creams. It now paints five, all from the logo or next to it: navy `#12395F` for every dark
  (headings, body text, dark bands, footer, hero overlays), rust `#C0521C` as the only accent, paper
  `#F7F3EB`, sand `#EDE4D3`, warm grey `#7A6E5F`. White and black stay. Values only: no layout, copy or
  class name changed (verified per file). `tools/palette.py` does the rewrite and is safe to re-run;
  `tools/palette-audit.mjs <url>` reads what the browser actually paints on all eleven pages and
  fails on anything outside the five (it reported 22 strays against the site before this change).
  Tailwind class names still read `text-[#0055A4]` and the like, because `site.css` is compiled and
  a renamed class would have no rule; their declarations now carry navy. Never type a new
  arbitrary-colour class: there is no build step to make its CSS.

## 2026-09-15

- **Rails of Time is the home page.** `/` is the old Rails of Time page, with a "Student films"
  stage under the hero: one big player, a queue filtered by school and searchable by title, team,
  school or course, prev/next, and a "See all films" link to `/films/`. Same manifest
  (`assets/films.json`), same no-YouTube-before-play rule as the films page.
- **Asso page.** The old home and the old association page are one page at `/asso/`: the About
  block now holds the association's two intro paragraphs, the team photo and a collapsible
  "History & Values" (native `<details>`); pillars, featured projects, team, partners and
  the community block stay. The association page's motto band was dropped (its quote is already
  the hero line). Nav is flat: Rails of Time, Films, Asso, Right to Dignity, Contact.
- **Nav, second pass the same day:** two entries, Asso and Projects; Projects is a dropdown with
  Rails of Time, Right to Dignity and Films; Contact stays a button. `tools/nav.py` is the one
  writer of every header and footer nav from now on.
- **School picker** on the home stage and the films page: one block, the selected school's
  details on the left (logo, full name, city, film count, one-line tagline from `films.json`,
  `schools`) and a compact name-only list on the right that drives it. On the home it is the top
  band of the stage box, not a separate element (Tim's second-pass correction, same day). Rule: every school with a published film carries logo + tagline in both
  languages; `tools/films-pages.py` refuses to build without them. CAFA's logo is the 194x70 png
  from cafa.edu.cn, the only one that is not retina-sharp.
- **Eyebrow pills gone.** The 36 small rounded labels above headings ("Our Projects", "What We Do",
  "Since 2007 • Bordeaux" and so on, every page, both languages) are removed; the heading names the
  section. Kept: "Phase 1 / Phase 2" (a real sequence) and the "Students involved" sub-headings.
- **Hero polish:** the fade under every hero photo ended on `#F8F7F4`, one shade off the cream,
  which read as a pale band; it lands on the page colour now. The pulse glow on hero buttons is
  gone, shadows are quieter, the home CTA has room above it.
- **Clean URLs.** One folder per page (`/films/`, `/asso/`, `/dignity/`, `/contact/`, and under
  `/fr/`), absolute asset paths, canonical + hreflang + sitemap on the new addresses. Every old
  `*.html` address is a redirect stub that keeps the hash, so `films.html#film=apex` still opens
  Apex. `/index.html` is rewritten to `/` in the address bar.

## 2026-09-07

- **Site audit fixes.** Fonts self-hosted (`assets/fonts.css`, latin + latin-ext of Fraunces,
  Hanken Grotesk and Poppins 700): no request leaves railsoftime.fr for type any more, and one
  DNS + TLS round trip less before text renders. Photos over 120 KB converted to WebP at display
  size, the header emblem and footer logo resized from 768 to 1024 px down to 224 and 192 px, film
  posters to 800 px WebP, a 64 px favicon instead of the 299 KB og:image. Home page had two h1;
  the brand line above the title is a paragraph now. Contact form labels tied to their fields;
  the dead `href="#"` card is a plain box. Canonical + hreflang on every page, `robots.txt`,
  `sitemap.xml`. Films page reserves its height before the manifest loads (CLS 0.51 -> 0).
- **Student films page** (`films.html`, `fr/films.html`): one block per school and term, driven by
  `assets/films.json`; YouTube unlisted embeds loaded on click via youtube-nocookie. 22 entries
  (7 KEDGE 2025, 5 CNAM 2026, 10 CAFA 2026), posters, bilingual synopses for the CAFA films.
  `AJOUTER-UN-FILM.md` is the add-a-film path.
- **railsoftime.fr** is the site's domain (custom domain on GitHub Pages, HTTPS enforced);
  og:url/og:image point at it.
- Mobile: the header's dead globe button pushed the burger off-screen and gave every page a
  sideways scroll; hidden.

## 2026-08-07

- Partner marquee with official logos; Right to Dignity restructure per Daria; mobile fixes.
