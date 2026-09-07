# SLAVÉ website — faithful clone + near-term edits

Static clone of the live site (`https://asso-slave.netlify.app/`, a Vite+React SPA) with the
2026-05-28 Daria walkthrough edits applied. See `../00_intake/website-walkthrough-daria-2026-05-28.md`
and `../decisions.md`.

## What this is
- **Bilingual** — English at the root, French under `fr/`. Each page exists in both: `index.html` (home),
  `association.html`, `projects.html` (Rails of Time), `dignity.html` (Right to Dignity), `contact.html`,
  `404.html`. The header **EN / FR** buttons switch between a page and its counterpart.
- **`assets/`** — `site.css` (the live site's original compiled Tailwind CSS, reused verbatim for
  pixel-fidelity), `clone-fixes.css` (forces JS-revealed content visible + marquee/featured-card styles),
  `clone.js` (language switcher, Projects-dropdown, mobile-menu toggle, form guard), `logo.png`,
  `slave-logo.png`, and all original images.
- React/JS was intentionally removed so the markup is the source of truth and edits stick. The exact
  rendered DOM + original CSS make it visually faithful to the live site.

## Editing note (bilingual)
EN pages live at the root, FR pages in `fr/` (paths use `../assets/...`). When you change EN content,
re-generate the FR pages so they stay in sync. Regeneration helpers live in `/tmp/clone/`:
`make-fr-all.mjs` (regenerates all 6 FR pages) + the translation maps `fr-map.json` (page content)
and `fr-map-extra.json` (homepage + new sections). Add any new English string to a map, then re-run.

## Design
Warm, human look in the logo palette: **Fraunces** (display serif) + **Hanken Grotesk** (body),
warm cream backgrounds, navy `#0B2C46` + red-orange `#E04A2B` accents, soft rounded cards. The Dignity
page's original purple was remapped to the logo palette for brand cohesion. All in `assets/clone-fixes.css`.
Nav has no redundant links (single Contact CTA; the two projects live only under the Projects dropdown).

## Homepage redesign (2025-06 round)
- **About** — removed the Savoir/Langue/Art/Voyage acronym-cards graphic; team-photo slot in its place.
- **Featured Projects** — two equal cards (Rails of Time + Right to Dignity): image, name, description, button.
- **Team & Advisors** — section with Team (Daria, Tim, Alexandre Kashin, Natallia Kosak, Marina Murano) +
  Advisors (Moosmayer, Ertle, Sayadi, Feigelson, Schaaper, Dupuy). *Placeholder photos, confirm w/ Daria.*
- **Partner Institutions** — auto-rolling clickable logo marquee (links to each org); no subtitle, no "View All".
- **Join Our Community** — new copy + single Contact button.
- **Nav "Projects"** — dropdown listing the two projects, each linking to its page (click + hover).

## Run it
```
cd 04_build
python3 -m http.server 8099   # then open http://localhost:8099/index.html
```

## Student films (`films.html`, `fr/films.html`) - added 2026-09-07

**Hosting decision:** the films live on YouTube as *unlisted* videos on the association's own
channel (`asso.slave@gmail.com`), never in this repo. Reasons, in order: GitHub Pages cannot serve
them (the 12 originals are 2 GB and 2.2 GB per cohort, the repo limit is 1 GB and a single file is
capped at 100 MB); YouTube transcodes to adaptive quality for free, so a 970 MB 1080p original plays
on a phone in Dax without buffering; unlisted keeps them off YouTube search but embeddable; and it is
the one option Daria can operate alone without an account Tim owns. Self-hosting on a CDN (Bunny,
Cloudflare Stream) was considered and rejected: a paid account and a transcoding step that would land
back on Tim at every handover.

**How the page works.** One JSON file, `assets/films.json`, is the whole database: one entry per film
with school, term, course, team, YouTube id, optional poster and synopsis. `assets/films.js` fetches
it and renders one block per school + term, each a horizontally scrolling row of posters. Nothing
from YouTube loads until a poster is clicked; then a `youtube-nocookie.com` iframe is injected into a
`<dialog>` (no cookies and no third-party request before the click, which is what makes the page
fast and keeps the RGPD footprint at zero until the visitor acts). Left/right arrows and keyboard
step through the films. Deep link: `films.html#film=<id>`.

