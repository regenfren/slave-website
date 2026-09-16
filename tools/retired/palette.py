#!/usr/bin/env python3
"""Hold the site to its five colours.

Palette (Tim, 2026-09-16): the two colours of the logo plus three neutrals.
    navy  #12395F  every dark: headings, body text, dark bands, footer, overlays
    rust  #C0521C  the only accent
    paper #F7F3EB  page
    sand  #EDE4D3  alternating sections, tints
    grey  #7A6E5F  secondary text
White, black and pure transparency stay allowed.

    python3 tools/palette.py          rewrite every legacy colour onto the palette
    python3 tools/palette.py --check  exit 1 and list any colour outside the palette

Values only. Tailwind class NAMES such as text-[#0055A4] are left alone on purpose: site.css is a
compiled static file, so a renamed class would have no rule behind it. The selector keeps its legacy
hex and its declaration now carries navy. Never hand-type a new arbitrary-colour class; there is no
build step to generate its CSS.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAVY, RUST, PAPER, SAND, GREY = '12395f', 'c0521c', 'f7f3eb', 'ede4d3', '7a6e5f'
MAP = {
    # blues and browns: one dark
    '0055a4': NAVY, '003d6b': NAVY, '002d4f': NAVY, '0e5a9c': NAVY, '0b2c46': NAVY, '001e33': NAVY,
    '1e3a8a': NAVY, '3a2e20': NAVY, '2a2017': NAVY, '1e160e': NAVY, '5c5044': NAVY,
    '374151': NAVY, '1f2937': NAVY, '111827': NAVY,
    # reds, purples, terracottas: one accent
    'ef4444': RUST, 'dc2626': RUST, 'f87171': RUST, 'b91c1c': RUST, '8b5cf6': RUST, '6d28d9': RUST,
    '7c3aed': RUST, 'c4b5fd': RUST, 'a78bfa': RUST, 'd85d28': RUST, 'c0693f': RUST, 'b45309': RUST,
    'ea580c': RUST,
    '4a341e': NAVY, '3b2f21': NAVY, 'a8552f': RUST, 'f9f6f0': PAPER, 'eae2d1': SAND, 'd9c7b5': SAND,
    # greys
    '8c7f6c': GREY, '6b7280': GREY, '4b5563': GREY, '9ca3af': GREY,
    # lights
    'f8f7f4': PAPER, 'faf6ef': PAPER, 'fdfbf7': PAPER, 'f9fafb': PAPER,
    'f3ecdd': SAND, 'eae0cf': SAND, 'eff6ff': SAND, 'f3f4f6': SAND, 'e5e7eb': SAND,
}
ALLOWED = {NAVY, RUST, PAPER, SAND, GREY, 'ffffff', '000000', 'fff', '000'}
FILES = [p for p in ROOT.rglob('*') if p.suffix in ('.css', '.html', '.js')
         and not any(part in ('tools', 'media', '.git', 'archive') for part in p.relative_to(ROOT).parts)]

rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
RGBMAP = {rgb(k): rgb(v) for k, v in MAP.items()}
HEX = re.compile(r'#(' + '|'.join(MAP) + r')(?![0-9a-fA-F])', re.I)
RGB_COMMA = re.compile(r'(rgba?\(\s*)(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(\s*[,)/])', re.I)
RGB_SPACE = re.compile(r'(rgb\(\s*)(\d+)\s+(\d+)\s+(\d+)(\s*[/)])')

def values(s):
    s = HEX.sub(lambda m: '#' + MAP[m.group(1).lower()], s)
    def sub(sep):
        def f(m):
            k = tuple(int(m.group(i)) for i in (2, 3, 4))
            if k not in RGBMAP: return m.group(0)
            return m.group(1) + sep.join(map(str, RGBMAP[k])) + m.group(5)
        return f
    return RGB_SPACE.sub(sub(' '), RGB_COMMA.sub(sub(', '), s))

declarations = lambda css: re.sub(r'\{[^{}]*\}', lambda m: values(m.group(0)), css)

def html(h):
    h = re.sub(r'(<style[^>]*>)(.*?)(</style>)', lambda m: m.group(1) + declarations(m.group(2)) + m.group(3), h, flags=re.S)
    return re.sub(r'style="([^"]*)"', lambda m: 'style="' + values(m.group(1)) + '"', h)

# shadcn-style HSL tokens (space-separated "H S% L%") read by hsl(var(--x)). clone-fixes.css is the
# stylesheet that sets them last, so it is the one that paints.
HSL = {'navy': '210 68% 22%', 'rust': '20 75% 43%', 'paper': '40 43% 95%', 'sand': '39 42% 88%', 'grey': '33 12% 43%'}
TOKENS = {
    'background': 'paper', 'foreground': 'navy', 'card-foreground': 'navy', 'popover-foreground': 'navy',
    'primary': 'navy', 'primary-light': 'navy', 'primary-medium': 'navy', 'secondary': 'navy',
    'secondary-light': 'navy', 'card-shadow': 'navy',
    'accent': 'rust', 'accent-light': 'rust', 'ring': 'rust',
    'accent-soft': 'sand', 'border': 'sand', 'border-light': 'sand', 'card-border': 'sand',
    'primary-soft': 'sand', 'secondary-soft': 'sand', 'muted': 'sand',
    'muted-foreground': 'grey',
}
def tokens(css):
    return re.sub(r'--(' + '|'.join(sorted(TOKENS, key=len, reverse=True)) + r'):\s*[0-9.]+\s+[0-9.]+%\s+[0-9.]+%',
                  lambda m: f'--{m.group(1)}:{HSL[TOKENS[m.group(1)]]}', css)

REWRITE = {'.css': declarations, '.html': html, '.js': values}

def used(path):
    """Colours a browser would actually paint: declarations, <style>, style=, js. Not class names."""
    t = path.read_text(errors='ignore')
    if path.suffix == '.css': chunks = re.findall(r'\{[^{}]*\}', t)
    elif path.suffix == '.html':
        chunks = re.findall(r'<style[^>]*>(.*?)</style>', t, flags=re.S)
        chunks = [c for s in chunks for c in re.findall(r'\{[^{}]*\}', s)] + re.findall(r'style="([^"]*)"', t)
    else: chunks = [t]
    out = set()
    for c in chunks:
        out |= {h.lower() for h in re.findall(r'#([0-9a-fA-F]{6})(?![0-9a-fA-F])', c)}
        out |= {'%02x%02x%02x' % tuple(map(int, g)) for g in re.findall(r'rgba?\(\s*(\d+)\s*[, ]\s*(\d+)\s*[, ]\s*(\d+)', c)}
    return out

if '--check' in sys.argv:
    bad = {}
    for p in FILES:
        for c in used(p) - ALLOWED:
            bad.setdefault(c, []).append(str(p.relative_to(ROOT)))
    for c, where in sorted(bad.items()):
        print(f'#{c}  {len(where)} file(s): {", ".join(sorted(set(where))[:4])}')
    print(f'{len(bad)} colour(s) outside the palette')
    sys.exit(1 if bad else 0)

n = 0
for p in FILES:
    t = p.read_text(errors='ignore'); u = REWRITE[p.suffix](t)
    if p.name == 'clone-fixes.css': u = tokens(u)
    if u != t: p.write_text(u); n += 1
print(f'rewrote {n} file(s)')
