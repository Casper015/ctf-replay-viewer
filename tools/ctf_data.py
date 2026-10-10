"""Shared helpers for the data tools: paths, replay validation, match facts and copy drafts.

Every tool imports from here so facts (standings, lead changes, comebacks...) are computed
one way only. Standard library only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "matches"      # hand-edited metadata, one file per match
SITE = ROOT / "site"
MATCH_DIR = SITE / "data" / "matches"           # one replay per match
CATALOG = SITE / "data" / "catalog.json"        # generated
TEMPLATE = ROOT / "tools" / "templates" / "match.json"

LANGS = ("zh", "en")
TEXT_FIELDS = ("tag", "title", "desc")
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")

# Engine team names that need an English display form (mirrors site/assets/js/core/teams.js).
EN_NAMES = {"基准": "Baseline"}


# ---------------------------------------------------------------- JSON io

def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_pretty(path: Path, obj) -> None:
    """Human-edited files: indented, UTF-8, trailing newline."""
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_compact(path: Path, obj) -> None:
    """Machine files served to the browser: no whitespace."""
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


# ---------------------------------------------------------------- replays

def unwrap_replay(obj):
    """Accept a bare replay or a {"replay": {...}} wrapper (the old combined format)."""
    if isinstance(obj, dict) and "frames" not in obj and isinstance(obj.get("replay"), dict):
        return obj["replay"]
    return obj


def validate_replay(replay) -> list[str]:
    """Return a list of human-readable problems (empty list = valid). See docs/data-format.md."""
    errs: list[str] = []
    if not isinstance(replay, dict):
        return ["replay must be a JSON object"]
    for field in ("header", "names", "frames"):
        if field not in replay:
            errs.append(f"missing top-level field '{field}'")
    if errs:
        return errs

    header, names, frames = replay["header"], replay["names"], replay["frames"]
    for field in ("teams", "size", "map", "bases", "flag_spots", "rules"):
        if field not in header:
            errs.append(f"header is missing '{field}'")
    if errs:
        return errs

    teams, size = header["teams"], header["size"]
    if not isinstance(teams, int) or teams < 1:
        errs.append("header.teams must be a positive integer")
    if len(header["map"]) != size or any(len(row) != size for row in header["map"]):
        errs.append(f"header.map must be {size} rows of {size} characters")
    if len(header["bases"]) != teams:
        errs.append(f"header.bases has {len(header['bases'])} entries, expected {teams} (one per team)")
    if "hp" not in header["rules"]:
        errs.append("header.rules.hp is required (used for health rings)")
    if len(names) != teams:
        errs.append(f"names has {len(names)} entries, expected {teams}")
    if not isinstance(frames, list) or len(frames) < 2:
        errs.append("frames must be a list with at least 2 frames")
        return errs

    unit_count = len(frames[0].get("units", []))
    for idx, frame in enumerate(frames):
        where = f"frames[{idx}]"
        for field in ("turn", "score", "units", "flags", "events"):
            if field not in frame:
                errs.append(f"{where} is missing '{field}'")
        if errs:
            break
        if len(frame["score"]) != teams:
            errs.append(f"{where}.score has {len(frame['score'])} entries, expected {teams}")
        if len(frame["units"]) != unit_count:
            errs.append(f"{where} has {len(frame['units'])} units, expected {unit_count}")
        for k, unit in enumerate(frame["units"]):
            if unit.get("id") != k:
                errs.append(f"{where}.units[{k}].id should be {k} (units must be sorted by id)")
                break
        if len(errs) > 20:
            errs.append("... stopping after 20 problems")
            break
    if unit_count != teams * 3:
        errs.append(f"expected 3 units per team ({teams * 3}), found {unit_count}")
    return errs


# ---------------------------------------------------------------- facts

def team_of(unit_id: int) -> int:
    return unit_id // 3


def standings(replay: dict) -> list[dict]:
    """Final per-team totals sorted by score, then KDA (same order the viewer uses)."""
    names = replay["names"]
    rows = [{"team": t, "name": names[t], "score": 0, "kills": 0, "assists": 0, "deaths": 0,
             "pickups": 0, "carrier_kills": 0} for t in range(replay["header"]["teams"])]
    for frame in replay["frames"]:
        for e in frame["events"]:
            kind = e["type"]
            if kind == "capture":
                rows[e["team"]]["score"] += 1
            elif kind == "pickup":
                rows[team_of(e["unit"])]["pickups"] += 1
            elif kind == "death":
                rows[team_of(e["unit"])]["deaths"] += 1
                by = e.get("by") or []
                if by:
                    rows[team_of(by[0])]["kills"] += 1
                    if e.get("flag") is not None:
                        rows[team_of(by[0])]["carrier_kills"] += 1
                    for a in by[1:]:
                        rows[team_of(a)]["assists"] += 1
    for r in rows:
        r["kda"] = round((r["kills"] + r["assists"] * 0.5) / max(1, r["deaths"]), 2)
    rows.sort(key=lambda r: (r["score"], r["kda"]), reverse=True)
    return rows


def capture_log(replay: dict) -> list[list[int]]:
    return [[f["turn"], e["team"]] for f in replay["frames"] for e in f["events"] if e["type"] == "capture"]


def lead_changes(replay: dict) -> int:
    """Times the sole leader changed hands (ties don't count as a change)."""
    prev, changes = None, 0
    for frame in replay["frames"]:
        score = frame["score"]
        top = max(score)
        leaders = [t for t, s in enumerate(score) if s == top]
        if top > 0 and len(leaders) == 1:
            if prev is not None and leaders[0] != prev:
                changes += 1
            prev = leaders[0]
    return changes


def match_facts(replay: dict) -> dict:
    """Everything the catalog and the copy drafts need, computed from the frames."""
    frames = replay["frames"]
    names = replay["names"]
    teams = replay["header"]["teams"]
    final = frames[-1]["score"]
    table = standings(replay)
    top = max(final)
    winners = [t for t in range(teams) if final[t] == top]

    mid_frame = frames[len(frames) // 2]
    mid_score = mid_frame["score"]
    mid_top = max(mid_score)

    facts = {
        "teams": teams,
        "size": replay["header"]["size"],
        "units": len(frames[0]["units"]),
        "turns": frames[-1]["turn"],
        "total": sum(final),
        "standings": table,
        "lead_changes": lead_changes(replay),
        "winners": winners,
        "tie": len(winners) > 1,
        "mid_turn": mid_frame["turn"],
        "mid_top": mid_top,
        "mid_leaders": [t for t in range(teams) if mid_score[t] == mid_top] if mid_top > 0 else [],
        "names": names,
    }

    if not facts["tie"] and teams > 1:
        w = winners[0]
        runner = table[1]["team"]
        deficit, deficit_turn, last_not_leading = 0, None, -1
        for idx, frame in enumerate(frames):
            s = frame["score"]
            best_other = max(s[t] for t in range(teams) if t != w)
            if best_other - s[w] > deficit:
                deficit, deficit_turn = best_other - s[w], frame["turn"]
            if s[w] <= best_other:
                last_not_leading = idx
        go_ahead = frames[last_not_leading + 1]["turn"] if last_not_leading + 1 < len(frames) else None
        facts.update(winner=w, runner=runner, margin=final[w] - final[runner],
                     max_deficit=deficit, max_deficit_turn=deficit_turn, go_ahead_turn=go_ahead)
    return facts


# ---------------------------------------------------------------- copy drafts

def display_name(raw: str, lang: str) -> str:
    return EN_NAMES.get(raw, raw) if lang == "en" else raw


def _join(items: list[str], lang: str) -> str:
    if lang == "zh":
        return "、".join(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def draft_copy(f: dict) -> dict:
    """Draft tag/title/desc in both languages from match facts.

    The phrasing mirrors the hand-written entries so new matches read the same way in the
    lobby. Drafts are a starting point: edit content/matches/<key>.json to add the story.
    """
    n = {lang: [display_name(x, lang) for x in f["names"]] for lang in LANGS}
    score = {t: row["score"] for row in f["standings"] for t in [row["team"]]}
    top3 = f["standings"][:3]
    total, teams, turns = f["total"], f["teams"], f["turns"]

    if f["tie"]:
        tied = f["winners"]
        s = score[tied[0]]
        if len(tied) == 2:
            a, b = tied
            tag = {"zh": f"{s}:{s} 平局", "en": f"{s}–{s} draw"}
            title = {"zh": f"{n['zh'][a]} 与 {n['zh'][b]} {s}:{s} 握手言和",
                     "en": f"{n['en'][a]} and {n['en'][b]} share the win at {s}–{s}"}
        else:
            tag = {"zh": f"{len(tied)} 队并列第一", "en": f"{len(tied)}-way tie"}
            title = {"zh": f"{_join([n['zh'][t] for t in tied], 'zh')} {s} 分并列第一",
                     "en": f"{_join([n['en'][t] for t in tied], 'en')} finish level on {s}"}
    elif teams == 1:
        tag = {"zh": "单队演练", "en": "Solo run"}
        title = {"zh": f"{n['zh'][0]} 拿下 {total} 分", "en": f"{n['en'][0]} scores {total}"}
    else:
        w, r = f["winner"], f["runner"]
        sw, sr = score[w], score[r]
        W = {lang: n[lang][w] for lang in LANGS}
        R = {lang: n[lang][r] for lang in LANGS}
        go = f["go_ahead_turn"]
        if f["max_deficit"] >= 4:
            d, dt = f["max_deficit"], f["max_deficit_turn"]
            tag = {"zh": f"落后 {d} 分逆转", "en": f"Comeback from {d} down"}
            title = {"zh": f"第 {dt} 回合落后 {d} 分，{W['zh']} {sw}:{sr} 逆转 {R['zh']}",
                     "en": f"Down {d} on turn {dt}, {W['en']} comes back to beat {R['en']} {sw}–{sr}"}
        elif go is not None and go >= turns - 10:
            tag = {"zh": "末段绝杀", "en": "Late winner"}
            title = {"zh": f"{W['zh']} 第 {go} 回合交旗，{sw}:{sr} 绝杀 {R['zh']}",
                     "en": f"{W['en']} beats {R['en']} {sw}–{sr} with a capture on turn {go}"}
        elif f["margin"] == 1:
            tag = {"zh": f"{sw}:{sr} 一分险胜", "en": f"{sw}–{sr} thriller"}
            title = {"zh": f"{W['zh']} {sw}:{sr} 险胜 {R['zh']}",
                     "en": f"{W['en']} edges {R['en']} {sw}–{sr}"}
        elif teams == 2:
            tag = {"zh": f"{total} 球单挑", "en": f"{total}-capture duel"}
            title = {"zh": f"{W['zh']} {sw}:{sr} 击败 {R['zh']}",
                     "en": f"{W['en']} beats {R['en']} {sw}–{sr}"}
        else:
            tag = {"zh": f"{teams} 队混战", "en": f"{teams}-team battle"}
            title = {"zh": f"{W['zh']} 以 {sw} 分夺冠，{R['zh']} {sr} 分次之",
                     "en": f"{W['en']} wins with {sw}, ahead of {R['en']} on {sr}"}

    # Description: halftime picture, when the winner took over, final top three, total.
    mid, mid_top, mid_leaders = f["mid_turn"], f["mid_top"], f["mid_leaders"]
    if not mid_leaders:
        half = {"zh": f"第 {mid} 回合双方仍未开张。", "en": f"Nobody had scored by turn {mid}. "}
    elif len(mid_leaders) == 1:
        L = mid_leaders[0]
        half = {"zh": f"第 {mid} 回合 {n['zh'][L]} 以 {mid_top} 分领先。",
                "en": f"{n['en'][L]} led with {mid_top} at turn {mid}. "}
    else:
        half = {"zh": f"第 {mid} 回合 {_join([n['zh'][t] for t in mid_leaders], 'zh')} 以 {mid_top} 分并列领先。",
                "en": f"{_join([n['en'][t] for t in mid_leaders], 'en')} shared the lead on {mid_top} at turn {mid}. "}

    took = {"zh": "", "en": ""}
    # Skip when the title already names the winning turn (the "late winner" variant)
    late = (f.get("go_ahead_turn") is not None and f["go_ahead_turn"] >= turns - 10
            and f.get("max_deficit", 0) < 4)
    if not f["tie"] and teams > 1 and f.get("go_ahead_turn") is not None and not late:
        w = f["winner"]
        took = {"zh": f"{n['zh'][w]} 第 {f['go_ahead_turn']} 回合取得领先后再未落后。",
                "en": f"{n['en'][w]} went ahead for good on turn {f['go_ahead_turn']}. "}

    final = {
        "zh": "终局 " + "、".join(f"{n['zh'][row['team']]} {row['score']}" for row in top3) + f"，全场共 {total} 次交旗。",
        "en": "Final: " + ", ".join(f"{n['en'][row['team']]} {row['score']}" for row in top3) + f". {total} captures in all.",
    }
    desc = {lang: (half[lang] + took[lang] + final[lang]).strip() for lang in LANGS}
    return {"tag": tag, "title": title, "desc": desc}


# ---------------------------------------------------------------- content (metadata)

def validate_meta(meta: dict, source: str = "") -> list[str]:
    where = source or meta.get("key", "?")
    errs = []
    key = meta.get("key")
    if not isinstance(key, str) or not KEY_RE.match(key):
        errs.append(f"{where}: 'key' must be lowercase letters, digits, '_' or '-' (got {key!r})")
    if not meta.get("id"):
        errs.append(f"{where}: 'id' is required (use the schedule id, or repeat the key)")
    if not isinstance(meta.get("order"), (int, float)):
        errs.append(f"{where}: 'order' must be a number (lobby sorts by it, low first)")
    for field in TEXT_FIELDS:
        value = meta.get(field)
        if not isinstance(value, dict):
            errs.append(f"{where}: '{field}' must be an object with zh and en")
            continue
        for lang in LANGS:
            if not str(value.get(lang, "")).strip():
                errs.append(f"{where}: '{field}.{lang}' is empty")
    return errs


def load_content() -> list[dict]:
    """All match metadata files, sorted by `order` then key. Keys starting with '$' are notes."""
    metas = []
    for path in sorted(CONTENT_DIR.glob("*.json")):
        meta = {k: v for k, v in read_json(path).items() if not k.startswith("$")}
        meta["_path"] = path
        metas.append(meta)
    metas.sort(key=lambda m: (m.get("order", 1e9), m.get("key", "")))
    return metas


def next_order() -> int:
    orders = [m.get("order", 0) for m in load_content() if isinstance(m.get("order"), (int, float))]
    return int(max(orders, default=0)) + 10
