# Retired 2026-09-16

Replaced by `tools/build.py`, which writes every page (header, footer, navigation and the films page
included) from `content/{en,fr}.json` in the S.L.A.V.É. brand. Do not run these: they edit the old
template markup and would break the rebuilt pages.

- `nav.py` - header and footer links for the old template. Now `header()` / `footer()` in build.py.
- `films-pages.py` - built the films page from the old home page's head and header. Its schools rule
  (logo + tagline in both languages for every school with a published film) lives on in build.py.
- `palette.py` - rewrote the pre-brand colours onto the five-colour palette of the morning of
  2026-09-16. The brand palette is in `assets/brand/brand.css`; `tools/palette-audit.mjs` checks it.