**Rules the JS enforces.**
- A film is shown only when it has a `youtube` id. Add `?preview=1` to the URL to see every entry,
  including the ones still waiting for an upload (they carry a "Coming soon" tag).
- No `poster`? The YouTube thumbnail is used. The committed posters in `assets/films/` are frames
  pulled from the originals with ffmpeg (960 px wide, 30 to 160 KB each).
- On `localhost` a film with a `file` field plays the original from `media/<file>`. `media/` is a
  gitignored folder of symlinks to the Dropbox originals under `../00_intake/dropbox-dump/`, so the
  whole page can be reviewed before anything is uploaded.

**Adding a film:** `AJOUTER-UN-FILM.md` (French, written for Daria). Upload to YouTube, paste one
block into `films.json` on github.com, commit. Under five minutes.

**Regenerating the pages:** `python3 tools/films-pages.py`. It rebuilds `films.html` and
`fr/films.html` from the header, head and footer of `projects.html` / `fr/projects.html`, and
(idempotently) keeps the "Student films" link in the Projects dropdown and footer of every page plus
the mobile menu in `clone.js`. Edit the copy in the `LANGS` dict at the top of that script, not in
the generated HTML.

**Known gaps in the source material (2026-09-07):** the CNAM *Limitless* file in Daria's Dropbox is
truncated (no moov atom, will not play or upload; ask the team for the original); *Nova Night* is
still the 8-second teaser; the BDX Consulting film exists only as a 360p upload on a student's
YouTube channel (id `Nv8xsx0MZLw`), so it should be re-uploaded to the association channel once the
team sends the original. Both Dropbox folders download without a login by appending `&dl=1` to the
shared link (`VIDEO PREMAL FALL 2025.zip`, `VIDEO CNAM SPRING 2026.zip`).

## Edits applied (near-term — Daria 2026-05-28)
**Home:** removed hero trust-chips (Since 2007 / 6 Partner Universities / Creative Projects / Cultural
Dialogue); About grid reworked into **5 Core Pillars** (Savoir·Science, Langue, Art, Voyage, Échange)
— *draft wording, confirm w/ Daria*; added **team-photo placeholder**; added **Right to Dignity** as a
2nd featured project; **Partner Universities → Partners** (logo placeholders).
**Association:** removed the **timeline graphic** and the **"Our Key Areas"** section (narrative kept).
**Rails of Time:** removed **"5 Project Groups"**, the **"Featured Project: Les Rails du Temps"** badge,
and the **"Participant blog"** outcome; **Project Curators → Team & Advisors**; **Academic Partners →
Partners**; Project Objectives copy replaced with a placeholder.
**Right to Dignity:** role label pluralised → "Translation & cultural-project specialists".

## ⚠ Pending from Daria (placeholders / TODO comments in the HTML — search `TODO(Daria)`)
- HQ **team photo** (home About section)
- Final **5 Core Pillars** wording
- Full **Team & Advisors** list (names, roles, photos) — split Team (Daria, Tim, Alexandre Kashin, …)
  vs Advisors (Dirk Moosmayer, …); keep only project-relevant people on the Rails of Time page
- **Partner logos** (home + Rails of Time)
- New **Project Objectives** copy (pedagogical-innovation framing)
- Pilot-cohort **videos**

## Notes
- Keeps **SLAVÉ** branding + current hosting. The SÉLA rebrand / `sela.fr` / new logo is the long-term
  phase (see `../decisions.md`), not done here.
- Internal links use `*.html`. If redeployed to Netlify with clean URLs, add redirects accordingly.
- Regeneration helpers (DOM capture, transform, edits scripts) live in `/tmp/clone/` this session
  (`render.mjs`, `transform.mjs`, `edits.mjs`, `fix-assoc.mjs`) — not committed here.
