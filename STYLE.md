# style.json

One file holds your look. Every Rocha Coded tool reads the same file, so you make it once.

## Where it goes
The tool looks in this order and uses the first one it finds:
1. `style.json` in the folder you are working in (your Cowork folder, or wherever you run Claude Code)
2. `~/.rocha-coded/style.json`, to use one look across every project
3. `examples/style.rocha-coded.json`, the bundled example (Rocha's look)

Start from `style.example.json`: copy it to `style.json` and fill it in. Or ask Claude to make one with you.

Your words do not live here. Your name, tagline, folders, notes and links live in `desktop.config.json`.
`style.json` is colour, type and motif.

## The keys
| Key | What to put there | Used by this tool |
|---|---|---|
| `name`, `owner`, `handle`, `site` | your brand, your name, your handle, your site | no (your desktop takes its name from `desktop.config.json`) |
| `palette.hero` | your ground colour, the deep one, as a hex code like `#50163C` | the page behind the desktop |
| `palette.plum` | a deep shade | the y2k title bar stripes, the cyberpunk desk |
| `palette.wine` | a second deep colour | title bars, analog menubar, the cyberdeck bezel, polaroid photos |
| `palette.accent` | your one bright accent | buttons, washi tape, pixel folders, the blinking cursor |
| `palette.paper` | a light paper colour | windows, the analog desk |
| `palette.paper_pink` | a second paper colour | the y2k wallpaper, sticky notes, the clock face |
| `palette.ink` | your text colour | text, outlines, the counter box |
| `palette.marker` | the colour of a pen mark | the date stamp, the wallpaper stamp, crossed-out trash |
| `palette.gold` | a highlight colour | window buttons, cyberdeck screws, pixel hearts, focus rings |
| `palette.cool` | one cool accent | no |
| `fonts.masthead` | a big display font from Google Fonts | your name in the welcome window, the stamp |
| `fonts.label` | a font for labels and buttons | icon labels, buttons, the menubar |
| `fonts.body` | a reading font | the words inside windows |
| `fonts.scrawl` | a handwriting or marker font | sticky notes, analog captions |
| `fonts.script` | a signature script font | no |
| `fonts.mono` | a typewriter font | the clock, the counter, the cyberpunk screens |
| `fonts.pixel` (optional) | a pixel font from Google Fonts | y2k and cyberpunk window titles (Silkscreen if empty) |
| `motif` | `analog`, `cyberpunk` or `y2k-blog` (older names like `guest-check` or `retro-tv` still work) | yes, when `desktop.config.json` has no motif of its own |
| `lines.stamp` | one short word of yours | a faint stamp on your wallpaper |
| `lines.*` (the rest) | more of your own lines | kept for other tools |
| `references`, `notes` | 3 to 5 images or links, and your look in a sentence | Claude reads these when it makes your style with you |

## Which motif wins
`--motif` on the command line, then `motif` in `desktop.config.json`, then `motif` in your own `style.json`,
then `y2k-blog`. The bundled example says `analog` for other tools, and this tool ignores that and opens as the 2003 desktop.

## Good to know
- Colours must be hex codes (`#RRGGBB`). Anything else is skipped and the bundled colour is used for that slot.
- Fonts are Google Fonts names, letters, numbers and spaces only. Offline, the page uses a similar font already on the computer.
- Any colour or font you leave empty borrows the bundled example's, so the desktop always looks finished.
- Your words never borrow. Leave `lines.stamp` empty and there is no stamp. Rocha's LORE stamp appears only when the whole bundled example is in use.
