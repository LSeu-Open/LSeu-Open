#!/usr/bin/env python3
"""Generate all README badges as local SVGs in the m3 "material" pill style.

No runtime/external dependencies in the README: every badge is a self-hosted
SVG committed to the repo. Edit the BADGES table below to control colors,
labels, or which icon is used, then run:  python badges/generate.py

For each badge a light "container" background + dark "on-container" foreground
are auto-derived from the brand color, so the whole set stays visually
consistent. Logo paths are official simple-icons glyphs (fetched once at build
time and baked into the output — not referenced at runtime). Text width is
forced with textLength so labels never clip regardless of the viewer's fonts.
"""
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CDN = "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{}.svg"

# Unified "Cool Professional" palette: the color encodes the CATEGORY, the
# logo identifies the specific tool. Each entry is (background, foreground).
# Edit one pair to recolor an entire category at once, then re-run.
PALETTE = {
    "links": ("#DCE3EF", "#243B66"),  # navy
    "lang":  ("#DBDFF0", "#2D3A7A"),  # indigo
    "ml":    ("#D6E4F2", "#1E5AA0"),  # blue
    "web":   ("#D6EAF2", "#1A6E94"),  # sky
    "test":  ("#D6EEE8", "#157065"),  # teal
    "tools": ("#DEE1EA", "#3F4A66"),  # slate
}

# name -> (label, [icon-slug candidates], category)
BADGES = [
    # --- Header / links ---
    ("orcid",            "ORCID",            ["orcid"],            "links"),
    ("semanticscholar",  "Semantic Scholar", ["semanticscholar"], "links"),
    ("github",           "GitHub",           ["github"],          "links"),
    # --- Languages ---
    ("python",           "Python",           ["python"],          "lang"),
    ("r",                "R",                ["r"],               "lang"),
    ("rust",             "Rust",             ["rust"],            "lang"),
    ("typescript",       "TypeScript",       ["typescript"],      "lang"),
    ("javascript",       "JavaScript",       ["javascript"],      "lang"),
    ("shell",            "Shell",            ["gnubash"],         "lang"),
    # --- Data Science & ML ---
    ("pytorch",          "PyTorch",          ["pytorch"],         "ml"),
    ("tensorflow",       "TensorFlow",       ["tensorflow"],      "ml"),
    # --- Web & App ---
    ("svelte",           "Svelte",           ["svelte"],          "web"),
    ("astro",            "Astro",            ["astro"],           "web"),
    ("vite",             "Vite",             ["vite", "vitejs"],  "web"),
    ("nodejs",           "Node.js",          ["nodedotjs"],       "web"),
    ("html",             "HTML5",            ["html5"],           "web"),
    ("css",              "CSS",              ["css", "css3"],     "web"),
    ("nginx",            "NGINX",            ["nginx"],           "web"),
    # --- Testing ---
    ("pytest",           "pytest",           ["pytest"],          "test"),
    ("vitest",           "Vitest",           ["vitest"],          "test"),
    ("playwright",       "Playwright",       ["playwright"],      "test"),
    ("stryker",          "Stryker",          ["stryker"],         "test"),
    # --- Data & Tools ---
    ("sqlite",           "SQLite",           ["sqlite"],          "tools"),
    ("mysql",            "MySQL",            ["mysql"],           "tools"),
    ("git",              "Git",              ["git"],             "tools"),
    ("docker",           "Docker",           ["docker"],          "tools"),
    ("podman",           "Podman",           ["podman"],          "tools"),
]

# Approx glyph advance (px) for a 15px bold sans; only used to size the pill
# nicely. textLength then forces the rendered text to exactly this width.
NARROW = set("ijltfrI.,;:!|'()[]{}")
WIDE = set("mwMW@")


def char_w(c):
    if c == " ":
        return 4.4
    if c in NARROW:
        return 5.2
    if c in WIDE:
        return 12.8
    if c.isupper() or c.isdigit():
        return 9.8
    return 8.5


def text_width(s):
    return sum(char_w(c) for c in s)


_logo_cache = {}


def fetch_logo(slugs):
    for slug in slugs:
        if slug in _logo_cache:
            return _logo_cache[slug]
        try:
            with urllib.request.urlopen(CDN.format(slug), timeout=20) as r:
                svg = r.read().decode("utf-8")
        except Exception as e:
            print(f"  ! {slug}: {e}")
            continue
        # take everything inside <svg>...</svg>, drop the <title>
        inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S).strip()
        _logo_cache[slug] = inner
        return inner
    return None


def build(name, label, slugs, category):
    bg, fg = PALETTE[category]
    logo = fetch_logo(slugs)

    tw = round(text_width(label))
    if logo:
        text_x = 38
        width = text_x + tw + 14
        logo_g = (f'<g transform="translate(13 6) scale(0.75)" fill="{fg}">'
                  f"{logo}</g>")
    else:
        text_x = 16
        width = text_x + tw + 14
        logo_g = ""

    svg = (
        f'<svg width="{width}" height="30" viewBox="0 0 {width} 30" '
        f'fill="none" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect width="{width}" height="30" rx="15" fill="{bg}"/>\n'
        f'  {logo_g}\n'
        f'  <text x="{text_x}" y="20" textLength="{tw}" '
        f'lengthAdjust="spacingAndGlyphs" '
        f'font-family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif" '
        f'font-size="15" font-weight="700" fill="{fg}">{label}</text>\n'
        f'</svg>\n'
    )
    with open(os.path.join(HERE, f"{name}.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ok  {name}.svg  ({width}px, {'logo' if logo else 'no logo'})")


if __name__ == "__main__":
    print("Generating badges...")
    for entry in BADGES:
        build(*entry)
    print("Done.")
