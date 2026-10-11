"""AI commentary for matches: generate with an LLM, or export/import for offline writing.

Online (an LLM API writes the lines):
  python3 tools/commentate.py generate g2                       # default provider (mock: no key needed)
  python3 tools/commentate.py generate g2 --provider claude --lang zh en
  python3 tools/commentate.py generate --all --provider deepseek --roles caster
  python3 tools/commentate.py prompt g2 --role analyst --lang en --window 2   # show one prompt

Offline (any LLM or person reads a brief of the whole match and writes a JSON file):
  python3 tools/commentate.py export g2 --lang zh               # -> commentary/briefs/g2.zh.md
  python3 tools/commentate.py import path/to/g2.zh.json         # validate and publish it

Checks (CI runs this):
  python3 tools/commentate.py check

Lines are written to site/data/commentary/<key>/<lang>.json; then the catalog is rebuilt so
the viewer shows them. See commentary/README.md.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

from commentary_lib import (COMMENTARY_DIR, OUTPUT_DIR, CommentaryError, MockWriter, RefusalError, accept_lines,
                            build_prompt, check_config, load_config, load_role, load_skill, make_provider,
                            min_gap_any, parse_lines, role_priorities, today, window_facts, write_track)
from ctf_data import MATCH_DIR, ROOT, load_content, read_json, write_pretty

BRIEF_DIR = COMMENTARY_DIR / "briefs"
SKILL_DIR = ROOT / ".claude" / "skills" / "ctf-commentary"


def match_meta(key: str) -> dict:
    meta = next((m for m in load_content() if m["key"] == key), None)
    if not meta:
        raise CommentaryError(f"unknown match '{key}' (see: python3 tools/add_match.py list)")
    return meta


def windows(total: int, size: int) -> list[tuple[int, int]]:
    return [(t0, min(total, t0 + size)) for t0 in range(0, total, size)]


def rebuild_catalog() -> None:
    sys.stdout.flush()
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_catalog.py")], check=True)


# ---------------------------------------------------------------- generate

def run_track(key: str, replay: dict, meta: dict, role: dict, lang: str, config: dict, provider, provider_name: str,
              t_from: int, t_to: int) -> list[dict]:
    """One role in one language across the match, window by window (sequential for continuity)."""
    total = replay["frames"][-1]["turn"]
    mock = MockWriter(lang) if provider is None else None
    lines: list[dict] = []
    retries = config.get("generation", {}).get("max_retries", 2)
    keep = config.get("generation", {}).get("previous_lines", 3)
    for t0, t1 in windows(total, role["window"]):
        if t1 <= t_from or t0 >= t_to:
            continue
        facts = window_facts(replay, meta, t0, t1, lang, role["context"], config.get("generation", {}).get("focus"))
        last = lines[-1]["turn"] if lines else None
        if mock:
            raw = mock.lines(role, facts, replay, lang)
        else:
            system, user = build_prompt(role, lang, config, facts, [ln["text"] for ln in lines[-keep:]])
            raw = []
            for attempt in range(retries + 1):
                try:
                    raw = parse_lines(provider.complete(system, user))
                    break
                except RefusalError:
                    print(f"  {key} {role['id']}/{lang} turns {t0 + 1}-{t1}: declined, skipped")
                    break
                except (CommentaryError, ValueError) as exc:
                    if attempt == retries:
                        print(f"  {key} {role['id']}/{lang} turns {t0 + 1}-{t1}: {exc} (skipped)")
        lines += accept_lines(raw, role, lang, config, t0, t1, last)
    return lines


def cmd_generate(args) -> None:
    config = load_config()
    keys = [m["key"] for m in load_content()] if args.all else args.keys
    if not keys:
        sys.exit("error: name match keys or pass --all")
    langs = args.lang or list(config["languages"])
    role_ids = args.roles or config["roles"]
    for lang in langs:
        if lang not in config["languages"]:
            sys.exit(f"error: language '{lang}' is not in commentary/config.json")
    roles = [load_role(r) for r in role_ids]
    provider_name = args.provider or config["default_provider"]
    try:
        provider = make_provider(provider_name, config, args.model)
    except CommentaryError as exc:
        sys.exit(f"error: {exc}")
    model = None if provider is None else getattr(provider, "model", None)
    jobs = args.jobs or config.get("generation", {}).get("jobs", 4)

    for key in keys:
        meta = match_meta(key)
        replay = read_json(MATCH_DIR / f"{key}.json")
        total = replay["frames"][-1]["turn"]
        t_from, t_to = args.from_turn or 0, args.to_turn or total
        print(f"{key}: {', '.join(r['id'] for r in roles)} in {', '.join(langs)} via {provider_name}"
              + (f" ({model})" if model else ""))
        tracks = [(role, lang) for lang in langs for role in roles]
        results: dict[tuple[str, str], list[dict]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
            futures = {pool.submit(run_track, key, replay, meta, role, lang, config, provider, provider_name, t_from, t_to):
                       (role["id"], lang) for role, lang in tracks}
            for fut in concurrent.futures.as_completed(futures):
                results[futures[fut]] = fut.result()
        source = {"provider": provider_name, "model": model, "generated": today()}
        for lang in langs:
            new = [ln for role in roles for ln in results[(role["id"], lang)]]
            path = write_track(key, lang, config, new, roles, source)
            print(f"  {lang}: {len(new)} lines -> {path.relative_to(ROOT)}")
    rebuild_catalog()


def cmd_prompt(args) -> None:
    config = load_config()
    meta = match_meta(args.key)
    replay = read_json(MATCH_DIR / f"{args.key}.json")
    role = load_role(args.role)
    t0, t1 = windows(replay["frames"][-1]["turn"], role["window"])[args.window]
    facts = window_facts(replay, meta, t0, t1, args.lang, role["context"], config.get("generation", {}).get("focus"))
    system, user = build_prompt(role, args.lang, config, facts, [])
    print("=== system ===\n" + system + "\n\n=== user ===\n" + user)


# ---------------------------------------------------------------- offline export / import

def cmd_export(args) -> None:
    """Write one self-contained Markdown brief: instructions, glossary, role skills, the whole match."""
    config = load_config()
    lang = args.lang
    if lang not in config["languages"]:
        sys.exit(f"error: language '{lang}' is not in commentary/config.json")
    meta = match_meta(args.key)
    replay = read_json(MATCH_DIR / f"{args.key}.json")
    total = replay["frames"][-1]["turn"]
    language = config["languages"][lang]
    role_ids = args.roles or config["roles"]
    focus = config.get("generation", {}).get("focus")
    big = bool(focus) and replay["header"]["teams"] > focus.get("when_teams_over", 4)

    parts = [
        f"# Commentary brief: {meta['title'].get(lang) or meta['title']['en']}",
        "",
        "You are writing esports commentary for a recorded AI capture-the-flag match, as a team of "
        f"{len(role_ids)} broadcast roles. Read this whole brief first, then write the commentary file "
        "described under *Output*. Use only facts in this brief.",
        "",
        f"- Match key: `{args.key}` · language: `{lang}` ({language['name']}) · turns: {total}",
        f"- Language rules: {language['style']}",
        "",
        "## Output",
        "",
        f"Write one JSON file named `{args.key}.{lang}.json`:",
        "",
        "```json",
        json.dumps({"match": args.key, "language": lang,
                    "source": {"provider": "offline", "model": "<the model or person who wrote this>"},
                    "lines": [{"turn": 12, "role": role_ids[0], "text": "..."}]}, ensure_ascii=False, indent=2),
        "```",
        "",
        "- `turn` is the turn the line refers to (0 to %d). Lines can be in any order." % total,
        "- Optional `\"key\": true` marks a lead change, a tie at the top or the winning capture. Key lines always keep their slot.",
        f"- `role` is one of: {', '.join(f'`{r}`' for r in role_ids)}.",
        f"- Every `text` is written in {language['english_name']} and at most {language['max_chars']} characters.",
        "- Follow each role's pacing below: how many lines per window and the minimum gap between its lines.",
        f"- Across all booth roles (every role except bullet-comment roles marked display=danmaku), at most one line every {min_gap_any(config)} turns. Where two roles would speak within "
        f"{min_gap_any(config)} turns, keep the higher-priority one: "
        + " > ".join(f"`{r}`" for r in sorted(role_ids, key=lambda r: -role_priorities(config).get(r, 0))) + ". "
        "Lines closer than that are dropped on import.",
        *([f"- This match has {replay['header']['teams']} teams. Follow only the contenders, the top "
           f"{focus.get('top', 3)} teams by score, listed in each window under `focus` (they change as the match "
           "goes). Don't narrate every team; mention others only when they directly affect a contender, "
           "for example by stopping a leader's flag carrier. Each window only lists events that involve contenders."]
          if big else []),
        "",
        f"Publish it with: `python3 tools/commentate.py import {args.key}.{lang}.json`",
        "",
    ]

    glossary = SKILL_DIR / "references" / "game-and-data.md"
    if glossary.exists():
        parts += ["## How the game and the data work", "", glossary.read_text(encoding="utf-8").split("\n", 1)[1].strip(), ""]

    parts += ["## Roles", ""]
    for rid in role_ids:
        role = load_role(rid)
        skill, _ = load_skill(rid, lang, config)
        parts += [
            f"### `{rid}`: {role['name'].get(lang) or role['name']['en']}",
            "",
            f"Pacing: at most {role['max_lines']} lines per {role['window']} turns, at least {role['min_gap']} turns apart. "
            f"Length: {language['length'][role['length']]}.",
            "",
            skill.split("\n", 1)[1].strip() if skill.startswith("#") else skill,
            "",
        ]

    final = replay["frames"][-1]["score"]
    standings = sorted(range(len(final)), key=lambda t: -final[t])
    parts += [
        "## Match",
        "",
        f"{meta['desc'].get(lang) or meta['desc']['en']}",
        "",
        "Final standings (for your awareness only; don't reveal the result before it happens): "
        + ", ".join(f"{replay['names'][t]} {final[t]}" for t in standings),
        "",
        "## Turn by turn",
        "",
        "Each block covers 10 turns. Every 50 turns there is also a positions and intent snapshot for the analyst.",
        "",
    ]
    for t0, t1 in windows(total, 10):
        context = ["events", "standings", "window_stats"]
        if t1 % 50 == 0 or t1 == total:
            context += ["positions", "orders"]
        facts = window_facts(replay, meta, t0, t1, lang, context, focus)
        facts.pop("match")
        parts += [f"### Turns {t0 + 1}–{t1}", "", "```json", json.dumps(facts, ensure_ascii=False, separators=(",", ":")), "```", ""]

    out = Path(args.output) if args.output else BRIEF_DIR / f"{args.key}.{lang}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB). Give it to any LLM, then import its JSON reply.")


def validate_offline(data: dict, config: dict, total: int, lang: str) -> list[str]:
    errs = []
    if not isinstance(data.get("lines"), list) or not data["lines"]:
        return ["'lines' must be a non-empty list"]
    max_chars = config["languages"][lang]["max_chars"]
    for i, ln in enumerate(data["lines"]):
        where = f"lines[{i}]"
        if not isinstance(ln, dict):
            errs.append(f"{where} must be an object")
            continue
        if ln.get("role") not in config["roles"]:
            errs.append(f"{where}.role '{ln.get('role')}' is not one of {config['roles']}")
        if not isinstance(ln.get("turn"), int) or not 0 <= ln["turn"] <= total:
            errs.append(f"{where}.turn must be an integer from 0 to {total}")
        text = ln.get("text")
        if not isinstance(text, str) or not text.strip():
            errs.append(f"{where}.text is empty")
        elif len(text) > max_chars:
            errs.append(f"{where}.text is {len(text)} characters (max {max_chars})")
        if len(errs) > 20:
            errs.append("... stopping after 20 problems")
            break
    return errs


def cmd_import(args) -> None:
    config = load_config()
    path = Path(args.file)
    try:
        data = read_json(path)
    except (OSError, ValueError) as exc:
        sys.exit(f"error: can't read {path}: {exc}")
    key = args.key or data.get("match")
    lang = args.lang or data.get("language")
    if not key or not lang:
        sys.exit("error: the file needs \"match\" and \"language\" (or pass --key and --lang)")
    if lang not in config["languages"]:
        sys.exit(f"error: language '{lang}' is not in commentary/config.json (add it there first)")
    replay = read_json(MATCH_DIR / f"{match_meta(key)['key']}.json")
    errs = validate_offline(data, config, replay["frames"][-1]["turn"], lang)
    if errs:
        sys.exit(f"error: {path} has problems:\n  - " + "\n  - ".join(errs))
    lines = [{"turn": ln["turn"], "role": ln["role"], "text": ln["text"].strip(), **({"key": True} if ln.get("key") is True else {})}
             for ln in data["lines"]]
    roles = [load_role(r) for r in config["roles"] if any(ln["role"] == r for ln in lines)]
    src = data.get("source") or {}
    source = {"provider": src.get("provider") or "offline", "model": src.get("model"), "generated": today()}
    out = write_track(key, lang, config, lines, roles, source)
    kept = len(read_json(out)["lines"])
    dropped = len(lines) - kept
    print(f"imported {kept} lines ({', '.join(r['id'] for r in roles)}) -> {out.relative_to(ROOT)}"
          + (f"; dropped {dropped} closer than {min_gap_any(config)} turns to another line" if dropped > 0 else ""))
    rebuild_catalog()


# ---------------------------------------------------------------- check

def cmd_check(_args) -> None:
    config_errs = check_config()
    errs = list(config_errs)
    if not config_errs:
        config = load_config()
        keys = {m["key"] for m in load_content()}
        for match_dir in sorted(OUTPUT_DIR.glob("*")) if OUTPUT_DIR.exists() else []:
            if match_dir.name not in keys:
                errs.append(f"{match_dir.relative_to(ROOT)}: no match called '{match_dir.name}'")
                continue
            total = read_json(MATCH_DIR / f"{match_dir.name}.json")["frames"][-1]["turn"]
            for f in sorted(match_dir.glob("*.json")):
                lang = f.stem
                rel = f.relative_to(ROOT)
                if lang not in config["languages"]:
                    errs.append(f"{rel}: language '{lang}' is not in commentary/config.json")
                    continue
                data = read_json(f)
                errs += [f"{rel}: {e}" for e in validate_offline(data, config, total, lang)]
                danmaku = {r["id"] for r in data.get("roles", []) if r.get("display") == "danmaku"}
                turns = sorted(ln["turn"] for ln in data.get("lines", []) if ln.get("role") not in danmaku)
                gap = min_gap_any(config)
                close = [(a, b) for a, b in zip(turns, turns[1:]) if b - a < gap]
                if close:
                    errs.append(f"{rel}: lines at turns {close[0][0]} and {close[0][1]} are closer than {gap} turns "
                                f"(re-run generate/import to re-space)")
                ids = {r["id"] for r in data.get("roles", [])}
                missing = {ln.get("role") for ln in data.get("lines", [])} - ids
                if missing:
                    errs.append(f"{rel}: roles used in lines but not listed in 'roles': {sorted(missing)}")
    if errs:
        print("\n".join(f"error: {e}" for e in errs), file=sys.stderr)
        sys.exit(1)
    n = sum(1 for _ in OUTPUT_DIR.glob("*/*.json")) if OUTPUT_DIR.exists() else 0
    print(f"ok: commentary config valid, {n} commentary files checked")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("generate", help="write commentary with an LLM provider (or the offline mock)")
    p.add_argument("keys", nargs="*")
    p.add_argument("--all", action="store_true", help="every match")
    p.add_argument("--provider", help="provider name from commentary/config.json")
    p.add_argument("--model", help="override the provider's model")
    p.add_argument("--lang", nargs="+", help="languages (default: all in config)")
    p.add_argument("--roles", nargs="+", help="roles (default: all in config)")
    p.add_argument("--from-turn", type=int, help="only windows after this turn")
    p.add_argument("--to-turn", type=int, help="only windows up to this turn")
    p.add_argument("--jobs", type=int, help="parallel role/language tracks")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("prompt", help="print the prompt one window would send")
    p.add_argument("key")
    p.add_argument("--role", required=True)
    p.add_argument("--lang", default="en")
    p.add_argument("--window", type=int, default=0, help="window index (0 = first)")
    p.set_defaults(func=cmd_prompt)

    p = sub.add_parser("export", help="write an offline brief of the whole match for any LLM")
    p.add_argument("key")
    p.add_argument("--lang", default="zh")
    p.add_argument("--roles", nargs="+")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("import", help="validate and publish an offline commentary JSON file")
    p.add_argument("file")
    p.add_argument("--key")
    p.add_argument("--lang")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("check", help="validate config, roles, skills and commentary files")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args()
    try:
        args.func(args)
    except CommentaryError as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
