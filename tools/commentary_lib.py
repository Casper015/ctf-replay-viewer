"""AI commentary: config, match facts, prompts, LLM providers and the offline mock writer.

Used by tools/commentate.py. Layout of the inputs (see commentary/README.md):

  commentary/config.json                 providers, languages, enabled roles
  commentary/roles/<role>/role.json      what the role covers and how often it speaks
  commentary/roles/<role>/skill.<lang>.md   the role's persona/instructions in that language
  commentary/mock/<lang>.json            templates for the offline mock provider

Output: site/data/commentary/<match key>/<lang>.json (format in docs/data-format.md).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from ctf_data import ROOT, SITE, display_name, read_json, team_of, write_pretty

COMMENTARY_DIR = ROOT / "commentary"
ROLES_DIR = COMMENTARY_DIR / "roles"
MOCK_DIR = COMMENTARY_DIR / "mock"
OUTPUT_DIR = SITE / "data" / "commentary"

ROLE_FIELDS = ("id", "name", "icon", "window", "max_lines", "min_gap", "length", "context")
CONTEXT_KINDS = {"events", "standings", "window_stats", "positions", "orders"}
ICONS = {"mic", "chat", "chart", "activity", "swords", "flag", "trophy", "info"}  # must exist in icons.js


class CommentaryError(Exception):
    pass


class RefusalError(CommentaryError):
    pass


# ---------------------------------------------------------------- config

def strip_notes(obj):
    if isinstance(obj, dict):
        return {k: strip_notes(v) for k, v in obj.items() if not k.startswith("$")}
    return obj


def load_config() -> dict:
    return strip_notes(read_json(COMMENTARY_DIR / "config.json"))


def load_role(role_id: str) -> dict:
    return strip_notes(read_json(ROLES_DIR / role_id / "role.json"))


def load_skill(role_id: str, lang: str, config: dict) -> tuple[str, str]:
    """Skill text for a language. Falls back to English, then any language, so a new language
    works before its skills are translated. Returns (text, language the text is written in)."""
    order = [lang, "en", *config["languages"].keys()]
    for code in order:
        path = ROLES_DIR / role_id / f"skill.{code}.md"
        if path.exists():
            return path.read_text(encoding="utf-8").strip(), code
    raise CommentaryError(f"role '{role_id}' has no skill.<lang>.md files")


def check_config() -> list[str]:
    """Validate config, roles, skills and mock templates. Returns problems (empty = ok)."""
    errs: list[str] = []
    try:
        config = load_config()
    except (OSError, ValueError) as exc:
        return [f"commentary/config.json: {exc}"]

    langs = config.get("languages", {})
    if not langs:
        errs.append("config.json: 'languages' is empty")
    for code, lang in langs.items():
        for field in ("name", "english_name", "style", "length", "max_chars"):
            if field not in lang:
                errs.append(f"config.json: languages.{code} is missing '{field}'")

    providers = config.get("providers", {})
    if config.get("default_provider") not in providers:
        errs.append("config.json: default_provider must name one of 'providers'")
    for name, p in providers.items():
        if p.get("type") not in ("mock", "anthropic", "openai_compatible"):
            errs.append(f"config.json: providers.{name}.type must be mock, anthropic or openai_compatible")
        if p.get("type") in ("anthropic", "openai_compatible") and not p.get("model"):
            errs.append(f"config.json: providers.{name} needs a 'model'")
        if p.get("type") == "openai_compatible" and not p.get("base_url"):
            errs.append(f"config.json: providers.{name} needs a 'base_url'")

    if not isinstance(config.get("generation", {}).get("min_turns_between_lines", DEFAULT_MIN_GAP), int):
        errs.append("config.json: generation.min_turns_between_lines must be an integer")
    for role_id in config.get("roles", []):
        rdir = ROLES_DIR / role_id
        if not (rdir / "role.json").exists():
            errs.append(f"roles/{role_id}/role.json is missing")
            continue
        role = load_role(role_id)
        for field in ROLE_FIELDS:
            if field not in role:
                errs.append(f"roles/{role_id}/role.json is missing '{field}'")
        if role.get("id") != role_id:
            errs.append(f"roles/{role_id}/role.json: id should be '{role_id}'")
        if role.get("icon") not in ICONS:
            errs.append(f"roles/{role_id}/role.json: icon must be one of {sorted(ICONS)}")
        for code in langs:
            if code not in role.get("name", {}):
                errs.append(f"roles/{role_id}/role.json: name.{code} is missing")
        for kind in role.get("context", []):
            if kind not in CONTEXT_KINDS:
                errs.append(f"roles/{role_id}/role.json: unknown context '{kind}'")
        if role.get("length") and any(role["length"] not in lang.get("length", {}) for lang in langs.values()):
            errs.append(f"roles/{role_id}/role.json: length '{role.get('length')}' must exist in every language")
        if not list(rdir.glob("skill.*.md")):
            errs.append(f"roles/{role_id}/ has no skill.<lang>.md")
    return errs


# ---------------------------------------------------------------- facts

def _frame_index(frames: list[dict], turn: int) -> int:
    for k, f in enumerate(frames):
        if f["turn"] >= turn:
            return k
    return len(frames) - 1


def _scoreline(scores: list[int], lang: str) -> str:
    top = sorted(scores, reverse=True)[:2]
    return (":" if lang == "zh" else "–").join(str(s) for s in top)


def _leaders(score: list[int]) -> list[int]:
    best = max(score)
    return [t for t, s in enumerate(score) if s == best]


def contenders(score: list[int], top: int) -> list[int]:
    """Teams fighting for first: the top `top` by score, plus anyone tied with the last of them."""
    order = sorted(range(len(score)), key=lambda t: -score[t])
    cutoff = score[order[min(top, len(order)) - 1]]
    return [t for t in order if score[t] >= cutoff and score[t] > 0] or order[:top]


def window_facts(replay: dict, meta: dict, t0: int, t1: int, lang: str, context: list[str],
                 focus: dict | None = None) -> dict:
    """Facts for turns t0 < turn <= t1, in the language's display names.

    focus = {"when_teams_over": 4, "top": 3}: in bigger matches only the contenders' events and
    stats are included (plus events where another team directly hits a contender), so
    commentary follows the title race instead of narrating every team."""
    frames = replay["frames"]
    header = replay["header"]
    teams = header["teams"]
    names = [display_name(n, lang) for n in replay["names"]]
    total = frames[-1]["turn"]
    k0, k1 = _frame_index(frames, t0), _frame_index(frames, t1)

    phase = "opening" if t1 <= total * 0.2 else "late" if t0 >= total * 0.85 else "midgame"
    if t0 < total / 2 <= t1:
        phase = "halftime"
    if t1 >= total:
        phase = "final"

    end = frames[k1]
    focus_teams = None
    if focus and teams > focus.get("when_teams_over", 4):
        # Contenders as of the window's end; scores before it are already known to viewers
        focus_teams = set(contenders(end["score"], focus.get("top", 3)))
    keep = (lambda *ts: True) if focus_teams is None else (lambda *ts: any(t in focus_teams for t in ts if t is not None))

    facts: dict = {
        # No title: titles state the final result, which would spoil live commentary
        "match": {"teams": teams, "map": f"{header['size']}x{header['size']}", "total_turns": total, "team_names": names},
        "window": {"from_turn": t0 + 1, "to_turn": t1, "phase": phase},
    }
    if focus_teams is not None:
        facts["focus"] = {"contenders": [names[t] for t in sorted(focus_teams, key=lambda t: -end["score"][t])],
                          "note": "Talk about these teams. Mention another team only when it directly affects one of them."}

    if "events" in context:
        captures, stops, pickups, brawls = [], [], [], []
        for k in range(k0 + 1, k1 + 1):
            f, prev = frames[k], frames[k - 1]
            deaths = 0
            for e in f["events"]:
                kind = e["type"]
                if kind == "capture":
                    if not keep(e["team"]):
                        continue
                    before, after = _leaders(prev["score"]), _leaders(f["score"])
                    captures.append({
                        "turn": f["turn"], "team": names[e["team"]], "team_score": f["score"][e["team"]],
                        "scoreline": _scoreline(f["score"], lang),
                        "takes_lead": after == [e["team"]] and before != [e["team"]],
                        "ties_lead": e["team"] in after and len(after) > 1,
                    })
                elif kind == "death":
                    deaths += 1
                    by = e.get("by") or []
                    if e.get("flag") is not None and keep(team_of(e["unit"])):
                        stops.append({"turn": f["turn"], "victim": names[team_of(e["unit"])],
                                      "by": names[team_of(by[0])] if by else None})
                elif kind == "pickup" and keep(team_of(e["unit"])):
                    pickups.append({"turn": f["turn"], "team": names[team_of(e["unit"])]})
            if deaths >= 3 and focus_teams is None:
                brawls.append({"turn": f["turn"], "units_down": deaths})
        facts["events"] = {"captures": captures, "carrier_stops": stops, "pickups": pickups, "big_fights": brawls}

    if "standings" in context:
        order = sorted(range(teams), key=lambda t: -end["score"][t])
        facts["standings"] = [{"team": names[t], "score": end["score"][t]} for t in order[:8]]

    if "window_stats" in context:
        stats = {t: Counter() for t in range(teams)}
        for k in range(k0 + 1, k1 + 1):
            for e in frames[k]["events"]:
                if e["type"] == "capture":
                    stats[e["team"]]["captures"] += 1
                elif e["type"] == "pickup":
                    stats[team_of(e["unit"])]["pickups"] += 1
                elif e["type"] == "death":
                    stats[team_of(e["unit"])]["deaths"] += 1
                    by = e.get("by") or []
                    if by:
                        stats[team_of(by[0])]["kills"] += 1
                        if e.get("flag") is not None:
                            stats[team_of(by[0])]["carrier_stops"] += 1
        facts["window_stats"] = [{"team": names[t], **dict(c)} for t, c in stats.items() if c and keep(t)]

    if "positions" in context:
        center = (header["size"] - 1) / 2
        rows = []
        for t in range(teams):
            if not keep(t):
                continue
            base = header["bases"][t]
            bx = sum(x for x, _ in base) / len(base)
            by = sum(y for _, y in base) / len(base)
            alive = [u for u in end["units"][t * 3:t * 3 + 3] if u["pos"]]
            if not alive:
                rows.append({"team": names[t], "alive": 0})
                continue
            home = sum(abs(u["pos"][0] - bx) + abs(u["pos"][1] - by) for u in alive) / len(alive)
            mid = sum(abs(u["pos"][0] - center) + abs(u["pos"][1] - center) for u in alive) / len(alive)
            rows.append({"team": names[t], "alive": len(alive),
                         "carrying_flags": sum(1 for u in alive if u.get("flag") is not None),
                         "avg_cells_from_home": round(home, 1), "avg_cells_from_center": round(mid, 1)})
        facts["positions"] = rows

    if "orders" in context:
        notes = {t: Counter() for t in range(teams)}
        for k in range(k0 + 1, k1 + 1):
            for team_key, raw in (frames[k].get("orders") or {}).items():
                units = raw.get("units", []) if isinstance(raw, dict) else raw
                for u in units or []:
                    note = str(u.get("note") or "").strip()
                    # Coordinates like "2:36,22" are targets, not intent
                    if note and not re.fullmatch(r"[\d:,.\s-]+", note):
                        notes[int(team_key)][note] += 1
        facts["bot_intent_notes"] = [{"team": names[t], "notes": [n for n, _ in c.most_common(4)]}
                                     for t, c in notes.items() if c and keep(t)]
    return facts


# ---------------------------------------------------------------- prompts

def build_prompt(role: dict, lang: str, config: dict, facts: dict, previous: list[str]) -> tuple[str, str]:
    language = config["languages"][lang]
    skill, skill_lang = load_skill(role["id"], lang, config)
    rules = [
        f"- Language: {language['style']}",
        f"- Length: each line {language['length'][role['length']]}.",
        "- Use only facts from the match data below. Never invent scores, kills, turns, names or reasons.",
        f"- Write at most {role['max_lines']} lines for this window, at least {role['min_gap']} turns apart. "
        "Fewer lines are fine; an empty list is fine when nothing is worth saying.",
        f"- Each line's \"turn\" must be between {facts['window']['from_turn']} and {facts['window']['to_turn']}: "
        "the turn where the thing you describe happened, or the last turn for a summary.",
        f"- Across all roles there is at most one line every {min_gap_any(config)} turns, so make each line count: "
        "pick the moments that matter most (lead changes, ties, captures by the leaders, stops of a leader's carrier).",
        '- Add "key": true to a line about a lead change, a tie at the top or the winning capture; key lines are never '
        'dropped when the booth gets crowded. Use it sparingly.',
        '- Reply with JSON only, no other text: {"lines": [{"turn": <integer>, "text": "<line>", "key": <optional true>}]}',
    ]
    if "focus" in facts:
        rules.insert(-1, "- This is a big match: follow only the contenders listed under \"focus\" (the teams fighting for "
                         "first). Don't run through every team's score or name teams outside the race unless they "
                         "directly affect a contender (for example, stopping a leader's flag carrier).")
    if skill_lang != lang:
        rules.insert(0, f"- Write every line in {language['english_name']} ({language['name']}), "
                        "even though your role description is in another language.")
    system = f"{skill}\n\n## Rules for every line\n" + "\n".join(rules)
    user = "Match data for this window (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=1)
    if previous:
        user += "\n\nYour most recent lines (don't repeat them or their phrasing):\n" + "\n".join(f"- {p}" for p in previous)
    return system, user


def parse_lines(text: str) -> list[dict]:
    """Pull {"lines": [...]} out of a model reply, tolerating code fences or stray prose."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise CommentaryError(f"reply had no JSON object: {text[:120]!r}")
    data = json.loads(cleaned[start:end + 1])
    lines = data.get("lines") if isinstance(data, dict) else None
    if not isinstance(lines, list):
        raise CommentaryError("reply JSON has no 'lines' list")
    return lines


