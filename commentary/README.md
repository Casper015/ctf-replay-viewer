# AI commentary · AI 解说

[English](#english) · [中文](#中文)

---

## English

Every match can have a commentary booth of three roles, written by any LLM (or by hand):

| Role | Job | Speaks |
| --- | --- | --- |
| **Caster** (`caster`) | Play-by-play: captures, carrier stops, big fights | Often, short lines |
| **Color commentator** (`color`) | Momentum, rivalries, what the score means | Every ~25 turns |
| **Analyst** (`analyst`) | Why: conversion, fights, positioning, the bots' intent | Every ~50 turns, plus halftime and the end |
| **Crowd** (`crowd`) | Audience bullet comments (弹幕) that fly across the board | Bursts after big moments, up to 4 per 10 turns |

Viewers see the lines in the **Commentary** panel as the replay reaches each turn (no spoilers), and caster/color lines appear as **captions** on the board.

Two rules keep the booth watchable (both in `config.json` → `generation`):
- **At most one line every 5 turns**, across all booth roles (`min_turns_between_lines`). The crowd's bullet comments (`"display": "danmaku"` in its `role.json`) don't count; they have their own pacing and an on/off **弹幕** toggle in the viewer. Lines marked `"key": true` (lead changes, ties, the winner) keep their slot first, then analyst > caster > color.
- **Big matches follow the contenders** (`focus`): with more than 4 teams, roles only receive and talk about the top 3 teams by score. Others are mentioned only when they stop a contender's carrier.

### Files

```
commentary/
  config.json                 providers (which LLMs), languages, enabled roles: the demo file that controls everything
  roles/<role>/role.json      pacing and what facts the role receives
  roles/<role>/skill.zh.md    the role's persona and instructions, one file per language
  roles/<role>/skill.en.md
  mock/<lang>.json            templates for the offline "mock" provider (no LLM)
  briefs/                     exported whole-match briefs (generated, not committed)
.claude/skills/ctf-commentary/  skill + reference that teach an LLM the game, the data and the output format
tools/commentate.py           generate / export / import / check
site/data/commentary/<key>/<lang>.json   what the website loads (generated)
```

### Way 1: an LLM API writes it (online)

```bash
python3 tools/commentate.py generate g2                                  # mock: free, template lines
export ANTHROPIC_API_KEY=...;  python3 tools/commentate.py generate g2 --provider claude
export DEEPSEEK_API_KEY=...;   python3 tools/commentate.py generate g2 --provider deepseek --lang zh
python3 tools/commentate.py generate --all --provider qwen --roles caster
python3 tools/commentate.py prompt g2 --role analyst --lang en --window 3  # see exactly what is sent
```

The script walks the match window by window for each role and language, sends the facts plus the role's skill, checks the reply (turns inside the window, pacing, length) and writes `site/data/commentary/<key>/<lang>.json`. Providers in `config.json`:

- `claude` uses the official `anthropic` Python SDK (`pip install anthropic`).
- `deepseek`, `qwen`, `openai` and `ollama` use the OpenAI-compatible chat API. Any compatible server works: copy an entry and change `base_url`/`model`.
- API keys are read from the environment variable named in `api_key_env` and never written to files.

### Way 2: offline (any LLM or person, no API)

1. Export a brief of the **whole match**. It includes the game rules, what every field means, each role's skill, and every 10-turn window:
   ```bash
   python3 tools/commentate.py export g2 --lang zh      # -> commentary/briefs/g2.zh.md
   ```
2. Give the brief to any LLM (a chat app, a local model, an agent) or a human writer. It writes `g2.zh.json`:
   ```json
   { "match": "g2", "language": "zh", "source": {"provider": "offline", "model": "..."},
     "lines": [ {"turn": 6, "role": "caster", "text": "..."} ] }
   ```
   In Claude Code, the `ctf-commentary` skill in this repo is picked up automatically.
3. Preview it in the viewer without publishing: open the match, go to **Commentary → Open file…**, and pick the JSON. It stays on your device.
4. Publish it:
   ```bash
   python3 tools/commentate.py import g2.zh.json
   ```
   Import validates roles, turns and length, merges with other roles' lines and rebuilds the catalog.

`site/data/commentary/g2/` was written this way, as a worked example.

### Add a language

1. Add an entry under `languages` in `config.json`: `name`, `english_name`, `style` (punctuation, score format), `length` words for short/medium/long, and `max_chars`.
2. Add `"<lang>": "..."` to `name` in every `roles/*/role.json`.
3. Optional but recommended: `roles/<role>/skill.<lang>.md` for each role. Without it, the English skill is used with an instruction to write in the new language.
4. Optional: `mock/<lang>.json` for template output.

Commentary languages are independent of the interface languages (`site/assets/js/locales/`). The viewer offers every language a match has.

### Add a role

Copy a folder in `roles/`, edit `role.json` (`id`, `name`, `icon` from `mic chat chart activity swords flag trophy info`, `window`, `max_lines`, `min_gap`, `length`, `context`, `caption`), write its skill files, and add the id to `roles` in `config.json`.

### Check

```bash
python3 tools/commentate.py check     # config, roles, skills and every commentary file (CI runs this)
```

---

## 中文

每场比赛都可以配一个由三个角色组成的解说席，由任意大模型撰写（也可以人工撰写）：

| 角色 | 职责 | 发言频率 |
| --- | --- | --- |
| **解说**（`caster`） | 实况：交旗、截杀持旗、混战 | 频繁、短句 |
| **嘉宾点评**（`color`） | 势头、对抗、比分意味着什么 | 约每 25 回合 |
| **战术分析师**（`analyst`） | 为什么：转化率、交火、站位、机器人的意图 | 约每 50 回合，以及半场和终场 |
| **观众弹幕**（`crowd`） | 从棋盘上飞过的观众弹幕 | 关键时刻后集中出现，每 10 回合最多 4 条 |

观众在**解说**面板中看到台词，回放到哪一回合才显示到哪一回合（不剧透）；解说和嘉宾的台词还会作为**字幕**显示在棋盘上。

两条规则让解说不会过于密集（都在 `config.json` → `generation` 中）：
- **每 5 个回合最多一句**，解说席角色共用（`min_turns_between_lines`）。观众弹幕（`role.json` 中 `"display": "danmaku"`）不计入，有自己的节奏，观战页可用 **弹幕** 开关打开或关闭。标记了 `"key": true` 的台词（领先易主、扳平、制胜球）优先保留，其次按 分析师 > 解说 > 嘉宾 的顺序。
- **大型比赛只跟踪争冠队伍**（`focus`）：超过 4 支队伍时，角色只拿到、也只评论得分前三的队伍；其他队伍只有在截下争冠队伍的持旗者时才会被提及。

### 文件

```
commentary/
  config.json                 模型服务、语言、启用的角色：控制一切的演示配置
  roles/<角色>/role.json      发言节奏和角色能拿到哪些数据
  roles/<角色>/skill.zh.md    角色设定和要求，每种语言一个文件
  roles/<角色>/skill.en.md
  mock/<语言>.json            离线 mock 模式的模板（不调用大模型）
  briefs/                     导出的整场比赛简报（自动生成，不提交）
.claude/skills/ctf-commentary/  技能和参考资料：教大模型理解游戏规则、数据含义和输出格式
tools/commentate.py           generate / export / import / check
site/data/commentary/<对局>/<语言>.json   网站加载的文件（自动生成）
```

### 方式一：调用大模型 API（在线）

```bash
python3 tools/commentate.py generate g2                                  # mock：免费，模板台词
export ANTHROPIC_API_KEY=...;  python3 tools/commentate.py generate g2 --provider claude
export DEEPSEEK_API_KEY=...;   python3 tools/commentate.py generate g2 --provider deepseek --lang zh
python3 tools/commentate.py generate --all --provider qwen --roles caster
python3 tools/commentate.py prompt g2 --role analyst --lang en --window 3  # 查看实际发送的提示词
```

脚本会按角色和语言逐个窗口处理整场比赛：发送该窗口的事实和角色技能，检查回复（回合是否在窗口内、节奏、长度），写入 `site/data/commentary/<对局>/<语言>.json`。`config.json` 中的模型服务：

- `claude`：使用官方 `anthropic` Python SDK（`pip install anthropic`）。
- `deepseek`、`qwen`、`openai`、`ollama`：使用 OpenAI 兼容接口。任何兼容服务都可以，复制一项再改 `base_url` 和 `model` 即可。
- API 密钥从 `api_key_env` 指定的环境变量读取，绝不写入文件。

### 方式二：离线（任意大模型或人工，不需要 API）

1. 导出**整场比赛**的简报，内含游戏规则、每个字段的含义、各角色技能，以及每 10 回合的数据：
   ```bash
   python3 tools/commentate.py export g2 --lang zh      # -> commentary/briefs/g2.zh.md
   ```
2. 把简报交给任意大模型（聊天应用、本地模型、智能体）或人工撰稿人，让它写出 `g2.zh.json`（格式见上方英文部分）。在 Claude Code 中，本仓库的 `ctf-commentary` 技能会自动生效。
3. 不发布也能预览：打开比赛，进入**解说 → 打开文件…**，选择这个 JSON，文件只在本机使用。
4. 发布：
   ```bash
   python3 tools/commentate.py import g2.zh.json
   ```
   导入时会校验角色、回合和长度，与其他角色的台词合并，并重新生成索引。

`site/data/commentary/g2/` 就是用这种方式写成的示例。

### 添加语言

1. 在 `config.json` 的 `languages` 下新增一项：`name`、`english_name`、`style`（标点、比分写法）、短/中/长三档的 `length` 描述和 `max_chars`。
2. 在每个 `roles/*/role.json` 的 `name` 中加入该语言。
3. 建议为每个角色添加 `roles/<角色>/skill.<语言>.md`；没有时会使用英文技能，并要求用新语言写作。
4. 可选：添加 `mock/<语言>.json` 以支持模板输出。

解说语言与界面语言（`site/assets/js/locales/`）相互独立，观战页会列出这场比赛已有的所有解说语言。

### 添加角色

复制 `roles/` 中的一个文件夹，修改 `role.json`（`id`、`name`、`icon`（可选 `mic chat chart activity swords flag trophy info`）、`window`、`max_lines`、`min_gap`、`length`、`context`、`caption`），编写技能文件，再把 id 加入 `config.json` 的 `roles`。

### 检查

```bash
python3 tools/commentate.py check     # 检查配置、角色、技能和所有解说文件（CI 会运行）
```
