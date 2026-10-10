# Working on this repo (people and AI agents)

A static, bilingual (zh/en) replay viewer for AI capture-the-flag matches. Plain ES modules, no build step and no npm dependencies. Data tools use the Python standard library only. Read `README.md` for what the site does and `docs/data-format.md` for the data contracts.

## Verify before you hand off

```bash
python3 tools/build_catalog.py --check   # metadata + replays valid
python3 tools/build_catalog.py           # regenerate catalog after any content/ or replay change
node tools/check.mjs                     # i18n keys, imports, icons, links, catalog
python3 tools/serve.py                   # look at it: http://localhost:8000 (no caching)
```

CI (`.github/workflows/pages.yml`) runs the same checks on every pull request and blocks the deploy if they fail, or if `site/data/catalog.json` is stale.

## Where things live (lanes)

Each lane can be worked on in parallel. Stay inside your lane; if you must cross into another, keep the change minimal and say so in the PR.

| Lane | Paths | Talks to the rest through |
| --- | --- | --- |
| Match content | `content/matches/*.json`, `site/data/matches/*.json` | `tools/add_match.py`, then `build_catalog.py` |
| Data tools | `tools/*.py`, `tools/templates/` | the formats in `docs/data-format.md` |
| Board rendering | `site/assets/js/board/` | `BoardRenderer.render(view)`, `drawTerrain`, sprite functions |
| Viewer panels | `site/assets/js/viewer/ui/*.js` | the store (`viewer/store.js`) |
| Viewer core | `site/assets/js/viewer/{main,store,derive,playback,keyboard,url-state}.js` | store keys documented in `store.js` |
| Lobby | `site/assets/js/lobby/`, `site/index.html`, `assets/css/lobby.css` | `core/data.js` (catalog) |
| Text & translation | `site/assets/js/locales/zh-CN.js`, `en.js` | `t(key)` in `core/i18n.js` |
| Design system | `site/assets/css/tokens.css`, `base.css`, `components.css` | CSS custom properties |

## Rules that keep parallel work safe

1. **One match = its own files.** Never put match data in a shared file by hand. `site/data/catalog.json` is generated; only `build_catalog.py` writes it. On merge conflicts there, just re-run the script.
2. **Modules don't call each other's internals.** Viewer modules read and write the store (`store.set`, `store.subscribe(keys, fn)`). If you need new shared state, add the key to the comment at the top of `viewer/store.js` first.
3. **`derive.js` stays pure.** No DOM or store, just replay in and numbers out.
4. **Every visible string goes through `t()`** with a key in *both* locale files. Use `{name}` placeholders and `_one` / `_other` for plurals. Team names go through `teamName()`. Match text comes from `content/` via `pick()`.
5. **Colors come from tokens.** Gold (`--flag`) means "flag or score" only. Team colors and shapes come from `core/teams.js` and are only used for teams. Don't hard-code new colors in components.
6. **Escape anything that came from data** (team names, notes, ids) with `escapeHtml` before putting it in `innerHTML`.
7. **Facts in match text must match the replay.** Check with `python3 tools/build_catalog.py --report`.
8. **Keep paths relative.** The site is served from `/ctf-replay-viewer/` on GitHub Pages, so never use root-absolute URLs (`/assets/...`).

## Conventions

- JS: ES modules, 2-space indent, single quotes, small named exports, a short header comment saying what the module owns.
- Python: standard library only, `from __future__ import annotations`, shared logic in `tools/ctf_data.py`.
- Commits: imperative summary line; explain *why* in the body.
- Files are 644. This repo sits in OneDrive, which flips executable bits, so run `git config core.fileMode false` locally.