def accept_lines(raw: list[dict], role: dict, lang: str, config: dict, t0: int, t1: int,
                 last_turn: int | None) -> list[dict]:
    """Clamp turns to the window, enforce min_gap / max_lines / length. Returns accepted lines."""
    max_chars = config["languages"][lang]["max_chars"]
    out = []
    for item in sorted((r for r in raw if isinstance(r, dict)), key=lambda r: r.get("turn", t1) if isinstance(r.get("turn"), int) else t1):
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        if len(text) > max_chars:
            text = text[:max_chars - 1].rstrip() + "…"
        turn = item.get("turn")
        turn = min(t1, max(t0 + 1, turn)) if isinstance(turn, int) else t1
        if last_turn is not None and turn - last_turn < role["min_gap"]:
            continue
        line = {"turn": turn, "role": role["id"], "text": text}
        if item.get("key") is True:
            line["key"] = True
        out.append(line)
        last_turn = turn
        if len(out) >= role["max_lines"]:
            break
    return out


# ---------------------------------------------------------------- providers

class AnthropicProvider:
    """Claude through the official SDK. Credentials: the named env var, else the SDK's own
    resolution (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / `ant auth login` profile)."""

    # Models that accept the server-side refusal fallback ("default" routing)
    FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}

    def __init__(self, cfg: dict):
        try:
            import anthropic  # noqa: PLC0415  (optional dependency)
        except ImportError as exc:
            raise CommentaryError("the 'claude' provider needs the SDK: pip install anthropic") from exc
        self.anthropic = anthropic
        key = os.environ.get(cfg.get("api_key_env") or "")
        self.client = anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()
        self.model = cfg["model"]
        self.effort = cfg.get("effort", "low")

    def complete(self, system: str, user: str) -> str:
        kwargs = {
            "model": self.model,
            "max_tokens": 4000,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": self.effort},
        }
        if self.model in self.FALLBACK_MODELS:
            kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
            response = self.client.beta.messages.create(**kwargs)
        else:
            response = self.client.messages.create(**kwargs)
        if response.stop_reason == "refusal":
            raise RefusalError("the model declined this window")
        return "".join(block.text for block in response.content if block.type == "text")


