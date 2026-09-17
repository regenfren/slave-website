# Changelog

Newest first. One entry per shipped change; the commit says how, this says what and why.

## 2026-09-16 (evening, branch `rebrand`, not live)

- **The site in the S.L.A.V.É. brand.** Every page rebuilt in the system of the film-led redesign
  proposal Tim chose: Jost and Literata, ink / rust / paper, the logo recoloured with rust rails, 2px
  corners, no shadows, no icon tiles, real photos in a duotone print treatment, no stock images. Same
  pages, same sections in the same order, same words in both languages, captured into
  `content/{en,fr}.json`; `tools/build.py` writes the pages from them and replaces `tools/nav.py` and
  `tools/films-pages.py` (moved to `tools/retired/`).
- **Home header is the student-film reel**, 35 s, slowed 10%, with a caption naming the film on screen.
  2.2 MB on desktop and 0.9 MB on phones (was 7.1 MB / 2.7 MB), loaded after the page, never with
  reduced motion or Save-Data, paused when off screen.
- **Reel rebuilt at high quality** (Tim: "way too low quality"). Cut again from the original films into
  a lossless master and encoded once: 1920x816 for wide screens and a 642x856 portrait crop for phones,
  in AV1, HEVC and H.264, picked per browser. The first version had passed through three lossy encodes
  and a 1280-wide, heavily denoised final.
- **Team and advisor photos reframed** (Tim: "i don't like how team photos appear"). Every portrait is
  recropped from its detected face box, so the heads are the same size on the same eye line whatever the
  photographer framed, and each sits in a mounted-print frame (paper mat, one hairline) that quiets the
  mismatched backgrounds. Columns widened so roles stop wrapping into ribbons. Considered and dropped:
  arch tops (reads like a wedding) and a heavy ink mount (too loud on the pages that are already dark).
- **Two bugs Tim caught.** The film popup scrolled as one sheet and showed a scrollbar over the film;
  it still scrolls, without the bar. The Projects menu closed the moment it was clicked, because
  hovering had already opened it and the click toggled it shut: a click now pins it open, a second
  click or Escape or a click outside closes it.
- Swept every interactive element on desktop and phone afterwards (menus, language switch, film popup
  and its prev/next, school picker, home stage queue/search/play, hero pause, contact form, History &
  Values, skip link, 404 back): 27 checks, all passing, no console errors.
- **One photo style, faces centred.** Every real photo now carries a face focal point (Apple Vision,
  `tools/faces/facepoint.swift`), which becomes its `object-position`, so no crop on any screen cuts a
  face. People are shown in one upright 4:5 portrait format. 36 of 42 photos have faces.
- **Rails of Time card** on the Asso page uses a full-resolution frame from Light Weavers (hard hats over
  a hand-drawn route map) instead of the low-resolution cinema photo (Tim).
- **Photos in a warm colour grade** instead of the grey duotone (Tim): each phone's colour cast removed,
  then warm highlights, soft blacks and fine grain. `tools/photo-grade.py`.
- **About the Project moved above the films** on the home page (Tim).
- **Partner sections are logos only**, on the home and Asso pages (Tim). The home page had been
  shipping the partner names as text since the template was built.
- **About the Project lost its icon illustration.** Every decorative icon on the site is gone.
- Checked: 0 console errors, every internal link and asset answers 200 (105 URLs), no horizontal
  scroll at 390 px, paint audit clean against the brand palette, reel caption follows the cuts.

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
