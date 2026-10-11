---
name: ctf-commentary
description: Write esports-style commentary (caster, color commentator, analyst) for recorded AI capture-the-flag matches in this repo, in Chinese, English or any language listed in commentary/config.json. Use this whenever someone wants commentary, casting, play-by-play, 解说, 点评, 战术分析 or match analysis for a replay; when they hand you a commentary brief (commentary/briefs/*.md) or a replay JSON and ask what happened; when they want to add a commentary role or language; or when they ask how the CTF replay data, stats or game rules work.
---

# CTF match commentary

This repo replays matches where AI agents play capture the flag on a grid. Viewers can watch each match with a commentary booth of three roles. You write those lines, either through the repo's tools or "offline" by reading a whole-match brief and writing a JSON file.

Before writing anything, read `references/game-and-data.md`. The data is compact and some fields are easy to misread: flags are shared, not owned by teams; a `death` with a non-null `flag` is a carrier stop; `pos: null` means dead, not missing. Commentary that gets the game wrong is worse than none.

## Pick the workflow

**A. You have a brief** (`commentary/briefs/<key>.<lang>.md`, or text the user pasted from one). It already holds the rules, the role skills and every 10-turn window of the match. Read it end to end, then write the output file described in `references/output-format.md`. This is the offline path; it works without API keys.

**B. You are in the repo and want a brief.** Run:
```bash
python3 tools/commentate.py export <key> --lang zh      # or en, or any configured language
```
then follow A. Publish your file with `python3 tools/commentate.py import <file>.json`.

**C. The user wants an API model to do it.** Use `python3 tools/commentate.py generate <key> --provider <name>`. Providers are in `commentary/config.json`, and API keys come from environment variables named there. Use `--provider mock` for a free template-based dry run.

To check everything after any change, run `python3 tools/commentate.py check`.

## Writing the lines

Each role has a persona file at `commentary/roles/<role>/skill.<lang>.md` and pacing in `role.json`. The brief embeds them. In short:

- **caster:** what just happened. Captures first, then carrier stops, then dangerous pickups and big fights. Short, present tense, names every team. Silence beats filler.
- **color:** the story. Momentum, rivalries, comebacks, what the scoreline means. Opinion, then the fact behind it.
- **analyst:** why. Conversion (captures ÷ pickups), fights, positions relative to bases, the bots' own intent notes. Calm, cites numbers. Gives a verdict at halftime and at the end.

Things that make commentary good here:
- **Stay on the turn.** A line at turn 120 may only use what is known by turn 120. The brief shows the final result so you understand the arc, but foreshadowing the winner spoils the replay for viewers.
- **Every number comes from the data.** If you can't point to the window that shows it, cut it.
- **One line every 5 turns at most, for the whole booth.** That's the hard rule (`generation.min_turns_between_lines` in `commentary/config.json`; import drops anything closer). Mark the few defining moments (lead changes, ties at the top, the winning capture) with `"key": true` so they're never dropped; otherwise, when two roles want the same moment, the analyst wins, then the caster, then the color commentator. Within that budget, pick the moments that change the story; a 400-turn match gets at most 80 lines in total, usually far fewer.
- **In big matches, follow the contenders, not everyone.** With more than 4 teams (`generation.focus`), talk only about the top teams fighting for first. They're listed under `focus` in each window and they change as the match goes. Don't read out the whole table or narrate a mid-table team's capture; another team earns a mention only when it directly affects a contender, for example by stopping the leader's carrier. Viewers of a 15-team match want the title race, not a roll call.
- **Write natively.** Use the language's style rules from `commentary/config.json` (Chinese scores `31:29`, English `31–29`). Keep team and model names exactly as given. In English, the team `基准` is shown as "Baseline".
- **Make 400 turns interesting.** Note when a lead changes, when someone goes cold, when a deficit shrinks. Don't narrate every pickup.

## Adding a role or a language

- **New language:** add an entry under `languages` in `commentary/config.json` (name, style rules, length words, max_chars), add `name.<lang>` to each `role.json`, and ideally add `skill.<lang>.md` per role. Without one, the English skill is used with an instruction to write in the new language. Add `commentary/mock/<lang>.json` if you want mock output. The viewer's interface languages are separate (`site/assets/js/locales/`); commentary in a new language still shows up there.
- **New role:** create `commentary/roles/<id>/role.json` (copy an existing one) plus skill files, then add the id to `roles` in `config.json`. Icons must be one of those listed in `tools/commentary_lib.py` (`ICONS`).

See `references/output-format.md` for the file format and the validation rules `import` enforces.
