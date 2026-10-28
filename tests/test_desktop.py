"""Tests for desktop-core. Run: python3 -m unittest discover -s tests -v

The headless-Chrome tests skip, with a message, when Chrome is not installed.
"""
from __future__ import annotations

import copy
import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402
import render  # noqa: E402

EXAMPLE = json.loads((ROOT / "desktop.config.json").read_text(encoding="utf-8"))
ROCHA = json.loads((ROOT / "examples" / "style.rocha-coded.json").read_text(encoding="utf-8"))
CHROME = render.find_chrome()


def block(html: str, bid: str) -> dict:
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % bid, html, re.S)
    return json.loads(m.group(1))


class ConfigValidation(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(build.validate_config(EXAMPLE), [])

    def test_name_required(self):
        cfg = copy.deepcopy(EXAMPLE)
        del cfg["name"]
        errs = build.validate_config(cfg)
        self.assertTrue(any('"name" is missing' in e for e in errs))

    def test_unsafe_and_bare_links_rejected(self):
        cfg = copy.deepcopy(EXAMPLE)
        cfg["links"][0]["url"] = "javascript:alert(1)"
        cfg["clock"]["url"] = "example.com/book"
        errs = build.validate_config(cfg)
        self.assertTrue(any("links[0].url" in e for e in errs))
        self.assertTrue(any("clock.url" in e for e in errs))

    def test_limits_types_and_motif(self):
        cfg = copy.deepcopy(EXAMPLE)
        cfg["notes"] = [{"text": "x"}] * 7
        cfg["motif"] = "vaporwave"
        cfg["counter"] = "lots"
        cfg["currently"] = ["reading"]
        cfg["folders"].append({"blurb": "no name"})
        errs = "\n".join(build.validate_config(cfg))
        for needle in ('"notes" has 7', '"motif" should be', '"counter" should be', '"currently" should be',
                       "folders[4].name"):
            self.assertIn(needle, errs)

    def test_not_a_dict(self):
        self.assertEqual(len(build.validate_config(["nope"])), 1)

    def test_old_motif_names_still_work(self):
        self.assertEqual(build.resolve_alias("guest-check"), "analog")
        self.assertEqual(build.resolve_alias("retro-tv"), "cyberpunk")
        self.assertEqual(build.resolve_alias("blog"), "y2k-blog")
        self.assertIsNone(build.resolve_alias("vaporwave"))


class StyleAndInheritance(unittest.TestCase):
    def test_fallback_order(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as home:
            cwd, home = Path(cwd), Path(home)
            self.assertEqual(build.find_style(cwd=cwd, home=home), build.STYLE_EXAMPLE)
            (home / ".rocha-coded").mkdir()
            (home / ".rocha-coded" / "style.json").write_text("{}")
            self.assertEqual(build.find_style(cwd=cwd, home=home), home / ".rocha-coded" / "style.json")
            (cwd / "style.json").write_text("{}")
            self.assertEqual(build.find_style(cwd=cwd, home=home), cwd / "style.json")

    def test_user_style_borrows_only_palette_and_fonts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "style.json"
            p.write_text(json.dumps({"palette": {"hero": "#112233", "accent": ""}, "fonts": {"masthead": "Bodoni Moda"},
                                     "motif": "cyberpunk"}))
            style, is_example = build.load_style(p)
        self.assertFalse(is_example)
        self.assertEqual(style["palette"]["hero"], "#112233")
        self.assertEqual(style["palette"]["accent"], ROCHA["palette"]["accent"])  # blank borrows
        self.assertEqual(style["palette"]["gold"], ROCHA["palette"]["gold"])
        self.assertEqual(style["fonts"]["masthead"], "Bodoni Moda")
        self.assertEqual(style["fonts"]["mono"], ROCHA["fonts"]["mono"])
        for key in ("lines", "owner", "handle", "name", "references", "notes"):
            self.assertNotIn(key, style, f"{key} must never fall back to Rocha's")
        self.assertEqual(build.page_style(style)["lines"], {})  # no LORE stamp on her desktop

    def test_bundled_example_keeps_rocha_lines(self):
        style, is_example = build.load_style(build.STYLE_EXAMPLE)
        self.assertTrue(is_example)
        self.assertEqual(build.page_style(style)["lines"], {"stamp": "LORE"})

    def test_bad_colours_and_fonts_dropped(self):
        ps = build.page_style({"palette": {"hero": "red;}</style>", "ink": "#3B1230"},
                               "fonts": {"label": "Evil</style>", "mono": "DM Mono"}})
        self.assertEqual(ps["palette"], {"ink": "#3B1230"})
        self.assertEqual(ps["fonts"], {"mono": "DM Mono"})

    def test_example_files_share_keys(self):
        blank = json.loads((ROOT / "style.example.json").read_text(encoding="utf-8"))
        self.assertEqual(set(blank), set(ROCHA))
        for k in ("palette", "fonts", "lines"):
            self.assertEqual(set(blank[k]), set(ROCHA[k]))

    def test_motif_order(self):
        cfg = {"name": "x"}
        self.assertEqual(build.resolve_motif(None, cfg, ROCHA, True), "y2k-blog")  # bundled analog is ignored
        self.assertEqual(build.resolve_motif(None, cfg, {"motif": "retro-tv"}, False), "cyberpunk")
        self.assertEqual(build.resolve_motif(None, {"motif": "analog"}, {"motif": "cyberpunk"}, False), "analog")
        self.assertEqual(build.resolve_motif("cyberpunk", {"motif": "analog"}, {}, False), "cyberpunk")


class BuildOutput(unittest.TestCase):
    def test_build_writes_one_file_with_config_style_and_meta(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = build.build(EXAMPLE, Path(tmp) / "site", motif="analog", style_path=build.STYLE_EXAMPLE,
                               today="2026-10-28")
            files = sorted(p.name for p in page.parent.iterdir())
            html = page.read_text(encoding="utf-8")
        self.assertEqual(files, ["index.html"])
        self.assertEqual(block(html, "desktop-config"), EXAMPLE)
        self.assertEqual(block(html, "desktop-meta"), {"motif": "analog", "built": "2026-10-28"})
        self.assertEqual(block(html, "desktop-style")["lines"], {"stamp": "LORE"})

    def test_script_breakout_is_escaped(self):
        cfg = copy.deepcopy(EXAMPLE)
        cfg["tagline"] = "</script><script>alert(1)</script>"
        with tempfile.TemporaryDirectory() as tmp:
            html = build.build(cfg, Path(tmp), style_path=build.STYLE_EXAMPLE).read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)", html)
        self.assertEqual(block(html, "desktop-config")["tagline"], cfg["tagline"])

    def test_invalid_config_refuses_to_build(self):
        with self.assertRaises(ValueError):
            build.build({"tagline": "no name"}, Path(tempfile.gettempdir()) / "dc-never")

    def test_cli_kind_message_on_bad_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "c.json"
            p.write_text(json.dumps({"links": [{"label": "x", "url": "nope"}]}))
            err = io.StringIO()
            with redirect_stderr(err), redirect_stdout(io.StringIO()):
                code = build.main([str(p), "--out", str(Path(tmp) / "site")])
        self.assertEqual(code, 1)
        self.assertIn("A few things to fix", err.getvalue())

    def test_root_page_shows_the_example(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(block(html, "desktop-config"), EXAMPLE)
        self.assertEqual(block(html, "desktop-meta")["motif"], "y2k-blog")

    def test_no_glow_no_framework_no_innerhtml(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("text-shadow", html)
        self.assertNotIn("innerHTML", html)
        self.assertNotRegex(html, r"<script[^>]+src=")
        self.assertIn("localStorage", html)
        self.assertIn("catch (err)", html)


@unittest.skipUnless(CHROME, "Chrome or Chromium not found: headless render tests skipped")
class HeadlessRender(unittest.TestCase):
    MARKERS = {"y2k-blog": "you are visitor no.", "cyberpunk": "juniper-lark:~$", "analog": "OCT 2026"}

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.page = build.build(EXAMPLE, Path(cls.tmp.name) / "site", style_path=build.STYLE_EXAMPLE,
                               today="2026-10-28")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_each_motif_renders_without_sideways_scroll(self):
        for motif in build.MOTIFS:
            for width in (1280, 390):
                with self.subTest(motif=motif, width=width):
                    r = render.measure(self.page, width, 900, "?motif=" + motif)
                    self.assertNotIn("error", r, r)
                    self.assertEqual(r["ready"], motif)
                    self.assertEqual(r["iw"], width)
                    self.assertLessEqual(r["sw"], width, f"{motif} is {r['sw']}px wide at {width}px")
                    self.assertIn(self.MARKERS[motif], r["text"])
                    self.assertIn("Juniper Lark", r["text"])
                    self.assertEqual(r["wins"], 2)  # welcome and currently open
                    if motif == "analog":
                        self.assertGreater(r["tape"], 0)
                    if motif == "cyberpunk":
                        self.assertGreater(r["prompt"], 0)

    def test_png_widths(self):
        with tempfile.TemporaryDirectory() as tmp:
            for motif in build.MOTIFS:
                for width in (1280, 390):
                    png = Path(tmp) / f"{motif}-{width}.png"
                    ok, msg = render.screenshot(self.page.as_uri() + "?motif=" + motif, png, width, 844)
                    self.assertTrue(ok, msg)
                    self.assertEqual(render.png_size(png), (width, 844))

    def test_her_style_never_shows_rocha_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            sp = Path(tmp) / "style.json"
            sp.write_text(json.dumps({"palette": {"hero": "#0B3D3A"}}))
            page = build.build(EXAMPLE, Path(tmp) / "site", style_path=sp)
            r = render.measure(page, 1280, 900)
        self.assertEqual(r["stamp"], "")
        r2 = render.measure(self.page, 1280, 900)
        self.assertEqual(r2["stamp"], "LORE")


if __name__ == "__main__":
    unittest.main()
