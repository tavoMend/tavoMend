"""Genera los SVG animados del profile README (estética terminal / ASCII).

Uso:  py scripts/generate.py "ruta/a/foto.png"
Salida: assets/header.svg, assets/divider.svg, assets/footer.svg, assets/sections/*.svg
"""
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

FONT = "'Fira Code','JetBrains Mono','Cascadia Code',Consolas,'Courier New',monospace"
BG = "#020a09"
DIM = "#0d4d45"
MID = "#00c896"
GREEN = "#00ff9c"
CYAN = "#00e5ff"
ICE = "#b8fcff"

RAMP = " .:-=+*#%@"
COLS, ROWS = 72, 48
CW, CH = 6, 9.2  # celda del retrato en px


def portrait_grid(src):
    im = Image.open(src).convert("RGB")
    _, g, b = im.split()
    lum = Image.merge("RGB", (g, g, b)).convert("L")
    small = ImageOps.autocontrast(lum.resize((COLS, ROWS), Image.BOX), cutoff=1)
    grid = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            v = (small.getpixel((x, y)) / 255) ** 0.8
            row.append(RAMP[min(9, int(v * 10))])
        grid.append(row)
    return grid


def tier(ch):
    i = RAMP.index(ch)
    if i <= 2:
        return "d"   # fondo: . :
    if i <= 5:
        return "m"   # medios: - = +
    if i <= 7:
        return "b"   # brillantes: * #
    return "h"       # máximos: % @


def portrait_svg(grid, ox, oy):
    out = [f'<g class="portrait" transform="translate({ox},{oy})">']
    for y, row in enumerate(grid):
        baseline = (y + 1) * CH
        spans, x = [], 0
        while x < COLS:
            ch = row[x]
            if ch == " ":
                x += 1
                continue
            t, start, run = tier(ch), x, []
            while x < COLS and row[x] != " " and tier(row[x]) == t:
                run.append(row[x])
                x += 1
            xs = " ".join(str(round((start + i) * CW, 1)) for i in range(len(run)))
            spans.append(f'<tspan class="{t}" x="{xs}">{escape("".join(run))}</tspan>')
        if spans:
            out.append(
                f'<text class="row" y="{baseline:.1f}" style="animation-delay:{y * 0.035:.2f}s">'
                + "".join(spans) + "</text>"
            )
    out.append("</g>")
    return "\n".join(out)


TERMINAL = [
    # (prompt, texto, clase)
    ("$ ", "whoami", "cmd"),
    ("> ", "Gustavo Mendoza", "out big"),
    ("$ ", "cat role.txt", "cmd"),
    ("> ", "Full Stack Developer & IT Solutions Engineer", "out"),
    ("$ ", "ls ./focus", "cmd"),
    ("  ", "networking/  automation/  cybersecurity/  fullstack/", "out dirs"),
    ("$ ", "ping tegucigalpa.hn", "cmd"),
    ("> ", "64 bytes from Honduras (HN)  time=0.42ms  ttl=64", "out"),
    ("$ ", "./learn --cloud --devops --security", "cmd"),
    ("> ", "[███████████░░░] 78%  always learning...", "out bar"),
]