class OpenAICompatibleProvider:
    """Any server speaking the OpenAI chat-completions API (DeepSeek, Qwen, OpenAI, Ollama...)."""

    def __init__(self, cfg: dict):
        self.url = cfg["base_url"].rstrip("/") + "/chat/completions"
        self.model = cfg["model"]
        self.json_mode = bool(cfg.get("json_mode"))
        env = cfg.get("api_key_env")
        self.key = os.environ.get(env) if env else None
        if env and not self.key:
            raise CommentaryError(f"set the {env} environment variable for this provider")

    def complete(self, system: str, user: str) -> str:
        body = {"model": self.model, "temperature": 0.8,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if self.json_mode:
            body["response_format"] = {"type": "json_object"}
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        for attempt in range(4):
            req = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=180) as res:
                    data = json.loads(res.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"] or ""
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** attempt * 2)
                    continue
                detail = exc.read().decode("utf-8", "replace")[:300]
                raise CommentaryError(f"{exc.code} from {self.url}: {detail}") from exc
            except urllib.error.URLError as exc:
                if attempt < 3:
                    time.sleep(2 ** attempt * 2)
                    continue
                raise CommentaryError(f"could not reach {self.url}: {exc.reason}") from exc
        raise CommentaryError("unreachable")


def make_provider(name: str, config: dict, model: str | None = None):
    if name not in config["providers"]:
        raise CommentaryError(f"unknown provider '{name}'. Choose from: {', '.join(config['providers'])}")
    cfg = dict(config["providers"][name])
    if model:
        cfg["model"] = model
    kind = cfg["type"]
    if kind == "mock":
        return None
    if cfg.get("model", "").startswith("SET-"):
        raise CommentaryError(f"set a model for provider '{name}' in commentary/config.json or pass --model")
    if kind == "anthropic":
        return AnthropicProvider(cfg)
    return OpenAICompatibleProvider(cfg)


