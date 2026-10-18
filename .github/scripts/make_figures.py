"""Generate the animated figures (key numbers, experience timeline, MindRAG pipeline) under assets/."""

from pathlib import Path
from xml.sax.saxutils import escape

from make_banner import THEMES

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# (final value, format, label)
NUMBERS = [
    (0.84, lambda v: f"{v:.2f}", "R² · fruit weight from RGB"),
    (40, lambda v: f"~{v:.0f}M", "records · Spark pipeline"),
    (2719, lambda v: f"{v:,.0f}", "companies · async scraper"),
    (4, lambda v: f"{v:.0f}", "internships since 2024"),
]

# Months counted from Oct 2024; end is exclusive.
TIMELINE_START = (2024, 10)
TIMELINE_MONTHS = 36
ROLES = [
    ("Colocqui", "Frontend", 1, 4),
    ("TUNIDEV", "Full-stack", 9, 12),
    ("Datalia", "Full-stack", 17, 19),
    ("vGreens", "Data science / CV", 21, 24),
    ("Next", "End-of-study internship", 28, 34),
]

STAGES = [
    ("Query", "rewrite"),
    ("Keyword", "routing"),
    ("BM25 + dense", "65 / 35"),
    ("RRF", "fusion"),
    ("Cross-encoder", "rerank"),
    ("Local LLM", "Ollama"),
]


def wrap(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{SANS}">{body}</svg>\n'
    )


def fade_in(begin, dy=8):
    return (
        f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.5s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 {dy}" to="0 0" '
        f'begin="{begin}s" dur="0.5s" fill="freeze"/>'
    )


def numbers(c):
    tile_w, gap, h, frames, dur = 185, 20, 96, 24, 1.4
    tiles = []
    for i, (value, fmt, label) in enumerate(NUMBERS):
        x = i * (tile_w + gap)
        start = 0.15 * i
        count = []
        for f in range(frames + 1):
            eased = 1 - (1 - f / frames) ** 3
            begin = start + dur * f / frames
            show = f'<set attributeName="display" to="inline" begin="{begin:.3f}s"/>'
            hide = "" if f == frames else (
                f'<set attributeName="display" to="none" begin="{start + dur * (f + 1) / frames:.3f}s"/>'
            )
            count.append(
                f'<text x="{x + 18}" y="50" font-size="34" font-weight="700" fill="{c["accent"]}" '
                f'display="none">{escape(fmt(value * eased))}{show}{hide}</text>'
            )
        tiles.append(
            f'<g opacity="0">{fade_in(start)}'
            f'<rect x="{x + 0.5}" y="0.5" width="{tile_w - 1}" height="{h - 1}" rx="10" '
            f'fill="{c["surface"]}" stroke="{c["border"]}"/>'
            f'{"".join(count)}'
            f'<text x="{x + 18}" y="76" font-size="13" fill="{c["muted"]}">{escape(label)}</text></g>'
        )
    return wrap(800, h, "".join(tiles))


def timeline(c):
    label_w, width, row_h, top = 230, 800, 34, 8
    scale = (width - label_w - 10) / TIMELINE_MONTHS
    axis_y = top + row_h * len(ROLES) + 6
    body = []

    for year in (2025, 2026, 2027):
        m = (year - TIMELINE_START[0]) * 12 + 1 - TIMELINE_START[1]
        x = label_w + m * scale
        body.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{axis_y}" stroke="{c["border"]}" stroke-dasharray="2 4"/>'
            f'<text x="{x:.1f}" y="{axis_y + 18}" font-size="12" fill="{c["muted"]}" text-anchor="middle">{year}</text>'
        )

    for i, (company, role, start, end) in enumerate(ROLES):
        y = top + i * row_h
        x, w = label_w + start * scale, (end - start) * scale
        begin = 0.3 + 0.35 * i
        future = i == len(ROLES) - 1
        if future:
            bar = (
                f'<rect x="{x:.1f}" y="{y + 7}" width="{w:.1f}" height="16" rx="4" fill="none" '
                f'stroke="{c["accent"]}" stroke-width="1.5" stroke-dasharray="5 4" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0.35;1" keyTimes="0;0.15;0.6;1" '
                f'begin="{begin}s" dur="2.4s" repeatCount="indefinite"/></rect>'
            )
        else:
            bar = (
                f'<rect x="{x:.1f}" y="{y + 7}" width="0" height="16" rx="4" fill="{c["accent"]}">'
                f'<animate attributeName="width" from="0" to="{w:.1f}" begin="{begin}s" dur="0.6s" '
                f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>'
            )
        body.append(
            f'<g opacity="0">{fade_in(begin - 0.2, dy=0)}'
            f'<text x="0" y="{y + 20}" font-size="14" font-weight="600" fill="{c["text"]}">{escape(company)}'
            f'<tspan font-weight="400" fill="{c["muted"]}"> · {escape(role)}</tspan></text></g>{bar}'
        )
    return wrap(width, axis_y + 26, "".join(body))


def pipeline(c):
    box_w, gap, box_h, x0, y0, dur = 110, 26, 56, 8, 10, 6.0
    width = x0 * 2 + len(STAGES) * box_w + (len(STAGES) - 1) * gap
    mid = y0 + box_h / 2
    span = width - 2 * x0
    body = [
        f'<defs><marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
        f'orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="{c["muted"]}"/></marker></defs>'
    ]
    for i, (top, bottom) in enumerate(STAGES):
        x = x0 + i * (box_w + gap)
        if i:
            body.append(
                f'<line x1="{x - gap + 2}" y1="{mid}" x2="{x - 3}" y2="{mid}" stroke="{c["muted"]}" '
                f'stroke-width="1.5" marker-end="url(#arrow)"/>'
            )
        # Light the box up while the travelling dot is over it.
        a = (x - x0) / span
        b = min((x + box_w - x0) / span, 0.98)
        times = f"0;{a:.3f};{a + 0.01:.3f};{b:.3f};{min(b + 0.06, 0.99):.3f};1"
        body.append(
            f'<rect x="{x}" y="{y0}" width="{box_w}" height="{box_h}" rx="10" fill="{c["surface"]}" '
            f'stroke="{c["border"]}" stroke-width="1.5">'
            f'<animate attributeName="stroke" values="{c["border"]};{c["border"]};{c["accent"]};{c["accent"]};{c["border"]};{c["border"]}" '
            f'keyTimes="{times}" dur="{dur}s" repeatCount="indefinite"/></rect>'
            f'<text x="{x + box_w / 2}" y="{y0 + 24}" font-size="13" font-weight="600" fill="{c["text"]}" '
            f'text-anchor="middle">{escape(top)}</text>'
            f'<text x="{x + box_w / 2}" y="{y0 + 42}" font-size="12" fill="{c["muted"]}" '
            f'text-anchor="middle">{escape(bottom)}</text>'
        )
    track_y = y0 + box_h + 12
    body.append(
        f'<line x1="{x0}" y1="{track_y}" x2="{width - x0}" y2="{track_y}" stroke="{c["border"]}"/>'
        f'<circle r="5" cy="{track_y}" fill="{c["accent"]}">'
        f'<animate attributeName="cx" from="{x0}" to="{width - x0}" dur="{dur}s" repeatCount="indefinite"/></circle>'
    )
    return wrap(width, track_y + 10, "".join(body))


def main():
    out = Path("assets")
    out.mkdir(exist_ok=True)
    for name, build in (("numbers", numbers), ("timeline", timeline), ("pipeline", pipeline)):
        for theme, colors in THEMES.items():
            (out / f"{name}-{theme}.svg").write_text(build(colors))


if __name__ == "__main__":
    main()
