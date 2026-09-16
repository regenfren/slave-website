// Which colours does the browser actually PAINT on every page? Static paint only (no hover states).
// usage: node tools/palette-audit.mjs <base-url>     e.g. http://localhost:8767/  or  https://railsoftime.fr/
// Exit 1 when anything outside the brand palette in assets/brand/brand.css is painted.
// A colour within 3 per channel of a palette value counts as that value: hsl() tokens round by one.
// Proven able to fail 2026-09-16: against the pre-palette live site it reports every stray colour.
// Needs puppeteer-core and a working Chrome; borrows the verified launcher from the x-post-cards skill.
import { createRequire } from 'node:module'
const puppeteer = createRequire('/Users/govenok-laptop/.agents/skills/x-post-cards/scripts/lib/chrome.mjs')('puppeteer-core')
import { findWorkingChrome } from '/Users/govenok-laptop/.agents/skills/x-post-cards/scripts/lib/chrome.mjs'
const base = process.argv[2]
const pages = ['', 'asso/', 'films/', 'dignity/', 'contact/', 'fr/', 'fr/asso/', 'fr/films/', 'fr/dignity/', 'fr/contact/', '404.html']
const browser = await puppeteer.launch({ executablePath: findWorkingChrome({ verbose: false }), headless: true, args: ['--no-sandbox'] })
const page = await browser.newPage()
await page.setViewport({ width: 1280, height: 800 })
const all = {}
for (const p of pages) {
  await page.goto(base + p, { waitUntil: 'networkidle2', timeout: 60000 })
  // open the Projects dropdown and hover states are not captured; static paint only
  const found = await page.evaluate(() => {
    const props = ['color', 'backgroundColor', 'borderTopColor', 'borderBottomColor', 'borderLeftColor', 'borderRightColor', 'backgroundImage', 'boxShadow', 'fill', 'stroke', 'outlineColor', 'textDecorationColor', 'caretColor']
    const out = {}
    const els = [...document.querySelectorAll('*')]
    for (const el of els) {
      for (const pseudo of [null, '::before', '::after']) {
        const cs = getComputedStyle(el, pseudo)
        if (pseudo && (cs.content === 'none' || cs.content === 'normal')) continue
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        for (const k of props) {
          const v = cs[k]; if (!v) continue
          for (const m of v.matchAll(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/g)) {
            const a = m[4] === undefined ? 1 : +m[4]
            if (a === 0) continue
            if ((k.startsWith('border') || k === 'outlineColor' || k === 'textDecorationColor' || k === 'caretColor') ) {
              const w = k.startsWith('border') ? parseFloat(cs[k.replace('Color', 'Width')]) : 1
              if (!w || (k.startsWith('border') && cs[k.replace('Color', 'Style')] === 'none')) continue
              if (k === 'outlineColor' && cs.outlineStyle === 'none') continue
              if (k === 'textDecorationColor' && !cs.textDecorationLine.includes('line')) continue
              if (k === 'caretColor') continue
            }
            if ((k === 'fill' || k === 'stroke') && !(el instanceof SVGElement)) continue
            const hex = [m[1], m[2], m[3]].map(n => (+n).toString(16).padStart(2, '0')).join('')
            const tag = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(/\s+/).slice(0, 3).join('.') : '') + (pseudo || '')
            ;(out[hex] ??= { n: 0, where: new Set() }).n++
            if (out[hex].where.size < 2) out[hex].where.add(k + ' ' + tag.slice(0, 90))
          }
        }
      }
    }
    return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, { n: v.n, where: [...v.where] }]))
  })
  for (const [hex, v] of Object.entries(found)) {
    (all[hex] ??= { n: 0, pages: new Set(), where: v.where }).n += v.n
    all[hex].pages.add(p || '/')
  }
}
await browser.close()
// Brand palette (2026-09-16): ink, night, rust, rust hover, paper, paper-2, steel, plus white and black.
const PALETTE = ['111a22', '0b1117', 'c0521c', 'a2441a', 'f2f1ed', 'e6e4dd', '5c6670', 'ffffff', '000000']
const ch = h => [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16))
const near = h => PALETTE.some(p => ch(p).every((v, i) => Math.abs(v - ch(h)[i]) <= 3))
const rows = Object.entries(all).sort((a, b) => b[1].n - a[1].n)
for (const [hex, v] of rows) console.log(`${near(hex) ? 'ok ' : 'OFF'} #${hex} ${String(v.n).padStart(5)}  ${[...v.pages].slice(0, 4).join(' ')}  | ${v.where.join(' ; ')}`)
const off = rows.filter(([h]) => !near(h)).length
console.log(off, 'painted colours outside the palette')
process.exit(off ? 1 : 0)
