"""Add new matches to the site from replay JSON files.

  python3 tools/add_match.py add replays/new_game.json                 # one match, copy auto-drafted
  python3 tools/add_match.py add replays/*.json                        # many at once (key = file name)
  python3 tools/add_match.py add game.json --key g4_upset --id sz04-m01
  python3 tools/add_match.py add game.json --meta my_meta.json         # use copy you wrote from the template
  python3 tools/add_match.py draft game.json -o my_meta.json           # draft metadata only, edit, then add --meta
  python3 tools/add_match.py list
  python3 tools/add_match.py remove g4_upset

What `add` does for each replay
  1. validates it (see docs/data-format.md) and stops with readable errors if anything is off
  2. copies it, minified, to site/data/matches/<key>.json
  3. writes content/matches/<key>.json with bilingual tag/title/desc; any field you didn't
     write (missing, empty or "auto") is drafted from the replay in the house style
  4. rebuilds site/data/catalog.json, so the match shows up in the lobby immediately

Replays can be a bare replay object or the old {"replay": {...}} wrapper.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

from ctf_data import (CONTENT_DIR, LANGS, MATCH_DIR, ROOT, TEXT_FIELDS, draft_copy, load_content,
                      match_facts, next_order, read_json, unwrap_replay, validate_meta, validate_replay,
                      write_compact, write_pretty)


def key_from_path(path: Path) -> str:
    key = re.sub(r"[^a-z0-9_-]+", "_", path.stem.lower()).strip("_-")
    return key[:48] or "match"


def expand(paths: list[str]) -> list[Path]:
    out = []
    for p in map(Path, paths):
        if p.is_dir():
            out += sorted(p.glob("*.json"))
        else:
            out.append(p)
    return out


def load_replay(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"error: {path} not found")
    try:
        replay = unwrap_replay(read_json(path))
    except ValueError as exc:
        sys.exit(f"error: {path} is not valid JSON ({exc})")
    errs = validate_replay(replay)
    if errs:
        sys.exit(f"error: {path} is not a usable replay:\n  - " + "\n  - ".join(errs))
    return replay


# Placeholder values in tools/templates/match.json that mean "not filled in".
TEMPLATE_KEY, TEMPLATE_ORDER = "g4_example", 999


def pick_order(key: str, explicit, from_meta):
    """--order wins, then the metadata file, then the match's current slot, then the end."""
    if explicit is not None:
        return explicit
    if isinstance(from_meta, (int, float)) and from_meta != TEMPLATE_ORDER:
        return from_meta
    current = next((m.get("order") for m in load_content() if m["key"] == key), None)
    return current if current is not None else next_order()


def is_auto(value) -> bool:
    return not str(value or "").strip() or str(value).strip().lower() == "auto"


def build_meta(replay: dict, key: str, match_id: str | None, given: dict, order, featured: bool) -> tuple[dict, list[str]]:
    """Merge user-written fields with drafts. Returns (meta, list of drafted field names)."""
    drafted_copy = draft_copy(match_facts(replay))
    drafted: list[str] = []
    meta = {
        "key": key,
        "id": match_id or given.get("id") or key,
        "order": pick_order(key, order, given.get("order")),
        "featured": featured or bool(given.get("featured")),
    }
    for field in TEXT_FIELDS:
        meta[field] = {}
        for lang in LANGS:
            value = (given.get(field) or {}).get(lang)
            if is_auto(value):
                meta[field][lang] = drafted_copy[field][lang]
                drafted.append(f"{field}.{lang}")
            else:
                meta[field][lang] = value.strip()
    return meta, drafted


def rebuild_catalog() -> None:
    sys.stdout.flush()
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_catalog.py")], check=True)


def unfeature_others(except_key: str) -> None:
    for m in load_content():
        if m.get("featured") and m["key"] != except_key:
            data = read_json(m["_path"])
            data["featured"] = False
            write_pretty(m["_path"], data)
            print(f"  {m['key']} is no longer featured")


# ---------------------------------------------------------------- commands

