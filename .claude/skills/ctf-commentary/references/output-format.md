# Commentary output format

## What you hand back (offline / import)

One JSON file per match per language, e.g. `g2.zh.json`:

```json
{
  "match": "g2",
  "language": "zh",
  "source": { "provider": "offline", "model": "claude-opus-5-5" },
  "lines": [
    { "turn": 10, "role": "caster",  "text": "Player5 率先交旗，1:0！" },
    { "turn": 25, "role": "color",   "text": "开局 Player5 明显更敢压上……" },
    { "turn": 50, "role": "analyst", "text": "前 50 回合 Player5 拾旗 6 次转化 5 次……" }
  ]
}
```

Optional per line: `"key": true` for a lead change, a tie at the top, or the winning capture. Key lines always keep their slot when lines collide, so use it for the handful of moments that define the match.

`python3 tools/commentate.py import g2.zh.json` checks:
- `match` is a known match key and `language` is configured in `commentary/config.json`.
- Each `role` is listed in `config.json` → `roles`.
- Each `turn` is an integer from 0 to the match's last turn.
- Each `text` is non-empty and within the language's `max_chars`.

Import replaces the lines of the roles present in your file and keeps other roles' lines, so you can deliver one role at a time.

## Pacing targets (from role.json)

| Role | Window | Max lines per window | Min gap | Length | Priority |
| --- | --- | --- | --- | --- | --- |
| caster | 10 turns | 2 | 5 turns | short | 2 |
| color | 25 turns | 2 | 8 turns | medium | 1 |
| analyst | 50 turns | 2 | 20 turns | long | 3 |

**Shared limit:** across all roles, at most one line every 5 turns (`generation.min_turns_between_lines`). On import, lines closer than that are dropped, keeping `key` lines first, then the higher-priority role (analyst 3 > caster 2 > color 1), then the earlier line. So space them yourself and keep the moments you care about. A 400-turn match has room for at most 80 lines; 40–60 well-chosen lines usually reads best.

**Focus:** in matches with more than 4 teams (`generation.focus`), write about the contenders only (the top 3 by score, listed under `focus` in each window).

## What the site stores (for reference)

`site/data/commentary/<key>/<lang>.json`, written by `generate`/`import` (don't hand-edit):

```json
{
  "version": 1, "match": "g2", "language": "zh",
  "roles": [{ "id": "caster", "name": "解说", "icon": "mic", "caption": true }],
  "sources": { "caster": { "provider": "offline", "model": "...", "generated": "2026-10-10" } },
  "lines": [{ "turn": 10, "role": "caster", "text": "..." }]
}
```

The viewer shows a line once playback reaches its turn, and can show caption-enabled roles as subtitles on the board.
