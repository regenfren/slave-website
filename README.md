# railsoftime.fr, the S.L.A.V.É. site

Static site on GitHub Pages (`regenfren/slave-website`, branch `main`), English at `/` and French
under `/fr/`. Rebuilt 2026-09-16 in the S.L.A.V.É. brand; the earlier template clone is in git history.

## How the pages are made

```
python3 tools/build.py          # writes all 12 pages
python3 tools/build.py --check  # fails if a page is out of date with content/ or the templates
```

- **Copy:** `content/en.json` and `content/fr.json`. Every word on every page lives there, same
  structure in both languages. Edit the copy there, then build. Never edit a generated `index.html`.
- **Templates:** `tools/build.py` (head, header, footer, one function per page). It also enforces the
  schools rule: every school with a published film needs name, city, logo file and a tagline in both
  languages in `assets/films.json`.
- **Brand:** `assets/brand/brand.css`. Jost for titles and interface, Literata for reading (both SIL
  Open Font License, self-hosted in `assets/brand/fonts/`). Colours: ink `#111A22`, night `#0B1117`,
  rust `#C0521C`, paper `#F2F1ED`, paper-2 `#E6E4DD`, steel `#5C6670`. 2px corners, no shadows.
  `node tools/palette-audit.mjs <url>` fails if a page paints any other colour.
- **Logo:** Kashin's drawing recoloured, book in ink or paper, rails in rust (`assets/brand/img/`).
- **Photos:** real association photos are served in a duotone print treatment from
  `assets/brand/photos/` (`map.json` maps each original to its print version). Hero photos stay in colour
  in `assets/brand/hero/`. No stock and no AI images.
- **Behaviour:** `assets/brand/site.js` (Projects dropdown, mobile menu, home reel, contact form note).

## The home reel

`assets/brand/reel/`: a 35-second silent loop of 19 shots from six student films (Light Weavers,
Stage Echo, WELL#, Aurelia, Apex, Elofit), 10% slower than the first cut so the caption can be read.
24 fps H.264, lightly denoised: `reel-1280.mp4` 2.2 MB, `reel-720.mp4` 0.9 MB for phones.

Loading: the poster frame (26 KB, 14 KB on phones) is the first paint. The video is fetched only after
the page's load event, never with reduced motion or Save-Data, and it pauses when scrolled away.
The caption's cut points are `REEL` in `tools/build.py`; change them if the video changes.
Shots with an AI watermark, stock footage, a TV channel logo, title cards or name tags were left out.
**Before merging to `main`:** the six film teams' yes, asked by Daria.

## Student films (`/films/`, the home stage)

Unchanged from 2026-09-07 / 2026-09-15 except for styling. `assets/films.json` is the whole database;
`films.js` renders the films page, `showcase.js` the home stage, `schools.js` the school picker.
Nothing from YouTube loads before a click (`youtube-nocookie.com`). A film shows only with a `youtube`
id; `?preview=1` shows all. Adding a film: `AJOUTER-UN-FILM.md` (for Daria). The nightly
`tools/upload-and-publish.sh` job only edits `films.json`, so it never touches the built pages.

## Run it locally

```
python3 -m http.server 8811   # then open http://localhost:8811/
```

Python's server does not answer byte-range requests, so seeking inside the reel does not work
locally. It works on GitHub Pages.

## Known gaps

- The contact form has no mail backend; submitting shows a note with the email address.
- *Limitless* (CNAM) has no playable original yet; *Nova Night* is still the 8-second teaser; BDX
  Consulting exists only as a 360p student upload.
- Old template assets (`assets/site.css`, `clone-fixes.css`, `clone.js`, `fonts.css`, the stock hero
  images) are no longer referenced by any page and can be deleted after the merge.
