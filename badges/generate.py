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

# name -> (label, [icon-slug candidates], brand_hex)
BADGES = [
    # --- Header / links ---
    ("orcid",            "ORCID",            ["orcid"],            "#A6CE39"),
    ("semanticscholar",  "Semantic Scholar", ["semanticscholar"], "#1857B6"),
    ("github",           "GitHub",           ["github"],          "#181717"),
    # --- Languages ---
    ("python",           "Python",           ["python"],          "#3776AB"),
    ("r",                "R",                ["r"],               "#276DC3"),
    ("rust",             "Rust",             ["rust"],            "#000000"),
    ("typescript",       "TypeScript",       ["typescript"],      "#3178C6"),
    ("javascript",       "JavaScript",       ["javascript"],      "#C9A800"),
    ("shell",            "Shell",            ["gnubash"],         "#4EAA25"),
    # --- Data Science & ML ---
    ("pytorch",          "PyTorch",          ["pytorch"],         "#EE4C2C"),
    ("tensorflow",       "TensorFlow",       ["tensorflow"],      "#FF6F00"),
    # --- Web & App ---
    ("svelte",           "Svelte",           ["svelte"],          "#FF3E00"),
    ("astro",            "Astro",            ["astro"],           "#BC52EE"),
    ("vite",             "Vite",             ["vite", "vitejs"],  "#646CFF"),
    ("nodejs",           "Node.js",          ["nodedotjs"],       "#5FA04E"),
    ("html",             "HTML5",            ["html5"],           "#E34F26"),
    ("css",              "CSS",              ["css", "css3"],     "#1572B6"),
    ("nginx",            "NGINX",            ["nginx"],           "#009639"),
    # --- Data & Tools ---
    ("sqlite",           "SQLite",           ["sqlite"],          "#0A5C8A"),
    ("mysql",            "MySQL",            ["mysql"],           "#4479A1"),
    ("git",              "Git",              ["git"],             "#F05032"),
    ("docker",           "Docker",           ["docker"],          "#2496ED"),
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


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def blend(hex_color, target, t):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex((r + (target - r) * t,
                       g + (target - g) * t,
                       b + (target - b) * t))


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


def build(name, label, slugs, brand):
    bg = blend(brand, 255, 0.80)   # pale brand container
    fg = blend(brand, 0, 0.50)     # dark on-container text/logo
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
