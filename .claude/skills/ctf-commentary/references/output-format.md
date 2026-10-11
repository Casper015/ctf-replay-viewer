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

`python3 tools/commentate.py import g2.zh.json` checks:
- `match` is a known match key and `language` is configured in `commentary/config.json`.
- Each `role` is listed in `config.json` → `roles`.
- Each `turn` is an integer from 0 to the match's last turn.
- Each `text` is non-empty and within the language's `max_chars`.

Import replaces the lines of the roles present in your file and keeps other roles' lines, so you can deliver one role at a time.

## Pacing targets (from role.json)

| Role | Window | Max lines per window | Min gap | Length |
| --- | --- | --- | --- | --- |
| caster | 10 turns | 3 | 2 turns | short |
| color | 25 turns | 2 | 8 turns | medium |
| analyst | 50 turns | 2 | 20 turns | long |

For a 400-turn match that's roughly 60–120 caster lines, 16–32 color lines and 8–16 analyst lines. Fewer is fine when the match is quiet. Import doesn't enforce pacing, but viewers notice when it's off.

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
