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
- **Photos:** one style for every real photo: a warm colour film grade, and each crop centred on the
  faces in the picture (`tools/faces/facepoint.swift` uses Apple's Vision framework, on this Mac only;
  the points land in `assets/brand/photos/focal.json` and become each image's `object-position`).
  People are shown in one upright 4:5 portrait format, recropped from the detected face box so every
  head is the same size on the same eye line, and mounted like a print (paper mat, one hairline) so a
  dozen different backgrounds stop fighting each other. `FACE_H` / `FACE_Y` in the grader set the crop. Served from
  `assets/brand/photos/` (`map.json` maps each original to its graded version), all written by
  `python3 tools/photo-grade.py` from the untouched originals. The Asso and Right to Dignity headers get
  the same grade. No stock and no AI images.
- **Behaviour:** `assets/brand/site.js` (Projects dropdown, mobile menu, home reel, contact form note).

## The home reel

A 35-second silent loop of 19 shots from six student films (Light Weavers, Stage Echo, WELL#, Aurelia,
Apex, Elofit), 10% slower than the first cut so the caption can be read. Shot list:
`tools/reel/shots.txt`. Build: `python3 tools/reel/build.py <path to media/>` (cuts every shot from the
original files into a lossless master, then encodes once per output; never re-encode an encoded reel).

Outputs in `assets/brand/reel/`: a 1920x816 cinema crop for landscape headers and a 642x856 portrait
crop for phones, each as AV1, HEVC and H.264. `site.js` picks the crop from the header's shape and the
first codec the browser decodes smoothly and power-efficiently. Settings were calibrated against the
lossless master (see `QUALITY` in the builder). Frame rate is 27.27 fps: the 30 fps master slowed 10%
with no duplicated frames. The caption's cut points are written to `tools/reel/cuts.json`.

Loading: the poster frame is the first paint. The video is fetched only after the page's load event,
never with reduced motion or Save-Data, and it pauses when scrolled away. MP4s are fast-start, so
playback begins before the file has finished downloading.
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
  images) and the first low-quality reel files (`assets/brand/reel/reel-1280.mp4`, `reel-720.mp4`,
  `poster-1280.*`, `poster-720.webp`) are no longer referenced by any page and can be deleted.
