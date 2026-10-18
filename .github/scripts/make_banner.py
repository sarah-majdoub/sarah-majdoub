"""Generate the typing banner as two SVGs (light and dark) under assets/."""

from pathlib import Path
from xml.sax.saxutils import escape

PREFIX = "I work on "
PHRASES = [
    "computer vision",
    "applied machine learning",
    "data engineering",
    "retrieval & RAG",
]

TYPE, DELETE, HOLD, GAP = 0.08, 0.035, 1.8, 0.4

THEMES = {
    "light": {"text": "#1f2328", "accent": "#0969da"},
    "dark": {"text": "#e6edf3", "accent": "#58a6ff"},
}


def slots():
    t = 0.0
    for phrase in PHRASES:
        n = len(phrase)
        length = n * TYPE + HOLD + n * DELETE + GAP
        yield phrase, t, length
        t += length


CYCLE = sum(length for _, _, length in slots())


def display(start, end):
    """SMIL animation that shows an element only between start and end seconds."""
    a, b = start / CYCLE, end / CYCLE
    if a <= 0:
        values, times = "inline;none", f"0;{b:.4f}"
    else:
        values, times = "none;inline;none", f"0;{a:.4f};{b:.4f}"
    return (
        f'<animate attributeName="display" values="{values}" keyTimes="{times}" '
        f'dur="{CYCLE:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'
    )


def svg(theme):
    colors = THEMES[theme]
    texts = []
    for phrase, start, length in slots():
        typed_end = start + len(phrase) * TYPE + HOLD
        # Hidden tspans drop out of text layout, so the cursor tracks the last visible character.
        chars = "".join(
            f'<tspan fill="{colors["accent"]}" display="none">{escape(c)}'
            f"{display(start + k * TYPE, typed_end + (len(phrase) - 1 - k) * DELETE)}</tspan>"
            for k, c in enumerate(phrase)
        )
        cursor = (
            f'<tspan fill="{colors["accent"]}">▍<animate attributeName="opacity" '
            f'values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></tspan>'
        )
        texts.append(
            f'<text x="0" y="30" display="none" xml:space="preserve">{escape(PREFIX)}{chars}{cursor}'
            f"{display(start, start + length)}</text>"
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="44" viewBox="0 0 640 44">'
        f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="24" fill="{colors["text"]}">{"".join(texts)}</g></svg>\n'
    )


def main():
    out = Path("assets")
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        (out / f"typing-{theme}.svg").write_text(svg(theme))


if __name__ == "__main__":
    main()
