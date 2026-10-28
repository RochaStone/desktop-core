# Testing

Everything below was run on 28 Oct 2026, on macOS with Python 3.12.8 and Google Chrome installed.

## 1. Tests
```sh
python3 -m unittest discover -s tests -v
```
Result: **21 tests, all OK.** They cover:
- **Config validation:** the fictional example passes; a missing name, a `javascript:` link, a link without `https://`, too many notes, an unknown motif, a counter that is not a number, `currently` as a list and a folder with no name are each reported in plain words; old motif names (`guest-check`, `retro-tv`, `blog`) map to the three families.
- **Style and the inheritance rule:** the fallback order (./style.json, then ~/.rocha-coded/style.json, then the bundled example); a user style borrows only missing palette and font entries and never the example's lines, owner, handle, name, references or notes; with a user style the page carries no stamp, with the bundled example it carries LORE; bad colours and font names are dropped before they reach the page; both bundled style files share the same keys; motif order is `--motif`, then the config, then her own style.json, then y2k-blog (the bundled example's `analog` is ignored on purpose).
- **Build output:** `site/` holds exactly one file, `index.html`, with the config, style and motif written in; a tagline of `</script><script>alert(1)</script>` cannot break out of its data block; a bad config refuses to build and the CLI prints "A few things to fix"; the root `index.html` shows the fictional example in y2k-blog; the page has no `text-shadow`, no `innerHTML`, no external script, and uses localStorage only inside try/catch.
- **Headless render, all three motifs, at 1280 and 390 wide:** each page reports its motif as ready, shows the name and its signature marker (y2k-blog: `you are visitor no.`; cyberpunk: the `juniper-lark:~$` prompt; analog: the washi tape and the `OCT 2026` date stamp), opens two windows, and its scroll width is no wider than the viewport. PNG screenshots of every motif at 1280 and 390 come back at exactly those widths. A user style with no lines renders no LORE stamp.

### How the 390px check works, honestly
Headless Chrome on macOS will not make a window narrower than 500px, so a 390px screenshot alone would crop a 500px
layout and hide overflow. The overflow test loads the site inside an iframe exactly 390px wide and reads the page's own
`scrollWidth` from inside it. The PNG width check is a second, weaker signal. This check caught two real bugs on the way:
the body grid grew to fit the scrolling tagline (444px wide), and windows kept their desktop width on a phone. Both are fixed.

## 2. By eye
`python3 scripts/make-readme-images.py` rendered the three desktops at 1280x800, the triptych and the three phone views.
Each was opened and checked: windows, folders, sticky notes, clock, trash and taskbar visible, nothing cut off, no glow.

## 3. Build, end to end
```sh
python3 build.py desktop.config.json --out site/
```
Output: `READY. Your desktop is in site/ ...` and the page opened in Chrome.

## 4. Security gate
```sh
./scripts/security-check.sh
```
Result: 9 passed, 0 failed, **SAFE TO PUBLISH**.

## Not tested
- **Dragging with a real mouse or finger, and keyboard moves,** were reviewed in code, not driven by an automated test.
  Saving positions uses localStorage inside try/catch, so a private window still works, it only forgets positions.
- **Deploying** to GitHub Pages or Vercel. The steps in SKILL.md follow each service's current screens and were not run on a real account for this build.
- **Claude Cowork** upload of the zip.
- Windows, Safari and Firefox. Screen readers were not tested; icons are real buttons, windows are labelled dialogs, and Escape returns focus to the icon that opened them.
