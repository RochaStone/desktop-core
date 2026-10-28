#!/usr/bin/env python3
"""Generate every image the README uses, from the tool itself. Needs Chrome or Chromium for the PNGs.

  python3 scripts/make-readme-images.py

Writes:
  docs/img/hero-y2k.png        the example desktop in the y2k-blog motif (1280x800)
  docs/img/triptych.png        the same desktop in analog | cyberpunk | y2k-blog (1620x420)
  docs/img/phone.png           the three motifs side by side at phone width (390px each)
  docs/img/step-01..05.svg     pixel step badges for "Start here"
  docs/img/divider.svg         a gold pixel hairline
  docs/img/heart.svg           a pixel heart
  docs/IMAGES.md               the list of all of the above
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402
import render  # noqa: E402

IMG = ROOT / "docs" / "img"
DIGITS = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
          "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
          "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"]}
ORDER = ("analog", "cyberpunk", "y2k-blog")


def _pixels(text: str, x0: int, y0: int) -> str:
    return "".join(f"M{x0 + n * 4 + c} {y0 + r}h1v1h-1z" for n, ch in enumerate(text)
                   for r, row in enumerate(DIGITS[ch]) for c, bit in enumerate(row) if bit == "1")


def badge(num: str, ground: str, gold: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 11 9" width="33" height="27" '
            f'shape-rendering="crispEdges"><path fill="{ground}" d="M1 0h9v1h1v7h-1v1H1v-1H0V1h1z"/>'
            f'<path fill="{gold}" d="{_pixels(num, 2, 2)}"/></svg>\n')


def divider(gold: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="6" shape-rendering="crispEdges">'
            '<defs><pattern id="p" width="12" height="6" patternUnits="userSpaceOnUse">'
            f'<rect width="6" height="2" y="2" fill="{gold}"/><rect x="8" y="2" width="2" height="2" fill="{gold}"/>'
            '</pattern></defs><rect width="720" height="6" fill="url(#p)"/></svg>\n')


def heart(colour: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 7 6" width="21" height="18" shape-rendering="crispEdges">'
            f'<path fill="{colour}" d="M1 0h2v1h1V0h2v1h1v2H6v1H5v1H4v1H3V5H2V4H1V3H0V1h1z"/></svg>\n')


def strip_html(cells: list[tuple[str, str]], w: int, h: int, cell_w: int, ground: str, gold: str, cream: str) -> str:
    figs = "".join(f'<figure><img src="{src}" style="width:{cell_w}px"><figcaption>{cap}</figcaption></figure>'
                   for cap, src in cells)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Silkscreen&display=swap">
<style>*{{margin:0;box-sizing:border-box}}body{{width:{w}px;height:{h}px;background:{ground};display:flex;gap:24px;
padding:20px 30px;justify-content:center;align-items:flex-start}}figure{{display:flex;flex-direction:column;align-items:center;gap:10px}}
img{{height:auto;border:2px solid {gold};display:block}}figcaption{{font-family:"Silkscreen",monospace;color:{cream};font-size:20px}}
</style></head><body>{figs}</body></html>"""


def phone_html(page: Path) -> str:
    frames = "".join(f'<iframe src="{page.as_uri()}?motif={m}" style="width:390px;height:844px;border:0;display:block"></iframe>'
                     for m in ORDER)
    return f'<!doctype html><html><body style="margin:0;display:flex;gap:0">{frames}</body></html>'


def main() -> int:
    style, _ = build.load_style(build.STYLE_EXAMPLE)
    pal = style["palette"]
    ground, gold, cream, candy = pal["hero"], pal["gold"], pal["paper"], pal["accent"]
    IMG.mkdir(parents=True, exist_ok=True)
    for i in range(1, 6):
        (IMG / f"step-{i:02d}.svg").write_text(badge(f"{i:02d}", ground, gold), encoding="utf-8")
    (IMG / "divider.svg").write_text(divider(gold), encoding="utf-8")
    (IMG / "heart.svg").write_text(heart(candy), encoding="utf-8")
    print("SVGs: step-01..05, divider, heart")

    ok_all = True
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cfg = build.load_config(build.EXAMPLE_CONFIG)
        page = build.build(cfg, tmp / "site", style_path=build.STYLE_EXAMPLE, today="2026-10-28")
        shots = {}
        for motif in ORDER:
            png = tmp / f"{motif}.png"
            ok, msg = render.screenshot(page.as_uri() + "?motif=" + motif, png, 1280, 800)
            print(msg)
            if not ok:
                ok_all = False
                break
            shots[motif] = png
        if ok_all:
            (IMG / "hero-y2k.png").write_bytes(shots["y2k-blog"].read_bytes())
            strip = tmp / "triptych.html"
            strip.write_text(strip_html([(m, shots[m].as_uri()) for m in ORDER], 1620, 420, 500, ground, gold, cream),
                             encoding="utf-8")
            ok, msg = render.screenshot(strip.as_uri(), IMG / "triptych.png", 1620, 420)
            print(msg)
            phones = tmp / "phones.html"
            phones.write_text(phone_html(page), encoding="utf-8")
            ok2, msg = render.screenshot(phones.as_uri(), IMG / "phone.png", 1170, 844)
            print(msg)
            ok_all = ok and ok2

    (ROOT / "docs" / "IMAGES.md").write_text("""# Images

Every image here is generated by `scripts/make-readme-images.py` from the fictional example in `desktop.config.json`.
No photos, no real people, no real businesses. Juniper Lark and every name on the sticky notes are made up.

| File | What it is |
|---|---|
| `docs/img/hero-y2k.png` | the example desktop in the y2k-blog motif at 1280x800, used as the README hero |
| `docs/img/triptych.png` | the same desktop in analog, cyberpunk and y2k-blog, side by side |
| `docs/img/phone.png` | the three motifs at phone width (390px each), stacked windows, no sideways scroll |
| `docs/img/step-01.svg` to `step-05.svg` | pixel step badges for "Start here" |
| `docs/img/divider.svg` | a gold pixel hairline between README sections |
| `docs/img/heart.svg` | the pixel heart beside "If it goes wrong" and the guestbook line |
""", encoding="utf-8")
    print("docs/IMAGES.md written" + ("" if ok_all else " (PNGs skipped: no Chrome)"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