def header_svg(grid):
    w, h = 1000, 480
    px, py = 26, 18
    tx, ty, tw, th = 500, 40, 474, 400
    lines = []
    t0, step = 1.6, 0.55
    y = ty + 66
    for i, (prompt, text, cls) in enumerate(TERMINAL):
        delay = t0 + i * step
        steps = max(4, len(text))
        lines.append(
            f'<text class="tl {cls}" x="{tx + 22}" y="{y}" '
            f'style="animation-delay:{delay:.2f}s;animation-timing-function:steps({steps})">'
            f'<tspan class="pr">{escape(prompt)}</tspan>{escape(text)}</text>'
        )
        y += 29 if "cmd" in cls else 34
    cursor_delay = t0 + len(TERMINAL) * step
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Gustavo Mendoza — retrato ASCII y terminal">
<title>Gustavo Mendoza — Developer · Networking · IT Solutions</title>
<defs>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.18"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.25" cy="0.45" r="0.5">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0.10"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#000" opacity="0.35"/>
  </pattern>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<style>
  text {{ font-family: {FONT}; }}
  .portrait text {{ font-size: 9px; font-weight: 700; }}
  .d {{ fill: {DIM}; }}
  .m {{ fill: {MID}; }}
  .b {{ fill: {CYAN}; }}
  .h {{ fill: {ICE}; animation: pulse 3.2s ease-in-out infinite; }}
  .row {{ opacity: 0; animation: reveal .5s ease-out forwards; }}
  .portrait {{ animation: glitch 7s steps(1) infinite 3s; }}
  .scan {{ animation: sweep 4.5s linear infinite; }}
  .tl {{ font-size: 14px; fill: {GREEN}; clip-path: inset(0 100% 0 0); animation-name: type; animation-duration: .45s; animation-fill-mode: forwards; }}
  .tl .pr {{ fill: {DIM}; }}
  .cmd {{ fill: {GREEN}; }}
  .out {{ fill: {CYAN}; }}
  .big {{ font-size: 24px; font-weight: 700; fill: {ICE}; }}
  .dirs {{ fill: {MID}; }}
  .bar {{ fill: {CYAN}; }}
  .label {{ font-size: 11px; fill: {DIM}; letter-spacing: 2px; }}
  .bartitle {{ font-size: 12px; fill: {MID}; }}
  .cursor {{ fill: {GREEN}; opacity: 0; animation: blink 1s steps(1) infinite {cursor_delay:.2f}s; }}
  @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .65; }} }}
  @keyframes sweep {{ from {{ transform: translateY(-120px); }} to {{ transform: translateY({h}px); }} }}
  @keyframes type {{ to {{ clip-path: inset(0 0 0 0); }} }}
  @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
  @keyframes glitch {{
    0%,100% {{ transform: translate({px}px,{py}px); }}
    91% {{ transform: translate({px + 3}px,{py}px); }}
    92% {{ transform: translate({px - 2}px,{py + 1}px); }}
    93% {{ transform: translate({px}px,{py}px); }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .row, .tl, .h, .portrait, .scan, .cursor {{ animation: none !important; opacity: 1; clip-path: none; }}
  }}
</style>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
  {portrait_svg(grid, px, py)}

  <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="#03110f" stroke="{DIM}"/>
  <rect x="{tx}" y="{ty}" width="{tw}" height="30" rx="10" fill="#062320"/>
  <rect x="{tx}" y="{ty + 20}" width="{tw}" height="10" fill="#062320"/>
  <circle cx="{tx + 18}" cy="{ty + 15}" r="5" fill="#ff5f57"/>
  <circle cx="{tx + 36}" cy="{ty + 15}" r="5" fill="#febc2e"/>
  <circle cx="{tx + 54}" cy="{ty + 15}" r="5" fill="#28c840"/>
  <text class="bartitle" x="{tx + tw / 2}" y="{ty + 19}" text-anchor="middle">gustavo@tegucigalpa: ~</text>
  {"".join(lines)}
  <rect class="cursor" x="{tx + 22}" y="{y - 14}" width="9" height="17"/>

  <text class="label" x="{px}" y="{h - 12}">// SIGNAL: STABLE  ·  RES 72x48  ·  ENCODING: ASCII</text>
  <text class="label" x="{w - 24}" y="{h - 12}" text-anchor="end">tavoMend v2.0</text>

  <rect class="scan" x="0" y="0" width="{w}" height="120" fill="url(#scan)"/>
  <rect width="{w}" height="{h}" fill="url(#lines)"/>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{DIM}"/>
</svg>
'''


SECTIONS = {
    "about": ("0x01", "cat about_me.yaml"),
    "projects": ("0x02", "ls ./featured_projects"),
    "stack": ("0x03", "tree ./tech_stack"),
    "stats": ("0x04", "top --user tavoMend"),
    "snake": ("0x05", "./snake --eat-contributions"),
    "strengths": ("0x06", "grep -i positive self.log"),
    "contact": ("0x07", "ssh connect@gustavo"),
}


def section_svg(idx, cmd):
    w, h = 720, 64
    steps = len(cmd)
    tl = len(cmd) * 10.8  # ancho fijo: el cursor queda pegado al texto con cualquier fuente
    cx = 146 + tl + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(cmd)}">
<style>
  text {{ font-family: {FONT}; font-size: 18px; font-weight: 700; }}
  .idx {{ fill: {DIM}; font-size: 13px; letter-spacing: 2px; }}
  .pr {{ fill: {MID}; }}
  .cmd {{ fill: {CYAN}; clip-path: inset(0 100% 0 0); animation: type 1.2s steps({steps}) .3s forwards; }}
  .cur {{ fill: {GREEN}; animation: blink 1s steps(1) infinite; }}
  .rule {{ stroke: {DIM}; stroke-dasharray: 2 5; }}
  @keyframes type {{ to {{ clip-path: inset(0 0 0 0); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .cmd, .cur {{ animation: none; clip-path: none; }} }}
</style>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{DIM}"/>
<text class="idx" x="22" y="38">[{idx}]</text>
<text class="pr" x="96" y="39">~ $</text>
<text class="cmd" x="146" y="39" textLength="{tl:.0f}" lengthAdjust="spacing">{escape(cmd)}</text>
<rect class="cur" x="{min(cx, w - 30):.0f}" y="24" width="10" height="19"/>
</svg>
'''


def divider_svg():
    w, h = 1000, 22
    rng = random.Random(7)
    chars = "".join(rng.choice(".:-=+*#") for _ in range(166))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="g" x1="0" x2="1">
    <stop offset="0" stop-color="{DIM}"/><stop offset=".45" stop-color="{DIM}"/>
    <stop offset=".5" stop-color="{ICE}"/>
    <stop offset=".55" stop-color="{DIM}"/><stop offset="1" stop-color="{DIM}"/>
    <animate attributeName="x1" values="-1;1" dur="3.5s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="0;2" dur="3.5s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<text x="0" y="15" fill="url(#g)" font-family="{FONT}" font-size="10" textLength="{w}" lengthAdjust="spacing">{escape(chars)}</text>
</svg>
'''


def footer_svg():
    w, h = 1000, 170
    rng = random.Random(42)
    rain = []
    for i in range(62):
        x = 8 + i * 16
        col = "".join(rng.choice("01:.+*#=") for _ in range(14))
        dur = rng.uniform(4, 9)
        delay = -rng.uniform(0, dur)
        tspans = "".join(f'<tspan x="{x}" dy="13">{c}</tspan>' for c in col)
        rain.append(
            f'<text class="rain" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s" y="-180">{tspans}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Always building. Always learning.">
<defs>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="1"/>
    <stop offset=".35" stop-color="{BG}" stop-opacity=".2"/>
    <stop offset="1" stop-color="{BG}" stop-opacity=".95"/>
  </linearGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<style>
  text {{ font-family: {FONT}; }}
  .rain {{ font-size: 12px; fill: {DIM}; animation: fall linear infinite; }}
  .msg {{ font-size: 22px; font-weight: 700; fill: {CYAN}; }}
  .sub {{ font-size: 12px; fill: {MID}; letter-spacing: 3px; }}
  .cur {{ fill: {GREEN}; animation: blink 1s steps(1) infinite; }}
  @keyframes fall {{ from {{ transform: translateY(0); }} to {{ transform: translateY(360px); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .rain, .cur {{ animation: none; }} }}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  {"".join(rain)}
  <rect width="{w}" height="{h}" fill="url(#fade)"/>
  <text class="msg" x="{w / 2}" y="86" text-anchor="middle" textLength="440" lengthAdjust="spacing">Always building. Always learning.</text>
  <rect class="cur" x="{w / 2 + 230}" y="68" width="11" height="22"/>
  <text class="sub" x="{w / 2}" y="118" text-anchor="middle">[ process exited with code 0 ]</text>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{DIM}"/>
</svg>
'''


def main():
    if len(sys.argv) < 2:
        sys.exit('uso: py scripts/generate.py "ruta/a/foto.png"')
    (ASSETS / "sections").mkdir(parents=True, exist_ok=True)
    grid = portrait_grid(sys.argv[1])
    (ASSETS / "header.svg").write_text(header_svg(grid), encoding="utf-8")
    (ASSETS / "divider.svg").write_text(divider_svg(), encoding="utf-8")
    (ASSETS / "footer.svg").write_text(footer_svg(), encoding="utf-8")
    for name, (idx, cmd) in SECTIONS.items():
        (ASSETS / "sections" / f"{name}.svg").write_text(section_svg(idx, cmd), encoding="utf-8")
    print("listo:", *sorted(p.relative_to(ROOT).as_posix() for p in ASSETS.rglob("*.svg")), sep="\n  ")


if __name__ == "__main__":
    main()
