"""Re-simulate curated matches with the arena engine and write one replay file per match.

This step needs the private ctf-stress-pack (engine.py, run_stress.py, schedule.jsonl and
the compiled bots). Everything downstream (catalog, site) only needs the replay files this
script writes, so most changes never require running it.

Usage
  python3 tools/build_replays.py --engine /path/to/ctf-stress-pack            # all curated matches
  python3 tools/build_replays.py --engine /path/to/ctf-stress-pack g2 g3      # only some keys
  CTF_ENGINE_DIR=/path/to/ctf-stress-pack python3 tools/build_replays.py

Matches come from content/matches/<key>.json (the "id" field is the schedule id).
Then run tools/build_catalog.py to refresh the lobby catalog. To add a match that was
simulated elsewhere, use tools/add_match.py instead.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ctf_data import MATCH_DIR, ROOT, load_content, write_compact


def load_engine(engine_dir: Path):
    sys.path.insert(0, str(engine_dir))
    sys.path.insert(0, str(engine_dir / "arena"))
    import engine  # noqa: E402  (provided by ctf-stress-pack)
    import run_stress  # noqa: E402

    return engine, run_stress


def team_stats(frames: list[dict], seats: list[str]) -> list[dict]:
    """Final per-team stats. Kept in the replay for tools that don't want to replay frames."""
    acc = {t: {"name": n, "kills": 0, "assists": 0, "carrier_kills": 0, "deaths": 0, "pickups": 0, "captures": 0}
           for t, n in enumerate(seats)}
    for frame in frames:
        for e in frame["events"]:
            kind = e["type"]
            if kind == "capture":
                acc[e["team"]]["captures"] += 1
            elif kind == "pickup":
                acc[e["unit"] // 3]["pickups"] += 1
            elif kind == "death":
                acc[e["unit"] // 3]["deaths"] += 1
                by = e.get("by") or []
                carrier = e.get("flag") is not None
                if by:
                    killer = by[0] // 3
                    acc[killer]["kills"] += 1
                    if carrier:
                        acc[killer]["carrier_kills"] += 1
                    for a in by[1:]:
                        acc[a // 3]["assists"] += 1
    rows = []
    for team, s in acc.items():
        rows.append({
            "team": team,
            "name": s["name"],
            "score": s["captures"],
            "kills": s["kills"],
            "assists": s["assists"],
            "carrier_kills": s["carrier_kills"],
            "deaths": s["deaths"],
            "pickups": s["pickups"],
            "captures": s["captures"],
            "kda": round((s["kills"] + s["assists"] * 0.5) / max(1, s["deaths"]), 2),
            "capture_rate": round(s["captures"] / s["pickups"] * 100, 1) if s["pickups"] else 0.0,
        })
    rows.sort(key=lambda r: (r["score"], r["kda"]), reverse=True)
    return rows


def simulate(engine, run_stress, commands, schedule: dict, game_id: str) -> dict:
    s = schedule[game_id]
    size, map_seed, flag_seed, seats = s["size"], s["map_seed"], s["flag_seed"], s["seats"]

    class FrozenGame(engine.Game):
        def __init__(self, n, seed):
            super().__init__(n, seed, flag_seed=flag_seed)

    game = FrozenGame(size, map_seed)
    bots = [run_stress.StressBot(commands[n], n, "record") for n in seats]
    frames = [game.frame()]
    try:
        while not game.done:
            starts = [b.send(game.encode(i)) for i, b in enumerate(bots)]
            orders = {}
            for i, (bot, start) in enumerate(zip(bots, starts)):
                line = bot.receive(start)
                if line is None:
                    orders[i] = {}
                    continue
                try:
                    orders[i] = game.decode(i, line)
                    bot.strikes = 0
                except ValueError:
                    orders[i] = {}
            game.step(orders)
            frames.append(game.frame(orders=orders))
    finally:
        for bot in bots:
            bot.close()

    result = game.result()
    result.update(seed=map_seed, flag_seed=flag_seed, names=list(seats), bots=[b.report() for b in bots])
    return {
        "header": game.header(),
        "names": list(seats),
        "result": result,
        "enhanced_stats": team_stats(frames, list(seats)),
        "frames": frames,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("keys", nargs="*", help="match keys to rebuild (default: all curated)")
    parser.add_argument("--engine", default=os.environ.get("CTF_ENGINE_DIR"),
                        help="path to ctf-stress-pack (or set CTF_ENGINE_DIR)")
    args = parser.parse_args()
    if not args.engine:
        sys.exit("pass --engine /path/to/ctf-stress-pack or set CTF_ENGINE_DIR")

    engine_dir = Path(args.engine).expanduser().resolve()
    engine, run_stress = load_engine(engine_dir)
    commands = run_stress.compile_all(run_stress.detect_compiler())
    with open(engine_dir / "schedule.jsonl", encoding="utf-8") as fh:
        schedule = {row["id"]: row for row in (json.loads(line) for line in fh)}

    curated = load_content()
    wanted = set(args.keys) or {m["key"] for m in curated}
    unknown = wanted - {m["key"] for m in curated}
    if unknown:
        sys.exit(f"unknown keys (create content/matches/<key>.json first): {', '.join(sorted(unknown))}")

    MATCH_DIR.mkdir(parents=True, exist_ok=True)
    for meta in curated:
        if meta["key"] not in wanted:
            continue
        print(f"simulating {meta['key']} ({meta['id']})...")
        replay = simulate(engine, run_stress, commands, schedule, meta["id"])
        out = MATCH_DIR / f"{meta['key']}.json"
        write_compact(out, replay)
        print(f"  {len(replay['frames'])} frames -> {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")

    print("done; now run: python3 tools/build_catalog.py")


if __name__ == "__main__":
    main()