# ---------------------------------------------------------------- mock writer

class MockWriter:
    """Fills commentary/mock/<lang>.json templates from facts. No network, deterministic."""

    def __init__(self, lang: str):
        path = MOCK_DIR / f"{lang}.json"
        if not path.exists():
            raise CommentaryError(f"no mock templates for '{lang}' (add commentary/mock/{lang}.json)")
        self.t = strip_notes(read_json(path))
        self.lang = lang

    def pick(self, key: str, seed: int, **values) -> str:
        options = self.t.get(key) or []
        if not options:
            return ""
        return options[seed % len(options)].format(**values)

    def lines(self, role: dict, facts: dict, replay: dict, lang: str) -> list[dict]:
        w = facts["window"]
        t0, t1 = w["from_turn"] - 1, w["to_turn"]
        rid = role["id"]
        if rid == "caster":
            cands = []
            ev = facts.get("events", {})
            for c in ev.get("captures", []):
                key = "caster.capture_lead" if c["takes_lead"] else "caster.capture_tie" if c["ties_lead"] else "caster.capture"
                cands.append((0 if key != "caster.capture" else 1, c["turn"],
                              self.pick(key, c["turn"], team=c["team"], score=c["scoreline"]), key != "caster.capture"))
            for s in ev.get("carrier_stops", []):
                if s["by"]:
                    cands.append((2, s["turn"], self.pick("caster.stop", s["turn"], by=s["by"], victim=s["victim"]), False))
            for b in ev.get("big_fights", []):
                cands.append((3, b["turn"], self.pick("caster.brawl", b["turn"], count=b["units_down"]), False))
            chosen = []
            for _prio, turn, text, is_key in sorted(cands):
                if text and all(abs(turn - c["turn"]) >= role["min_gap"] for c in chosen):
                    chosen.append({"turn": turn, "text": text, **({"key": True} if is_key else {})})
                if len(chosen) >= role["max_lines"]:
                    break
            return sorted(chosen, key=lambda c: c["turn"])

        standings = facts.get("standings") or []
        stats = facts.get("window_stats") or []
        if not standings:
            return []
        top = standings[0]
        tied = [s["team"] for s in standings if s["score"] == top["score"]]
        joiner = "、" if lang == "zh" else " and "
        if rid == "color":
            caps = sorted(stats, key=lambda s: -s.get("captures", 0))
            if top["score"] > 0 and len(tied) > 1:
                text = self.pick("color.tied", t1, tied=joiner.join(tied[:3]), lead_score=top["score"])
            elif not caps or caps[0].get("captures", 0) == 0:
                text = self.pick("color.quiet", t1, t0=t0 + 1, t1=t1)
            else:
                second = standings[1] if len(standings) > 1 else top
                text = self.pick("color.leading", t1, leader=top["team"], lead_score=top["score"],
                                 gap=top["score"] - second["score"], second=second["team"],
                                 hot=caps[0]["team"], hot_caps=caps[0]["captures"])
            return [{"turn": t1, "text": text}] if text else []

        if rid == "analyst":
            if w["phase"] == "final":
                team_index = replay["names"].index(next(n for n in replay["names"] if display_name(n, lang) == top["team"]))
                caps = picks = 0
                for f in replay["frames"]:
                    for e in f["events"]:
                        if e["type"] == "capture" and e["team"] == team_index:
                            caps += 1
                        elif e["type"] == "pickup" and team_of(e["unit"]) == team_index:
                            picks += 1
                conv = round(100 * caps / picks) if picks else 0
                return [{"turn": t1, "text": self.pick("analyst.final", t1, leader=top["team"], lead_score=top["score"], conv=conv)}]
            with_picks = [s for s in stats if s.get("pickups")]
            killers = sorted(stats, key=lambda s: -s.get("kills", 0))
            positions = [p for p in facts.get("positions", []) if p.get("alive")]
            if (t1 // role["window"]) % 2 and len(positions) >= 2:
                pos = sorted(positions, key=lambda p: -p["avg_cells_from_home"])
                return [{"turn": t1, "text": self.pick("analyst.push", t1, pusher=pos[0]["team"], dist=pos[0]["avg_cells_from_home"],
                                                       turtle=pos[-1]["team"], dist2=pos[-1]["avg_cells_from_home"])}]
            if with_picks and killers:
                best = max(with_picks, key=lambda s: (s.get("captures", 0) / s["pickups"], s.get("captures", 0)))
                return [{"turn": t1, "text": self.pick("analyst.window", t1, t0=t0 + 1, t1=t1, best=best["team"],
                                                       best_caps=best.get("captures", 0), best_picks=best["pickups"],
                                                       killer=killers[0]["team"], kills=killers[0].get("kills", 0))}]
        return []


# ---------------------------------------------------------------- spacing

DEFAULT_MIN_GAP = 5


def min_gap_any(config: dict) -> int:
    return int(config.get("generation", {}).get("min_turns_between_lines", DEFAULT_MIN_GAP))


def space_lines(lines: list[dict], gap: int, priority: dict[str, int]) -> list[dict]:
    """Keep at most one line per `gap` turns across all roles. Lines marked "key" (lead changes,
    ties, the winning capture) claim their turns first, then higher-priority roles, then earlier
    turns, so the decisive moments survive and a rare analyst line beats routine caster lines."""
    kept: list[dict] = []
    taken: list[int] = []
    for ln in sorted(lines, key=lambda ln: (not ln.get("key"), -priority.get(ln["role"], 0), ln["turn"])):
        if all(abs(ln["turn"] - t) >= gap for t in taken):
            kept.append(ln)
            taken.append(ln["turn"])
    return sorted(kept, key=lambda ln: ln["turn"])


def role_priorities(config: dict) -> dict[str, int]:
    return {rid: int(load_role(rid).get("priority", 1)) for rid in config["roles"]}


# ---------------------------------------------------------------- output

def output_path(key: str, lang: str) -> Path:
    return OUTPUT_DIR / key / f"{lang}.json"


def write_track(key: str, lang: str, config: dict, new_lines: list[dict], roles: list[dict], source: dict) -> Path:
    """Merge freshly generated lines for `roles` into the match's language file."""
    path = output_path(key, lang)
    existing = read_json(path) if path.exists() else {}
    replaced = {r["id"] for r in roles}
    lines = [ln for ln in existing.get("lines", []) if ln["role"] not in replaced] + new_lines
    gap = min_gap_any(config)
    lines = space_lines(lines, gap, role_priorities(config))
    sources = {k: v for k, v in existing.get("sources", {}).items() if k not in replaced}
    for r in roles:
        sources[r["id"]] = source
    used = {ln["role"] for ln in lines}
    role_meta = [{"id": rid, "name": load_role(rid)["name"].get(lang) or load_role(rid)["name"].get("en"),
                  "icon": load_role(rid)["icon"], "caption": bool(load_role(rid).get("caption")),
                  "priority": int(load_role(rid).get("priority", 1))}
                 for rid in config["roles"] if rid in used]
    out = {"version": 1, "match": key, "language": lang, "min_gap": gap, "roles": role_meta, "sources": sources,
           "lines": lines}
    path.parent.mkdir(parents=True, exist_ok=True)
    write_pretty(path, out)
    return path


def today() -> str:
    return dt.date.today().isoformat()
