# Changelog

Newest first. One entry per shipped change; the commit says how, this says what and why.

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
