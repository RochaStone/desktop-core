#!/usr/bin/env python3
"""desktop-core: turn desktop.config.json into a deployable link-in-bio folder.

  python3 build.py desktop.config.json --out site/
  python3 build.py desktop.config.json --out site/ --motif analog --style path/to/style.json
  python3 build.py --refresh-template      (rewrites the root index.html with the bundled example)

The page is one file, index.html, with no framework. This script checks the config, finds the style,
and writes the config, the style and the motif into a copy of index.html. Plain Python, standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "index.html"
EXAMPLE_CONFIG = HERE / "desktop.config.json"
STYLE_EXAMPLE = HERE / "examples" / "style.rocha-coded.json"
MOTIFS = ("analog", "cyberpunk", "y2k-blog")
DEFAULT_MOTIF = "y2k-blog"
MOTIF_ALIASES = {"guest-check": "analog", "front-page": "analog", "magazine-scrawl": "analog",
                 "pink-paper": "analog", "rotary": "analog", "leopard": "analog", "neutral": "analog",
                 "retro-tv": "cyberpunk", "sticker-collage": "y2k-blog", "y2k": "y2k-blog", "blog": "y2k-blog"}
COLOUR = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
FONT_NAME = re.compile(r"^[A-Za-z0-9 ]{1,40}$")
URL = re.compile(r"^(https?://|mailto:)[^\s\"'<>]+$", re.I)
BLOCK = '<script type="application/json" id="{id}">'
LIMITS = {"folders": 10, "notes": 6, "trash": 12, "links": 8, "currently": 6}


# ---------- config ----------

def resolve_alias(motif: object) -> str | None:
    raw = str(motif or "").strip().lower()
    raw = MOTIF_ALIASES.get(raw, raw)
    return raw if raw in MOTIFS else None


def validate_config(cfg: object) -> list[str]:
    """Return a list of kind, plain-English problems. An empty list means the config is ready."""
    if not isinstance(cfg, dict):
        return ["The config should be one { ... } block. Start from desktop.config.json in this folder."]
    errs: list[str] = []

    def text(key: str, val: object, required: bool = False, cap: int = 400) -> None:
        if val is None or val == "":
            if required:
                errs.append(f'"{key}" is missing. Add it, for example "{key}": "Your Studio".')
            return
        if not isinstance(val, str):
            errs.append(f'"{key}" should be words in quotes.')
        elif len(val) > cap:
            errs.append(f'"{key}" is {len(val)} characters. Keep it under {cap}.')

    def url(key: str, val: object, required: bool = False) -> None:
        if not val:
            if required:
                errs.append(f'"{key}" needs a link that starts with https://')
            return
        if not isinstance(val, str) or not URL.match(val.strip()):
            errs.append(f'"{key}" should be a full link that starts with https:// (or mailto:). Got: {str(val)[:60]}')

    def items(key: str, kind: type) -> list:
        val = cfg.get(key, [])
        if val in (None, ""):
            return []
        if not isinstance(val, kind):
            errs.append(f'"{key}" should be a {"list in [ ]" if kind is list else "block in { }"}.')
            return []
        if len(val) > LIMITS[key]:
            errs.append(f'"{key}" has {len(val)} entries. The desktop fits {LIMITS[key]}, so pick your favourites.')
        return list(val.items()) if kind is dict else val

    text("name", cfg.get("name"), required=True, cap=60)
    text("tagline", cfg.get("tagline"))
    text("mood", cfg.get("mood"), cap=80)
    if cfg.get("motif") not in (None, "") and not resolve_alias(cfg.get("motif")):
        errs.append(f'"motif" should be analog, cyberpunk or y2k-blog. Got: {cfg.get("motif")}')
    if "counter" in cfg and not (isinstance(cfg["counter"], int) and not isinstance(cfg["counter"], bool)
                                 and cfg["counter"] >= 0):
        errs.append('"counter" should be a whole number, like 777.')
    for i, f in enumerate(items("folders", list)):
        if not isinstance(f, dict):
            errs.append(f"folders[{i}] should be a block in {{ }} with a name.")
            continue
        text(f"folders[{i}].name", f.get("name"), required=True, cap=40)
        text(f"folders[{i}].blurb", f.get("blurb"))
        text(f"folders[{i}].cta", f.get("cta"), cap=40)
        url(f"folders[{i}].url", f.get("url"))
        if f.get("items") not in (None, "") and not (isinstance(f["items"], list)
                                                     and all(isinstance(x, str) for x in f["items"])):
            errs.append(f"folders[{i}].items should be a list of short lines in quotes.")
    for i, n in enumerate(items("notes", list)):
        if not isinstance(n, dict):
            errs.append(f'notes[{i}] should be a block like {{"text": "...", "from": "..."}}.')
            continue
        text(f"notes[{i}].text", n.get("text"), required=True, cap=240)
        text(f"notes[{i}].from", n.get("from"), cap=60)
    for i, t in enumerate(items("trash", list)):
        text(f"trash[{i}]", t, required=True, cap=120)
    for k, v in items("currently", dict):
        text(f"currently.{k}", v, cap=120)
    for i, link in enumerate(items("links", list)):
        if not isinstance(link, dict):
            errs.append(f'links[{i}] should be a block like {{"label": "instagram", "url": "https://..."}}.')
            continue
        text(f"links[{i}].label", link.get("label"), required=True, cap=40)
        url(f"links[{i}].url", link.get("url"), required=True)
    clock = cfg.get("clock")
    if clock not in (None, ""):
        if not isinstance(clock, dict):
            errs.append('"clock" should be a block like {"label": "book a call", "url": "https://..."}.')
        else:
            text("clock.label", clock.get("label"), cap=40)
            url("clock.url", clock.get("url"))
    url("guestbookUrl", cfg.get("guestbookUrl"))
    return errs


def load_config(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Could not open {path}. Check the file name and try again. ({exc.strerror})")
    except ValueError as exc:
        raise SystemExit(f"{path} is not valid JSON yet. Look near line {getattr(exc, 'lineno', '?')}: "
                         "a missing comma or quote is the usual reason.")


# ---------- style.json (shared Rocha Coded schema) ----------

def find_style(explicit: Path | None = None, cwd: Path | None = None, home: Path | None = None) -> Path:
    """./style.json, then ~/.rocha-coded/style.json, then the bundled example."""
    if explicit:
        return Path(explicit)
    for cand in ((cwd or Path.cwd()) / "style.json", (home or Path.home()) / ".rocha-coded" / "style.json"):
        if cand.is_file():
            return cand
    return STYLE_EXAMPLE


def inherit_style(user: dict) -> dict:
    """A user's style borrows ONLY missing palette and font entries from the bundled example.
    Lines, owner, handle, name, references and notes never fall back to Rocha's."""
    try:
        example = json.loads(STYLE_EXAMPLE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        example = {}
    merged = dict(user)
    for key in ("palette", "fonts"):
        mine = user.get(key) if isinstance(user.get(key), dict) else {}
        base = example.get(key) if isinstance(example.get(key), dict) else {}
        merged[key] = {**base, **{k: v for k, v in mine.items() if str(v or "").strip()}}
    return merged


def load_style(path: Path | None = None) -> tuple[dict, bool]:
    """Return (style, is_bundled_example)."""
    path = Path(path or STYLE_EXAMPLE)
    bundled = path.resolve() == STYLE_EXAMPLE.resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Could not read style file {path} ({exc}). Using the bundled example look.", file=sys.stderr)
        data, bundled = json.loads(STYLE_EXAMPLE.read_text(encoding="utf-8")), True
    data = data if isinstance(data, dict) else {}
    return (data if bundled else inherit_style(data)), bundled


def page_style(style: dict) -> dict:
    """Only what the page uses, with every colour and font name checked."""
    pal = style.get("palette") if isinstance(style.get("palette"), dict) else {}
    fonts = style.get("fonts") if isinstance(style.get("fonts"), dict) else {}
    lines = style.get("lines") if isinstance(style.get("lines"), dict) else {}
    stamp = str(lines.get("stamp") or "").strip()[:24]
    return {"palette": {k: v for k, v in pal.items() if isinstance(v, str) and COLOUR.match(v.strip())},
            "fonts": {k: v for k, v in fonts.items() if isinstance(v, str) and FONT_NAME.match(v.strip())},
            "lines": {"stamp": stamp} if stamp else {}}


def resolve_motif(cli: str | None, cfg: dict, style: dict, style_is_example: bool) -> str:
    """--motif, then the config's motif, then her own style.json motif, then y2k-blog.
    The bundled example's motif is never used here: this tool's house default is y2k-blog."""
    for cand in (cli, cfg.get("motif"), None if style_is_example else style.get("motif")):
        m = resolve_alias(cand)
        if m:
            return m
    return DEFAULT_MOTIF


# ---------- build ----------

def _json_block(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def fill_template(template: str, cfg: dict, style: dict, meta: dict) -> str:
    for bid, data in (("desktop-config", cfg), ("desktop-style", style), ("desktop-meta", meta)):
        pat = re.compile(re.escape(BLOCK.format(id=bid)) + r".*?</script>", re.S)
        if not pat.search(template):
            raise SystemExit(f"index.html is missing its {bid} block. Re-download the tool to repair it.")
        template = pat.sub(lambda _m, b=bid, d=data: BLOCK.format(id=b) + _json_block(d) + "</script>", template, 1)
    return template


def build(cfg: dict, out: Path, motif: str | None = None, style_path: Path | None = None,
          today: str | None = None) -> Path:
    errs = validate_config(cfg)
    if errs:
        raise ValueError("\n".join(errs))
    style, is_example = load_style(find_style(style_path))
    meta = {"motif": resolve_motif(motif, cfg, style, is_example), "built": today or dt.date.today().isoformat()}
    html = fill_template(TEMPLATE.read_text(encoding="utf-8"), cfg, page_style(style), meta)
    out.mkdir(parents=True, exist_ok=True)
    page = out / "index.html"
    page.write_text(html, encoding="utf-8")
    return page


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build your 2003 desktop link-in-bio into one deployable folder.")
    ap.add_argument("config", nargs="?", default="desktop.config.json", help="your desktop.config.json")
    ap.add_argument("--out", default="site", help="folder to write (default: site/)")
    ap.add_argument("--motif", choices=MOTIFS, help="analog, cyberpunk or y2k-blog (default: the config's motif)")
    ap.add_argument("--style", type=Path, help="a style.json somewhere else")
    ap.add_argument("--refresh-template", action="store_true", help="rewrite the root index.html with the example")
    a = ap.parse_args(argv)
    if a.refresh_template:
        style, _ = load_style(STYLE_EXAMPLE)
        cfg = load_config(EXAMPLE_CONFIG)
        TEMPLATE.write_text(fill_template(TEMPLATE.read_text(encoding="utf-8"), cfg, page_style(style),
                                          {"motif": resolve_motif(None, cfg, style, True)}), encoding="utf-8")
        print("index.html now shows the bundled example desktop.")
        return 0
    cfg = load_config(Path(a.config))
    try:
        page = build(cfg, Path(a.out), a.motif, a.style)
    except ValueError as exc:
        print("A few things to fix in your config first:", file=sys.stderr)
        for line in str(exc).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(f"READY. Your desktop is in {page.parent}/ (open {page} to see it).")
    print("Upload that folder to GitHub Pages or Vercel to put it online.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
