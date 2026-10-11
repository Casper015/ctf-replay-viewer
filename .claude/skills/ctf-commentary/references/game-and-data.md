# The game and the data

## Contents
- The game in one minute
- Rules (numbers)
- Reading a window (brief format)
- Stats and what they mean
- Replay fields (raw JSON)
- Glossary (English / 中文)

## The game in one minute

Several teams (2 to 15) share a square grid map with walls (`#`). Each team has **3 units** and a 3×3 **base**. A few **flags** sit on **flag spots**. Flags are **shared**: there are usually fewer flags than teams, and any team can take any flag. A unit picks up a flag, carries it back to **its own base**, and that is a **capture**, worth one point. The team with the most captures after 400 turns wins; ties are possible.

Units move one cell per turn (up, down, left, right, or wait) and can attack an enemy within about 2 cells. Three hits take a unit down. A downed unit drops any flag it carried and comes back at its base 10 turns later. A dropped flag stays where it fell, and anyone can pick it up, until its return timer runs out; then it goes back to a flag spot. After a capture, the flag disappears for a short cooldown, then respawns on a spot.

So matches are about **running flags home**, **stopping enemy carriers**, and **controlling the middle** where the flag spots usually are. Every team is an AI program (a "bot"); names like "GPT-6.1 Sol" or "Player5" are the competitors, and "基准" (Baseline) is a reference bot.

## Rules (numbers)

From `header.rules` in every replay; the values below are the usual ones.

| Rule | Value | Meaning |
| --- | --- | --- |
| `turns` | 400 | Match length |
| `hp` | 100 | Health of a unit; health goes 100 → 66 → 32 → 0 |
| `damage` | 34 | Health lost per hit, so 3 hits take a unit down |
| `attack_range` | 2 | How far an attack reaches |
| `respawn` | 10 | Turns a downed unit is out before reappearing at base |
| `flag_return` | 15 | Turns a dropped flag waits before returning to a spot |
| `flag_cooldown` | 8 | Turns a captured flag is gone before it respawns |

## Reading a window (brief format)

The brief has one JSON block per 10 turns:

```json
{
  "window": {"from_turn": 191, "to_turn": 200, "phase": "halftime"},
  "events": {
    "captures": [{"turn": 196, "team": "Player5", "team_score": 16, "scoreline": "16:12", "takes_lead": false, "ties_lead": false}],
    "carrier_stops": [{"turn": 193, "victim": "Opus 5.5", "by": "Player5"}],
    "pickups": [{"turn": 192, "team": "Opus 5.5"}],
    "big_fights": [{"turn": 194, "units_down": 3}]
  },
  "standings": [{"team": "Player5", "score": 16}, {"team": "Opus 5.5", "score": 12}],
  "window_stats": [{"team": "Player5", "captures": 2, "pickups": 3, "kills": 2, "deaths": 1, "carrier_stops": 1}],
  "positions": [{"team": "Player5", "alive": 3, "carrying_flags": 1, "avg_cells_from_home": 7.3, "avg_cells_from_center": 4.0}],
  "bot_intent_notes": [{"team": "Player5", "notes": ["escort", "intercept"]}]
}
```

- `phase` is one of `opening`, `midgame`, `halftime` (the window containing the middle turn), `late` or `final`.
- `scoreline` is the top two scores right after that capture, highest first. It's not necessarily the scoring team's score versus one opponent.
- `takes_lead`: this capture made the team the sole leader when it wasn't before. `ties_lead`: the team is now level at the top.
- `standings` are the scores at the end of the window (top 8 shown).
- `window_stats` count only this window. Teams with no activity are left out.
- `positions` and `bot_intent_notes` appear every 50 turns. Distances are grid steps (Manhattan distance). `avg_cells_from_home` is large when a team is pushing forward. Intent notes are free-text labels the bots themselves attach to orders ("camp", "escort", "fetch", "intercept", "def"); they show what the bot was trying to do.

## Stats and what they mean

- **Capture:** a flag brought home, +1 point.
- **Pickup:** a unit grabbed a flag. Pickups that never become captures were lost to stops or timers.
- **Conversion:** captures ÷ pickups. High conversion means clean runs home; low means the team keeps getting stopped.
- **Kill:** credited to the first attacker listed on a `death`. Others who hit the unit get an **assist**.
- **Death:** a unit of this team went down.
- **Carrier stop:** a kill on a unit that was carrying a flag. It's the most important defensive play, because the flag drops where the carrier fell.
- **KDA:** (kills + 0.5 × assists) ÷ max(1, deaths). Above 1 means the team wins its fights on balance.
- **Lead change:** the sole leader became a different team. Ties don't count as a change.

## Replay fields (raw JSON)

If you are reading `site/data/matches/<key>.json` directly instead of a brief:

- `names[t]`: team t's name. Unit `id` k belongs to team `floor(k / 3)`; its slot within the team (shown as #1–#3) is `k % 3 + 1`.
- `frames[n]`: the state after turn n (frame 0 is the start).
  - `score[t]` is cumulative captures.
  - `units[k]`: `pos` [x, y] is null while down; `hp` is health; `flag` is the id of a carried flag or null.
  - `flags[i]`: `status` is `home` (on a spot), `carried` (`holder` = unit id), `dropped` (on the ground; `return_at` = turn it returns) or `cooldown` (gone after a capture; `return_at` = turn it respawns).
  - `events`: what happened this turn. `capture` {unit, team, flag}, `pickup` {unit, flag}, `drop`, `attack` {unit, target}, `death` {unit, pos, by[], flag}, `respawn` {unit}, `return` {flag}.
  - `orders[t].units[]`: the bot's order for each unit. `move` (N/S/E/W/WAIT), `act` (attack/pickup/drop/wait), optional `target` and `note`.

Full format: `docs/data-format.md`.

## Glossary (English / 中文)

| English | 中文 |
| --- | --- |
| capture | 交旗得分 |
| pickup | 拾旗 |
| flag carrier | 持旗者 |
| carrier stop | 截杀持旗 |
| base | 基地 |
| flag spot | 旗点 |
| dropped flag | 掉落的旗帜 |
| respawn | 重生 |
| conversion | 转化率 |
| lead change | 领先易主 |
| comeback | 逆转 |
| halftime | 半场 |
| caster | 解说 |
| color commentator | 嘉宾点评 |
| analyst | 战术分析师 |
