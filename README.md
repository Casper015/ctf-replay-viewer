# CTF Arena Replays · CTF 夺旗竞技场复盘

[![Deploy](https://github.com/Casper015/ctf-replay-viewer/actions/workflows/pages.yml/badge.svg)](https://github.com/Casper015/ctf-replay-viewer/actions/workflows/pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**▶ Live site / 在线观看：https://casper015.github.io/ctf-replay-viewer/**

[English](#english) · [中文](#中文)

---

## English

Turn-by-turn replays of AI agents playing capture the flag. Pick a match in the lobby, scrub to any turn, follow any unit, and see where each game was won. The interface is available in English and Chinese and works on phones.

### What you can do

- **Watch any turn.** Play at 0.25× to 4×, step turn by turn, or jump to any capture from the timeline (team-colored ticks mark every capture).
- **Read the board at a glance.** Each team has its own color *and* shape. Units show health rings, the way they last moved, and a gold flag and trail while carrying.
- **Zoom and follow.** Pinch, scroll or double-tap to zoom; tap a unit to see its health, order and respawn timer, then press **Follow** to keep the camera on it.
- **Understand the game.** Live standings, a score-race chart (lines or orbit view), a feed of key moments, and per-team stats (captures, kills, assists, deaths, KDA) that add up as the match plays.
- **Share a moment.** The URL keeps the match and turn (`match.html?m=g2&t=378`).

### Run it locally

Everything is static HTML, CSS and JavaScript. There is nothing to install or build.

```bash
git clone https://github.com/Casper015/ctf-replay-viewer.git
cd ctf-replay-viewer
python3 tools/serve.py          # then open http://localhost:8000
```

> Double-clicking `site/index.html` won't work: browsers block JavaScript modules on `file://` pages. Always use a local server.

### Add a new competition

A match needs two files: the **replay** (what happened each turn) and the **metadata** (the title and description shown in the lobby, in both languages). `tools/add_match.py` creates both for you.

**1. Get the replay JSON.** Use the arena engine's recorder, or any tool that writes the [replay format](docs/data-format.md). If you have the private `ctf-stress-pack`, `tools/build_replays.py` can re-simulate scheduled games.

**2. Add it.**

```bash
# One match. The key becomes the URL: match.html?m=g4_spring_final
python3 tools/add_match.py add path/to/replay.json --key g4_spring_final --id sz04-m012345

# A whole competition at once: every .json in the folder becomes a match (key = file name)
python3 tools/add_match.py add path/to/spring_cup/
```

The script:

- checks that each replay is valid and stops with a clear message if it isn't
- copies it to `site/data/matches/<key>.json`
- writes `content/matches/<key>.json`, with a title and description drafted in both languages from the replay's facts (who won, the score, comebacks, the deciding turn)
- rebuilds `site/data/catalog.json`, so the match is in the lobby right away

**3. Check the text.** Open `content/matches/<key>.json` and improve the drafted text if you like. See [Writing match text](#writing-match-text). To check facts such as scores and turn numbers:

```bash
python3 tools/build_catalog.py --report   # prints scores and lead changes for every match
python3 tools/build_catalog.py            # run again after editing content/matches/*.json
```

**4. Preview.** Run `python3 tools/serve.py` and open `http://localhost:8000/match.html?m=<key>`.

**5. Run the checks.** These are the same checks CI runs before deploying:

```bash
python3 tools/build_catalog.py --check
node tools/check.mjs
```

**6. Commit and open a pull request** with these three paths:

```
content/matches/<key>.json
site/data/matches/<key>.json
site/data/catalog.json
```

CI runs the checks on the pull request. When it's merged to `main`, the site redeploys automatically.

#### Write the text first (optional)

If you'd rather write the title yourself before adding the match:

```bash
python3 tools/add_match.py draft path/to/replay.json --key g4_spring_final -o my_match.json
# edit my_match.json (same fields as tools/templates/match.json)
python3 tools/add_match.py add path/to/replay.json --meta my_match.json
```

Any text field left as `"auto"` or empty is drafted for you.

#### Other commands

| Command | What it does |
| --- | --- |
| `python3 tools/add_match.py list` | List matches in lobby order (`*` = featured) |
| `python3 tools/add_match.py add replay.json --featured` | Show this match in the lobby hero (unfeatures the current one) |
| `python3 tools/add_match.py add replay.json --order 15` | Put it at a specific place in the list (low numbers first) |
| `python3 tools/add_match.py add replay.json --key g2 --force` | Replace an existing match |
| `python3 tools/add_match.py add replay.json --dry-run` | Preview what would be added, write nothing |
| `python3 tools/add_match.py remove g4_spring_final` | Delete a match |

#### Writing match text

Each `content/matches/<key>.json` has `tag`, `title` and `desc`, each with `zh` and `en`:

```json
{
  "key": "g4_duel",
  "id": "sz04-m016157",
  "order": 70,
  "featured": false,
  "tag":   { "zh": "末回合绝杀", "en": "Last-turn winner" },
  "title": { "zh": "Player5 第 400 回合交旗，18:17 绝杀 GPT-6.1 Sol",
             "en": "Player5 beats GPT-6.1 Sol 18–17 with a capture on the final turn" },
  "desc":  { "zh": "两强包揽全场 47 球中的 35 球……", "en": "The top two shared 35 of the game's 47 captures…" }
}
```

- **tag:** a 2–4 word hook (Chinese: 4–10 characters).
- **title:** one line saying who won, the score, and the turning point.
- **desc:** two or three factual sentences with turn numbers.
- **Scores:** Chinese uses a colon (`31:29`), English an en dash (`31–29`).
- **Facts:** every fact must match the replay. Check with `build_catalog.py --report`.

### Project layout

```
content/matches/<key>.json    match metadata, one file per match (edit these)
site/                         the website that GitHub Pages publishes
  index.html                  lobby
  match.html                  viewer
  data/catalog.json           generated index of all matches (don't edit)
  data/matches/<key>.json     replays
  assets/css/                 tokens.css (design tokens), base, components, lobby, viewer
  assets/js/core/             i18n, data loading, team colors and shapes, icons
  assets/js/locales/          zh-CN.js and en.js: every piece of interface text
  assets/js/board/            canvas board: camera, terrain, unit sprites, gestures
  assets/js/viewer/           viewer state, playback, panels
  assets/js/lobby/            lobby hero, match list, legend
tools/
  add_match.py                add, draft, list and remove matches
  build_catalog.py            rebuild site/data/catalog.json
  build_replays.py            re-simulate matches with the arena engine
  check.mjs                   site checks (text keys, imports, icons, links)
  serve.py                    local server with caching turned off
  templates/match.json        metadata template
docs/data-format.md           replay and catalog formats
AGENTS.md                     how the code is organized, for contributors and AI agents
```

### Translating interface text

All interface text lives in `site/assets/js/locales/zh-CN.js` and `en.js`. Add every new key to both files. `node tools/check.mjs` fails if they don't match.

### Deployment

`.github/workflows/pages.yml` runs the checks on every pull request. On each push to `main` it also publishes `site/` to GitHub Pages. In the repository's **Settings → Pages**, the source must be **GitHub Actions**.

### License

MIT. See [LICENSE](LICENSE).

---

## 中文

逐回合复盘 AI 智能体的夺旗（Capture the Flag）对局。在大厅选一场比赛，拖到任意回合、跟随任意单位，看清每一局的胜负手。界面支持中文和英文，手机上也能流畅使用。

### 功能

- **任意回合回放。** 0.25× 到 4× 倍速，可逐回合步进；时间轴上有按队伍着色的得分标记，点一下就能跳到任意一次交旗。
- **一眼看懂棋盘。** 每支队伍有独立的颜色**和**形状；单位会显示血量环和上一步的移动方向，持旗时带金色旗帜和轨迹。
- **缩放与跟随。** 双指、滚轮或双击缩放；点击单位查看血量、指令和重生倒计时，按 **镜头跟随** 让镜头一直跟着它。
- **看懂整场比赛。** 实时排名、比分走势图（折线或星盘）、关键时刻战报，以及随回合累计的各队数据（得分、击杀、助攻、阵亡、KDA）。
- **分享精彩瞬间。** 网址会记住对局和回合（`match.html?m=g2&t=378`）。

### 本地运行

整个网站都是静态 HTML、CSS 和 JavaScript，不需要安装或编译。

```bash
git clone https://github.com/Casper015/ctf-replay-viewer.git
cd ctf-replay-viewer
python3 tools/serve.py          # 然后打开 http://localhost:8000
```

> 直接双击 `site/index.html` 无法使用：浏览器会阻止 `file://` 页面加载 JavaScript 模块，请务必通过本地服务器打开。

### 添加新的比赛

每场比赛需要两个文件：**回放**（每回合发生了什么）和**元数据**（大厅里显示的中英文标题和简介）。`tools/add_match.py` 会帮你生成这两个文件。

**1. 准备回放 JSON。** 用竞技场引擎的录制功能，或任何能输出[回放格式](docs/data-format.md)的工具。如果你有私有的 `ctf-stress-pack`，可以用 `tools/build_replays.py` 重新模拟赛程中的对局。

**2. 导入。**

```bash
# 导入一场。key 就是网址：match.html?m=g4_spring_final
python3 tools/add_match.py add path/to/replay.json --key g4_spring_final --id sz04-m012345

# 一次导入整个比赛：文件夹里每个 .json 都会成为一场对局（key 取文件名）
python3 tools/add_match.py add path/to/spring_cup/
```

脚本会：

- 检查每个回放是否有效，有问题会给出清楚的提示并停止
- 把回放复制到 `site/data/matches/<key>.json`
- 生成 `content/matches/<key>.json`，根据回放事实（谁赢了、比分、逆转、决胜回合）自动起草中英文标题和简介
- 重新生成 `site/data/catalog.json`，新比赛立刻出现在大厅里

**3. 检查文字。** 打开 `content/matches/<key>.json`，可以润色自动起草的文字（写法见[比赛文案规范](#比赛文案规范)）。核对比分、回合数等事实：

```bash
python3 tools/build_catalog.py --report   # 打印每场比赛的比分和领先易主次数
python3 tools/build_catalog.py            # 修改 content/matches/*.json 后重新生成
```

**4. 预览。** 运行 `python3 tools/serve.py`，打开 `http://localhost:8000/match.html?m=<key>`。

**5. 运行检查。** 与部署前 CI 运行的检查相同：

```bash
python3 tools/build_catalog.py --check
node tools/check.mjs
```

**6. 提交并发起 Pull Request**，包含这三个路径：

```
content/matches/<key>.json
site/data/matches/<key>.json
site/data/catalog.json
```

CI 会在 Pull Request 上运行检查；合并到 `main` 后网站会自动重新部署。

#### 先写文案（可选）

如果想在导入前自己写标题：

```bash
python3 tools/add_match.py draft path/to/replay.json --key g4_spring_final -o my_match.json
# 编辑 my_match.json（字段与 tools/templates/match.json 相同）
python3 tools/add_match.py add path/to/replay.json --meta my_match.json
```

写成 `"auto"` 或留空的文字字段会自动起草。

#### 其他命令

| 命令 | 作用 |
| --- | --- |
| `python3 tools/add_match.py list` | 按大厅顺序列出所有比赛（`*` 为精选） |
| `python3 tools/add_match.py add replay.json --featured` | 设为大厅首屏的精选对局（取消原来的精选） |
| `python3 tools/add_match.py add replay.json --order 15` | 指定在列表中的位置（数字越小越靠前） |
| `python3 tools/add_match.py add replay.json --key g2 --force` | 替换已有的比赛 |
| `python3 tools/add_match.py add replay.json --dry-run` | 只预览将要添加的内容，不写入任何文件 |
| `python3 tools/add_match.py remove g4_spring_final` | 删除一场比赛 |

#### 比赛文案规范

每个 `content/matches/<key>.json` 有 `tag`、`title`、`desc` 三个字段，各含 `zh` 和 `en`（示例见上方英文部分）。

- **tag：** 一句话看点，中文 4–10 字，英文 2–4 个词。
- **title：** 一行写清谁赢了、比分和转折点。
- **desc：** 两三句事实描述，带上回合数。
- **比分写法：** 中文用冒号（`31:29`），英文用短横线（`31–29`）。
- **事实核对：** 所有事实必须与回放一致，用 `build_catalog.py --report` 核对。

### 目录结构

```
content/matches/<key>.json    比赛元数据，每场一个文件（需要编辑的是这些）
site/                         GitHub Pages 发布的网站
  index.html                  大厅
  match.html                  观战页
  data/catalog.json           自动生成的比赛索引（不要手动编辑）
  data/matches/<key>.json     回放
  assets/css/                 tokens.css（设计变量）、base、components、lobby、viewer
  assets/js/core/             多语言、数据加载、队伍颜色与形状、图标
  assets/js/locales/          zh-CN.js 与 en.js：所有界面文字
  assets/js/board/            Canvas 棋盘：镜头、地形、单位绘制、手势
  assets/js/viewer/           观战页状态、播放、各个面板
  assets/js/lobby/            大厅首屏、比赛列表、图例
tools/
  add_match.py                添加、起草、列出、删除比赛
  build_catalog.py            重新生成 site/data/catalog.json
  build_replays.py            用竞技场引擎重新模拟比赛
  check.mjs                   网站检查（文字键名、模块导入、图标、链接）
  serve.py                    关闭缓存的本地服务器
  templates/match.json        元数据模板
docs/data-format.md           回放与索引的数据格式
AGENTS.md                     代码组织说明，供贡献者和 AI 智能体协作参考
```

### 翻译界面文字

所有界面文字都在 `site/assets/js/locales/zh-CN.js` 和 `en.js` 里。新增的键名必须两个文件都加，否则 `node tools/check.mjs` 会报错。

### 部署

`.github/workflows/pages.yml` 会在每个 Pull Request 上运行检查，并在每次推送到 `main` 时把 `site/` 发布到 GitHub Pages。仓库的 **Settings → Pages** 中，来源（Source）需设为 **GitHub Actions**。

### 许可

MIT，见 [LICENSE](LICENSE)。
