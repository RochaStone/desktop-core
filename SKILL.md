---
name: desktop-core
description: Build her link-in-bio as a 2003 desktop. Folders are her offers, sticky notes are testimonials, a clock widget books a call, the trash holds the things she let go, plus a guestbook, a "currently" window and a visitor counter, in analog, cyberpunk or y2k-blog. Interviews her one question at a time, writes desktop.config.json, builds one deployable folder, and walks her through putting it online on her own GitHub Pages or Vercel. Use when someone says "make my link in bio a desktop", "retro desktop link in bio", "2003 desktop website", "link in bio like Mac OS 9", "y2k link in bio", or "desktop core".
---

# Desktop Core

You are helping her turn her link-in-bio into a 2003 desktop that is entirely hers. You interview her, write her
`desktop.config.json`, build the site, show it to her, and help her put it online on HER OWN accounts.
You never invent testimonials, prices, results or links. Every word on the desktop is hers.

`SKILL_DIR` below means the folder this file lives in. Work in the user's working folder (in Cowork, the folder she
shared). Write her `desktop.config.json` and `site/` there, never inside `SKILL_DIR`.

## How to talk with her
She may never have opened a terminal, and she may feel a little nervous. Be warm, certain and kind. Never say
"simply" or "just". In every step:
- Ask one question at a time and wait for the answer.
- Reflect the answer back in one sentence ("Lovely: Juniper Lark, brand photography for ceramicists.").
- Say what you are about to do before you do it.
- End each step by telling her what happens next.
- If she needs to type anything herself, tell her exactly what to type, where, and what she will see when it worked.
- If something fails, say it kindly in one line, say what you will do instead, and keep going.

## 1. Show her the three desktops
Show her `SKILL_DIR/docs/img/triptych.png` and ask which feels like her:
analog (a paper desk with polaroids and tape), cyberpunk (a plum screen with pixel chrome) or y2k-blog
(the cream 2003 desktop, the default). Reflect her choice back. She can change it any time.

## 2. Interview her (one question at a time)
Ask these in order. After each answer, reflect it back in one sentence, then ask the next. If she skips one, leave it out.
1. The name on her desktop, exactly as she wants it to appear. (`name`)
2. One line about what she does, in her own words. (`tagline`)
3. Her offers. For each: its folder name, one or two sentences about it, the link to it, and the words for the
   button (for example "save a spot"). Up to ten. Ask "another one, or is that all?" after each. (`folders`)
4. Kind words from real clients, with the name or initials they agreed to show. Up to six. Never write these for her.
   If she has none yet, offer one sticky note of her own words instead. (`notes`)
5. The link where people book a call, and the words for that button (default "book a call"). (`clock`)
6. Three to five things she has let go of in her business. These go in the trash. (`trash`)
7. What she is reading, listening to and building right now. (`currently`)
8. Her other links: Instagram, newsletter, shop, podcast. Up to eight. (`links`)
9. Where her guestbook should go: a form, an email link (`mailto:you@example.com`), or a page. (`guestbookUrl`)
10. Optional: her mood today, in a few words, and the number her visitor counter starts at (default 777). (`mood`, `counter`)

Every link must start with `https://` (or `mailto:` for email). If she gives `instagram.com/name`, add `https://` for her
and tell her you did.

## 3. Write the config
Tell her you are writing her desktop file. Copy the shape of `SKILL_DIR/desktop.config.json` (a fictional example) into
`desktop.config.json` in her folder, with her answers only. Set `motif` to her choice from step 1. Show her the file.

## 4. Make it hers (style.json)
Colours and fonts come from one `style.json`. The same file styles every Rocha Coded tool. The tool looks for
`style.json` in the working folder, then `~/.rocha-coded/style.json`, then uses the bundled example
(`SKILL_DIR/examples/style.rocha-coded.json`, Rocha's own look).

If she has no `style.json`, offer once to make one. Never assume her taste is Rocha's.
1. Ask one at a time, reflecting each answer back: 3 to 5 references (screenshots, links, a Pinterest board), then her
   palette if she has one, then one short word she would stamp on her wallpaper (optional).
2. Look at every reference (open images, fetch links). Pick a palette as hex codes and fonts from Google Fonts that
   match them. The stamp comes from her own words, never from Rocha's lines.
3. Copy `SKILL_DIR/style.example.json` to `style.json` in her folder and fill it in. `SKILL_DIR/STYLE.md` explains each key.

If she says no thanks, use the bundled look and tell her in one line that it is Rocha's example, and she can make it hers any time.

## 5. Build it and show her
Tell her you are building her desktop into a folder called `site`. Then run:
```sh
python3 "$SKILL_DIR/build.py" desktop.config.json --out site/
```
You will see `READY. Your desktop is in site/`. If it lists things to fix, read each one to her in plain words,
fix the config with her, and run it again.

Open `site/index.html` for her if you can. If she has to open it herself: `open site/index.html` on a Mac, or
double-click `index.html` inside the `site` folder on Windows. She will see her desktop in her browser.
Tell her what to try: click a folder, drag a window by its title bar (it remembers where she left it), press Tab
to move between icons and Enter to open, Escape to close. On her phone it becomes one tidy column.

To try another look without changing her file, add `--motif analog`, `--motif cyberpunk` or `--motif y2k-blog`.

## 6. Put it online, on HER accounts
She owns the site. It goes on her own free account, never Rocha's and never yours. Ask which she prefers.
Explain each word the first time: "deploy" means putting the folder on the internet so anyone with the link can see it.
Never type her passwords. If a page asks her to log in, she logs in herself and tells you "ready".

### GitHub Pages (free, good if she already has GitHub)
GitHub is a website that stores files and can publish a folder as a site.
1. She signs in at github.com (or makes a free account). She will see her dashboard.
2. She clicks the + at the top right, then New repository. Name it, for example `my-desktop`. She ticks Public and
   clicks Create repository. She will see an empty repository page.
3. She clicks "uploading an existing file", drags in `index.html` from her `site` folder, and clicks Commit changes.
   She will see `index.html` listed.
4. She opens Settings, then Pages. Under Branch she picks `main` and `/ (root)` and clicks Save.
5. After a minute or two the Pages screen shows "Your site is live at https://<her-name>.github.io/my-desktop/".
   That is the link for her bio.
To update later: build again, then upload the new `index.html` the same way.

### Vercel (free, good for a custom domain later)
Vercel is a website that puts folders online in one drag.
1. She signs in at vercel.com (or makes a free Hobby account, it can use her GitHub). She will see her dashboard.
2. If she is happy with the terminal, run `npx vercel deploy site --prod` with her and let her answer its questions;
   the first time it opens a browser for her to log in. She will see a link ending in `.vercel.app`.
3. If she prefers no terminal: she pushes the `site` folder to a GitHub repository (steps 1 to 3 above), then in Vercel
   clicks Add New, then Project, picks that repository, and clicks Deploy. She will see "Congratulations" and her link.
To update later: build again and deploy again the same way.

Finish by giving her the link, and telling her the one line to change next time ("edit desktop.config.json, then build again").

## Rules
- Her words only. Never invent testimonials, clients, numbers or links. Testimonials need the client's permission.
- The visitor counter is a playful decoration: it starts at her number and counts visits from each browser. It is not analytics. Say so if she asks.
- Window positions are saved in the visitor's own browser only. Nothing is sent anywhere.
- No logins, passwords, purchases or sign-ups on her behalf. Her site goes on her accounts.