def cmd_add(args) -> None:
    paths = expand(args.replays)
    if not paths:
        sys.exit("error: no replay files given")
    if len(paths) > 1 and (args.key or args.id or args.meta):
        sys.exit("error: --key/--id/--meta only work with a single replay")

    given = {k: v for k, v in read_json(Path(args.meta)).items() if not k.startswith("$")} if args.meta else {}
    existing = {m["key"] for m in load_content()}
    added = []
    for path in paths:
        replay = load_replay(path)
        key = args.key or (given.get("key") if given.get("key") not in (None, TEMPLATE_KEY) else None) or key_from_path(path)
        if key in existing and not args.force:
            sys.exit(f"error: '{key}' already exists. Use --key to pick another name, or --force to replace it.")
        meta, drafted = build_meta(replay, key, args.id, given, args.order, args.featured)
        errs = validate_meta(meta)
        if errs:
            sys.exit("error:\n  - " + "\n  - ".join(errs))

        f = match_facts(replay)
        print(f"\n{key}: {f['teams']} teams, {f['size']}x{f['size']} map, {f['turns']} turns, {f['total']} captures")
        print("  top: " + ", ".join(f"{r['name']} {r['score']}" for r in f["standings"][:4]))
        for lang in LANGS:
            print(f"  [{lang}] {meta['tag'][lang]} | {meta['title'][lang]}")
            print(f"       {meta['desc'][lang]}")
        if args.dry_run:
            continue

        out_meta = {}
        if drafted:
            out_meta["$note"] = (f"Auto-drafted {', '.join(drafted)} from replay facts on "
                                 f"{dt.date.today().isoformat()}. Edit freely, then run tools/build_catalog.py.")
        out_meta.update(meta)
        MATCH_DIR.mkdir(parents=True, exist_ok=True)
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        write_compact(MATCH_DIR / f"{key}.json", replay)
        write_pretty(CONTENT_DIR / f"{key}.json", out_meta)
        if meta["featured"]:
            unfeature_others(key)
        existing.add(key)
        added.append(key)
        print(f"  wrote content/matches/{key}.json and site/data/matches/{key}.json")

    if args.dry_run:
        print("\n(dry run: nothing written)")
        return
    rebuild_catalog()
    print("\nadded: " + ", ".join(added))
    print("preview: python3 -m http.server -d site 8000  ->  http://localhost:8000/match.html?m=" + added[0])


def cmd_draft(args) -> None:
    path = Path(args.replay)
    replay = load_replay(path)
    key = args.key or key_from_path(path)
    meta, _ = build_meta(replay, key, args.id, {}, None, False)
    template = read_json(ROOT / "tools" / "templates" / "match.json")
    out = {"$help": template["$help"], **meta}
    if args.output:
        write_pretty(Path(args.output), out)
        print(f"wrote {args.output}. Edit the text, then: python3 tools/add_match.py add {path} --meta {args.output}")
    else:
        import json
        print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_list(_args) -> None:
    metas = load_content()
    print(f"{'order':>5}  {'key':<16} {'teams':>5}  title (zh / en)")
    for m in metas:
        replay_path = MATCH_DIR / f"{m['key']}.json"
        teams = read_json(replay_path)["header"]["teams"] if replay_path.exists() else "?"
        star = "*" if m.get("featured") else " "
        print(f"{m.get('order', ''):>5} {star}{m['key']:<16} {teams:>5}  {m['title']['zh']}")
        print(f"{'':>30}{m['title']['en']}")
    print(f"\n{len(metas)} matches (* = featured)")


def cmd_remove(args) -> None:
    content = CONTENT_DIR / f"{args.key}.json"
    replay = MATCH_DIR / f"{args.key}.json"
    if not content.exists() and not replay.exists():
        sys.exit(f"error: no match '{args.key}'")
    if not args.yes:
        answer = input(f"Delete {content.relative_to(ROOT)} and {replay.relative_to(ROOT)}? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            sys.exit("cancelled")
    for p in (content, replay):
        if p.exists():
            p.unlink()
            print(f"deleted {p.relative_to(ROOT)}")
    rebuild_catalog()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="import replay file(s) and publish them in the lobby")
    p.add_argument("replays", nargs="+", help="replay .json files or folders of them")
    p.add_argument("--key", help="match key (default: replay file name)")
    p.add_argument("--id", help="schedule/engine match id (default: the key)")
    p.add_argument("--meta", help="metadata file filled in from tools/templates/match.json")
    p.add_argument("--order", type=int, help="lobby position (default: after the last match)")
    p.add_argument("--featured", action="store_true", help="show in the lobby hero (unfeatures the current one)")
    p.add_argument("--force", action="store_true", help="replace a match with the same key")
    p.add_argument("--dry-run", action="store_true", help="show what would be added, write nothing")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("draft", help="print drafted bilingual metadata for a replay, write nothing else")
    p.add_argument("replay")
    p.add_argument("--key")
    p.add_argument("--id")
    p.add_argument("-o", "--output", help="write to this file instead of stdout")
    p.set_defaults(func=cmd_draft)

    p = sub.add_parser("list", help="list matches in lobby order")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("remove", help="delete a match's metadata and replay")
    p.add_argument("key")
    p.add_argument("-y", "--yes", action="store_true", help="don't ask for confirmation")
    p.set_defaults(func=cmd_remove)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
