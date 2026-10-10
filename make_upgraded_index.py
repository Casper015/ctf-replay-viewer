import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 读取全量对局数据
data_file = Path("all_replays_data.json")
if not data_file.exists():
    data_file = Path(r"C:\Users\caspe\OneDrive\Code\AI_Test\all_replays_data.json")

raw_data = json.loads(data_file.read_text(encoding='utf-8'))

# 提取各场比赛的轻量级元数据
all_meta = []
for k, v in raw_data.items():
    all_meta.append({
        'key': k,
        'id': v.get('id', ''),
        'tag': v.get('tag', ''),
        'badge': v.get('badge', ''),
        'title': v.get('title', ''),
        'desc': v.get('desc', ''),
        'teams': v['replay']['header']['teams'],
        'size': v['replay']['header']['size'],
        'file': f"match_{k}.html",
        'top': v.get('enhanced_stats', [])[:3]
    })


def generate_lobby_html(meta_list):
    cards_html = ""
    for m in meta_list:
        top_teams_html = ""
        for rank_idx, t in enumerate(m['top']):
            color_dot = ['#fbbf24', '#94a3b8', '#d97706'][rank_idx] if rank_idx < 3 else '#64748b'
            medal = ['🥇', '🥈', '🥉'][rank_idx] if rank_idx < 3 else f"#{rank_idx+1}"
            top_teams_html += f"""
              <div class="flex items-center justify-between text-xs py-1 border-b border-[#1e2a3b]/60 last:border-none">
                <span class="flex items-center gap-1.5 truncate">
                  <span>{medal}</span>
                  <span class="font-bold text-[#f0f6fc] truncate">{t['name']}</span>
                </span>
                <span class="font-mono font-bold text-emerald-400 ml-2">{t['score']} 进球</span>
              </div>
            """

        category_tag = "15人" if m['teams'] == 15 else ("8人" if m['teams'] == 8 else ("4人" if m['teams'] == 4 else "2-3人"))
        category_filter = "15" if m['teams'] == 15 else ("8" if m['teams'] == 8 else ("4" if m['teams'] == 4 else "few"))

        cards_html += f"""
          <div class="match-lobby-card bg-[#151d28] border border-[#26354a] hover:border-blue-500/60 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between transition-all duration-200 hover:-translate-y-1 hover:shadow-blue-500/10"
               data-category="{category_filter}" data-search="{m['key']} {m['id']} {m['tag']} {m['title']} {m['desc']}">
            <div>
              <div class="flex items-center justify-between gap-2 mb-2.5">
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/15 text-blue-400 border border-blue-500/30">
                  {m['badge'].split('·')[0].strip()}
                </span>
                <span class="text-[11px] font-mono text-[#8ca0ba]">{m['id']}</span>
              </div>

              <h3 class="text-sm sm:text-base font-extrabold text-[#f0f6fc] leading-snug line-clamp-2 mb-1.5">
                {m['title']}
              </h3>
              <p class="text-xs text-[#8ca0ba] line-clamp-2 leading-relaxed mb-4">
                {m['desc']}
              </p>

              <!-- 前三名终盘战果 -->
              <div class="bg-[#0b1017] rounded-xl p-2.5 border border-[#1e2a3b] mb-4">
                <div class="text-[10px] font-semibold text-[#8ca0ba] uppercase tracking-wider mb-1 flex justify-between">
                  <span>终盘三甲</span>
                  <span class="text-blue-400">{m['size']}×{m['size']} 棋盘</span>
                </div>
                {top_teams_html}
              </div>
            </div>

            <a href="{m['file']}" 
               class="block w-full text-center py-2.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 font-bold text-white text-xs sm:text-sm shadow-md hover:shadow-blue-500/25 transition">
              ▶ 进入独立观战室复盘 →
            </a>
          </div>
        """

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>CTF 多智能体夺旗 · 官方赛事大厅 (Match Lobby)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b1017;
      --panel: #151d28;
      --line: #26354a;
      --ink: #f0f6fc;
      --muted: #8ca0ba;
    }}
    * {{ box-sizing: border-box; }}
    body {{ 
      background-color: var(--bg); 
      color: var(--ink); 
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      min-height: 100vh;
    }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0b1017; }}
    ::-webkit-scrollbar-thumb {{ background: #26354a; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #3b82f6; }}
  </style>
</head>
<body class="antialiased p-3 sm:p-6 lg:p-8">
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- 顶部 Hero 导航 -->
    <header class="bg-gradient-to-r from-[#151d28] via-[#162132] to-[#151d28] border border-[#26354a] rounded-2xl p-5 sm:p-7 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-5">
      <div>
        <div class="flex flex-wrap items-center gap-2 mb-2.5">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            ✓ 8,000 局官方引擎评测精选
          </span>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            AMD Ryzen 9 7945HX vs Apple M5
          </span>
          <span class="text-xs text-[#8ca0ba]">15 大 AI 模型全员实战</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#f0f6fc]">
          🏆 CTF 多智能体夺旗 · 官方对局赛事大厅
        </h1>
        <p class="text-xs sm:text-sm text-[#8ca0ba] mt-1.5 max-w-2xl">
          各战役均配备独立观战页面秒开体验 · 沉浸式全屏微操复盘 · 实时 KDA 战损比矩阵 · 动态比分天体图
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <a href="match_g15_rec.html" 
           class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 font-bold text-xs sm:text-sm text-white shadow-lg hover:shadow-blue-500/30 flex items-center gap-2 transition">
          <span>🔥</span>
          <span>置顶高光战役 (15人 90球)</span>
        </a>
        <a href="https://github.com/Casper015/ctf-replay-viewer" target="_blank" 
           class="px-3.5 py-2.5 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-xs sm:text-sm font-medium text-[#f0f6fc] flex items-center gap-2 transition">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          <span class="hidden sm:inline">GitHub</span>
        </a>
      </div>
    </header>

    <!-- 战役大盘高能卡片 -->
    <section class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md">
        <div class="text-[#8ca0ba] text-xs">⚔️ 收录经典战役</div>
        <div class="text-xl sm:text-2xl font-extrabold text-[#f0f6fc] mt-1 font-mono">11 场</div>
        <div class="text-[11px] text-[#8ca0ba] mt-0.5">涵盖 15人、8人、4人及微型对决</div>
      </div>
      <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md">
        <div class="text-[#8ca0ba] text-xs">⚡ 单场历史破门纪录</div>
        <div class="text-xl sm:text-2xl font-extrabold text-emerald-400 mt-1 font-mono">90 次进球</div>
        <div class="text-[11px] text-[#8ca0ba] mt-0.5">49×49 地图 · 45 单位全图疯狂奔袭</div>
      </div>
      <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md">
        <div class="text-[#8ca0ba] text-xs">👑 单体终极破门纪录</div>
        <div class="text-xl sm:text-2xl font-extrabold text-yellow-400 mt-1 font-mono">31 进球</div>
        <div class="text-[11px] text-[#8ca0ba] mt-0.5">Player5 独挑 Opus 5.5 单刀杀穿全场</div>
      </div>
      <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md">
        <div class="text-[#8ca0ba] text-xs">🎯 参战智能体代表</div>
        <div class="text-xl sm:text-2xl font-extrabold text-cyan-400 mt-1 font-mono">15 支模型</div>
        <div class="text-[11px] text-[#8ca0ba] mt-0.5">Player5、Sol、Astra、Opus、Fable 等</div>
      </div>
    </section>

    <!-- 筛选过滤与搜索栏 -->
    <section class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md flex flex-col md:flex-row justify-between items-stretch md:items-center gap-3">
      <!-- 类别过滤 Pills -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 text-xs font-semibold">
        <button onclick="setFilter('all')" data-cat="all" class="cat-pill px-3 py-1.5 rounded-xl bg-blue-600 text-white shadow-sm whitespace-nowrap transition">
          全部对局 (11)
        </button>
        <button onclick="setFilter('15')" data-cat="15" class="cat-pill px-3 py-1.5 rounded-xl bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] whitespace-nowrap transition">
          15 阵营史诗混战 (2)
        </button>
        <button onclick="setFilter('8')" data-cat="8" class="cat-pill px-3 py-1.5 rounded-xl bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] whitespace-nowrap transition">
          8 阵营巅峰激战 (3)
        </button>
        <button onclick="setFilter('4')" data-cat="4" class="cat-pill px-3 py-1.5 rounded-xl bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] whitespace-nowrap transition">
          4 阵营战术对决 (4)
        </button>
        <button onclick="setFilter('few')" data-cat="few" class="cat-pill px-3 py-1.5 rounded-xl bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] whitespace-nowrap transition">
          2-3人 微操绝杀 (2)
        </button>
      </div>

      <!-- 搜索框 -->
      <div class="relative w-full md:w-72">
        <input type="text" id="search-input" oninput="handleSearch()"
               placeholder="搜索战役、智能体名称 (如 Sol, Player5)..." 
               class="w-full bg-[#0b1017] border border-[#26354a] focus:border-blue-500 rounded-xl px-3.5 py-1.5 text-xs text-[#f0f6fc] placeholder-[#64748b] outline-none transition">
        <span class="absolute right-3 top-2 text-xs text-[#64748b]">🔍</span>
      </div>
    </section>

    <!-- 比赛卡片网格列表 (响应式 1列 -> 2列 -> 3列) -->
    <main id="match-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {cards_html}
    </main>

    <!-- 空搜索状态 -->
    <div id="empty-state" class="hidden py-12 text-center text-[#8ca0ba] bg-[#151d28] border border-[#26354a] rounded-2xl">
      <div class="text-3xl mb-2">🔭</div>
      <div class="text-sm font-bold text-[#f0f6fc]">未找到符合条件的战役</div>
      <div class="text-xs mt-1">请尝试更换搜索关键词或选择“全部对局”</div>
    </div>

    <!-- 底部版权与说明 -->
    <footer class="text-center text-xs text-[#64748b] py-6 border-t border-[#1e2a3b]/50">
      <div>CTF 多智能体对战评测体系 · 官方裁判引擎 v1.0 · 逐回合动作级复盘</div>
      <div class="mt-1">每个战役均采用独立 HTML 构建，手机端超高速秒开，无额外数据流量浪费</div>
    </footer>

  </div>

  <script>
    let currentFilter = 'all';

    function setFilter(cat) {{
      currentFilter = cat;
      document.querySelectorAll('.cat-pill').forEach(btn => {{
        if (btn.dataset.cat === cat) {{
          btn.className = 'cat-pill px-3 py-1.5 rounded-xl bg-blue-600 text-white shadow-sm whitespace-nowrap transition';
        }} else {{
          btn.className = 'cat-pill px-3 py-1.5 rounded-xl bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] whitespace-nowrap transition';
        }}
      }});
      applyFilter();
    }}

    function handleSearch() {{
      applyFilter();
    }}

    function applyFilter() {{
      const query = (document.getElementById('search-input').value || '').toLowerCase().trim();
      const cards = document.querySelectorAll('.match-lobby-card');
      let visibleCount = 0;

      cards.forEach(c => {{
        const cat = c.dataset.category;
        const text = (c.dataset.search || '').toLowerCase();
        const matchCat = (currentFilter === 'all' || cat === currentFilter);
        const matchQuery = (!query || text.includes(query));

        if (matchCat && matchQuery) {{
          c.classList.remove('hidden');
          visibleCount++;
        }} else {{
          c.classList.add('hidden');
        }}
      }});

      const empty = document.getElementById('empty-state');
      if (empty) {{
        empty.classList.toggle('hidden', visibleCount > 0);
      }}
    }}
  </script>
</body>
</html>
"""


def generate_match_html(match_key, match_obj, meta_list):
    replay_json = json.dumps(match_obj['replay'], ensure_ascii=False)
    cfg_json = json.dumps({
        'key': match_obj['key'],
        'id': match_obj['id'],
        'tag': match_obj['tag'],
        'badge': match_obj['badge'],
        'title': match_obj['title'],
        'desc': match_obj['desc']
    }, ensure_ascii=False)
    all_options_html = ""
    for m in meta_list:
        sel = "selected" if m['key'] == match_key else ""
        all_options_html += f'<option value="{m["file"]}" {sel}>[{m["teams"]}人] {m["title"]}</option>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
  <title>{match_obj['title']} · CTF 独立动态复盘室</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b1017;
      --panel: #151d28;
      --line: #26354a;
      --ink: #f0f6fc;
      --muted: #8ca0ba;
    }}
    * {{ box-sizing: border-box; }}
    body {{ 
      background-color: var(--bg); 
      color: var(--ink); 
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      overflow-x: hidden;
    }}
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: #0b1017; }}
    ::-webkit-scrollbar-thumb {{ background: #26354a; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #3b82f6; }}

    .team-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.15s ease;
      background: #111822;
      border: 1px solid transparent;
    }}
    .team-row:hover {{
      background: #1e293b;
      border-color: #334155;
    }}
    .team-row.on {{
      background: #1e293b;
      border-color: #3b82f6;
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.25);
    }}
    .sw {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 6px;
      flex-shrink: 0;
    }}

    #celestial-canvas {{
      image-rendering: auto;
      touch-action: none;
    }}

    /* 全屏沉浸模式样式 (Desktop & Mobile) */
    #spectator-root.is-fullscreen {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      z-index: 9999;
      background: #050811;
      padding: 0;
      margin: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    #spectator-root.is-fullscreen .fs-hide {{
      display: none !important;
    }}
    #spectator-root.is-fullscreen #fs-top-bar {{
      display: flex !important;
    }}
    #spectator-root.is-fullscreen #fs-bottom-dock {{
      display: flex !important;
    }}
    #spectator-root.is-fullscreen #board-section {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 8px;
      max-height: calc(100vh - 100px);
    }}
    #spectator-root.is-fullscreen #board {{
      max-height: calc(100vh - 120px) !important;
      max-width: calc(100vh - 120px) !important;
      width: auto !important;
      height: auto !important;
    }}
  </style>
</head>
<body class="antialiased">

  <!-- 根容器 -->
  <div id="spectator-root" class="min-h-screen flex flex-col transition-all">

    <!-- 顶部导航栏 -->
    <header class="bg-[#151d28] border-b border-[#26354a] px-3 sm:px-6 py-2.5 flex items-center justify-between gap-3 flex-shrink-0 z-30">
      <div class="flex items-center gap-2.5 min-w-0">
        <a href="index.html" class="px-3 py-1.5 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-xs sm:text-sm font-bold text-[#f0f6fc] flex items-center gap-1.5 transition flex-shrink-0">
          <span>🏛️</span>
          <span>返回大厅</span>
        </a>
        <div class="min-w-0 flex items-center gap-2">
          <span class="hidden sm:inline-block px-2 py-0.5 rounded text-[11px] font-bold bg-[#111822] text-blue-400 border border-[#26354a] whitespace-nowrap">
            {match_obj['badge'].split('·')[0].strip()}
          </span>
          <h1 class="text-xs sm:text-sm font-bold text-[#f0f6fc] truncate">
            {match_obj['title']}
          </h1>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-shrink-0">
        <!-- 快速对局切换下拉菜单 -->
        <select onchange="location.href=this.value" class="hidden md:block bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] text-xs rounded-xl px-2.5 py-1.5 border border-[#26354a] outline-none max-w-[200px] truncate">
          {all_options_html}
        </select>

        <!-- 全屏按钮 -->
        <button id="btn-fullscreen" onclick="toggleFullscreen()" class="px-3 py-1.5 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-xs sm:text-sm font-bold text-cyan-400 flex items-center gap-1.5 transition shadow-sm">
          <span id="fs-icon">⛶</span>
          <span id="fs-text" class="hidden sm:inline">全屏模式</span>
        </button>
      </div>
    </header>

    <!-- 全屏模式浮动顶栏 (仅在全屏激活时显示) -->
    <div id="fs-top-bar" class="hidden absolute top-2 left-3 right-3 z-50 justify-between items-center bg-[#0b1017]/85 backdrop-blur-md px-4 py-2 rounded-xl border border-[#26354a] text-xs pointer-events-auto">
      <div class="flex items-center gap-2">
        <span class="text-yellow-400 font-bold">🏆 {match_obj['title']}</span>
        <span id="fs-hud-turn" class="font-mono text-cyan-400 font-bold">T0 / 400</span>
      </div>
      <button onclick="toggleFullscreen()" class="px-2.5 py-1 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/40 font-bold">
        ✕ 退出全屏
      </button>
    </div>

    <!-- 主展示区 (Desktop: 左右分栏 / Mobile: 纵向流式单屏) -->
    <div class="flex-1 max-w-7xl w-full mx-auto p-2.5 sm:p-5 lg:p-6 flex flex-col justify-between">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6 items-start">

        <!-- 左侧：棋盘对战主视界与播放器控制 (lg: 7列) -->
        <div id="left-spectator-col" class="lg:col-span-7 flex flex-col space-y-3.5">
          
          <!-- 棋盘卡片 -->
          <div id="board-section" class="relative bg-[#070b12] rounded-2xl p-2 sm:p-3 border border-[#26354a] shadow-2xl flex flex-col items-center justify-center overflow-hidden">
            <canvas id="board" class="w-full max-w-[620px] aspect-square block rounded-xl shadow-inner"></canvas>
            
            <!-- 棋盘悬浮角标 -->
            <div class="absolute top-4 left-4 pointer-events-none flex items-center gap-2">
              <span id="turns-counter" class="bg-[#0b1017]/85 backdrop-blur-md px-2.5 py-1 rounded-lg border border-[#26354a] text-xs font-mono font-bold text-cyan-400 shadow">
                回合 0 / 400
              </span>
              <span id="progress-percent" class="bg-[#0b1017]/85 backdrop-blur-md px-2 py-1 rounded-lg border border-[#26354a] text-[11px] font-mono text-[#8ca0ba]">
                0%
              </span>
            </div>

            <div id="board-leader-badge" class="absolute top-4 right-4 pointer-events-none bg-[#0b1017]/85 backdrop-blur-md px-2.5 py-1 rounded-lg border border-[#26354a] text-xs font-mono text-yellow-400 shadow">
              👑 实时领先: 计算中
            </div>
          </div>

          <!-- 播放控制器卡片 -->
          <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-3 sm:p-4 shadow-md space-y-2.5">
            <!-- 进度滑块 -->
            <div class="flex items-center gap-3">
              <input id="seek" type="range" min="0" max="400" value="0" class="flex-1 accent-blue-500 h-2 bg-[#0b1017] rounded-lg cursor-pointer">
              <span id="seek-value-badge" class="text-xs font-mono text-[#8ca0ba] w-12 text-right">T0</span>
            </div>

            <!-- 控制按钮行 -->
            <div class="flex flex-wrap items-center justify-between gap-2 pt-1">
              <div class="flex items-center gap-1.5 sm:gap-2">
                <button id="play" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 font-bold text-white text-xs sm:text-sm shadow-md transition flex items-center gap-1 min-w-[80px] justify-center">
                  <span>▶ 播放</span>
                </button>
                <button id="prev" class="px-3 py-2 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-xs font-bold text-[#f0f6fc] transition">
                  ◀ -1
                </button>
                <button id="next" class="px-3 py-2 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-xs font-bold text-[#f0f6fc] transition">
                  +1 ▶
                </button>
                <button onclick="go(0)" class="px-2.5 py-2 rounded-xl bg-[#111822] hover:bg-[#1e2a3b] border border-[#26354a] text-xs font-mono text-[#8ca0ba] transition">
                  ↺ 开局
                </button>
              </div>

              <div class="flex items-center gap-2">
                <!-- 播放速度选择 -->
                <div class="flex items-center gap-1 bg-[#111822] p-1 rounded-xl border border-[#26354a] text-xs font-mono">
                  <span class="text-[#64748b] px-1 hidden sm:inline">倍速:</span>
                  <select id="speed" class="bg-transparent text-cyan-400 font-bold outline-none cursor-pointer">
                    <option value="0.25">0.25x</option>
                    <option value="0.5">0.5x</option>
                    <option value="1" selected>1.0x</option>
                    <option value="2">2.0x</option>
                    <option value="4">4.0x</option>
                  </select>
                </div>

                <!-- 关键进球跳转 -->
                <select id="keys" class="bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] text-xs rounded-xl px-2.5 py-2 border border-[#26354a] outline-none max-w-[140px] sm:max-w-[180px] truncate">
                  <option value="">跳到进球/断旗…</option>
                </select>
              </div>
            </div>

            <!-- 图例与操作微操提示 -->
            <div class="text-[11px] text-[#8ca0ba] flex flex-wrap gap-x-3 gap-y-1 pt-1.5 border-t border-[#1e2a3b] font-mono">
              <span>● 角色 (附血条)</span>
              <span>⭕ 金环 = 携旗</span>
              <span>⭐ 星 = 地面旗</span>
              <span>⚡ 激光 = 攻击</span>
              <span>✖ 十字 = 阵亡</span>
              <span class="text-blue-400 hidden sm:inline">💡 空格=播放/暂停，左右键=逐回合微调</span>
            </div>
          </div>

        </div>

        <!-- 右侧 / 移动端下方：战术指挥中心多标签卡片系统 (lg: 5列) -->
        <div id="right-tactical-col" class="lg:col-span-5 flex flex-col space-y-3.5">
          
          <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-3 sm:p-4 shadow-md flex flex-col min-h-[460px]">
            
            <!-- 战术大厅多标签页导航 (适合手机与桌面) -->
            <div class="flex items-center justify-between border-b border-[#26354a] pb-2.5 mb-3 flex-shrink-0">
              <div class="flex items-center gap-1 bg-[#0b1017] p-1 rounded-xl border border-[#1e2a3b] text-xs font-bold overflow-x-auto">
                <button id="btn-tab-scores" onclick="switchMainTab('scores')" 
                  class="main-tab-btn px-2.5 py-1 rounded-lg transition bg-blue-600 text-white shadow-sm whitespace-nowrap">
                  📊 实时比分
                </button>
                <button id="btn-tab-celestial" onclick="switchMainTab('celestial')" 
                  class="main-tab-btn px-2.5 py-1 rounded-lg transition text-[#8ca0ba] hover:text-[#f0f6fc] whitespace-nowrap flex items-center gap-1">
                  <span>🌌 天体星图</span>
                  <span class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
                </button>
                <button id="btn-tab-events" onclick="switchMainTab('events')" 
                  class="main-tab-btn px-2.5 py-1 rounded-lg transition text-[#8ca0ba] hover:text-[#f0f6fc] whitespace-nowrap">
                  ⚔️ 战况事件
                </button>
                <button id="btn-tab-kda" onclick="switchMainTab('kda')" 
                  class="main-tab-btn px-2.5 py-1 rounded-lg transition text-[#8ca0ba] hover:text-[#f0f6fc] whitespace-nowrap">
                  📈 选手KDA
                </button>
              </div>

              <!-- 右侧附属小工具 -->
              <div id="tactical-sub-tools" class="flex items-center gap-1.5 text-[11px] font-mono">
                <!-- 天体图特有模式按钮 -->
                <div id="celestial-mode-box" class="hidden flex items-center gap-1">
                  <button onclick="toggleCelestialMode()" class="px-2 py-0.5 rounded bg-[#111822] text-cyan-400 border border-[#26354a] hover:bg-[#1a2536] transition flex items-center gap-1">
                    <span id="celestial-mode-icon">📈</span>
                    <span id="celestial-mode-text">星轨</span>
                  </button>
                </div>
                <button onclick="resetFocus()" title="重置队伍聚焦" class="px-1.5 py-0.5 rounded bg-[#111822] text-[#8ca0ba] hover:text-white border border-[#26354a] transition">
                  ↺ 全景
                </button>
              </div>
            </div>

            <!-- Tab 1: 实时比分面板 -->
            <div id="pane-tab-scores" class="flex-1 flex flex-col min-h-0 space-y-2">
              <div class="flex justify-between items-center text-[11px] text-[#8ca0ba] px-1 font-mono">
                <span>阵营列表 (点击队伍高亮追踪)</span>
                <span class="text-blue-400">实时得分降序</span>
              </div>
              <div id="teams-list" class="space-y-1.5 max-h-[360px] overflow-y-auto pr-1">
                <!-- 动态队伍条目 -->
              </div>
            </div>

            <!-- Tab 2: 天体走势星图面板 -->
            <div id="pane-tab-celestial" class="hidden flex-1 flex flex-col min-h-0 relative">
              <div class="relative w-full h-[290px] rounded-xl overflow-hidden bg-[#050811] border border-[#1e2a3b] shadow-inner">
                <canvas id="celestial-canvas" class="w-full h-full block cursor-crosshair"></canvas>
                
                <!-- 悬浮天体 HUD 提示器 -->
                <div id="celestial-hud" class="absolute pointer-events-none hidden transition-opacity duration-75 z-20 bg-[#0b111e]/95 backdrop-blur-md border border-[#3b82f6]/40 rounded-lg px-2.5 py-1.5 shadow-xl text-[11px] font-mono">
                  <div id="celestial-hud-title" class="font-bold text-[#f0f6fc] flex items-center gap-1.5 mb-0.5"></div>
                  <div id="celestial-hud-desc" class="text-[#8ca0ba] text-[10px]"></div>
                </div>

                <!-- 底部坐标系注释与扫描进度 -->
                <div class="absolute bottom-1.5 left-2 right-2 pointer-events-none flex justify-between items-center text-[10px] font-mono text-[#64748b]">
                  <span id="celestial-coord-hint">α: 回合 (Turn) · δ: 进球 (Score)</span>
                  <span id="celestial-scan-indicator" class="text-cyan-400/90 font-bold">T0 · 子午线校准</span>
                </div>
              </div>

              <!-- 天体图辅助说明 -->
              <div class="flex items-center justify-between text-[10px] text-[#8ca0ba] pt-2 px-1 font-mono">
                <span class="flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-cyan-400 inline-block"></span>
                  <span>星轨: 得分弧</span>
                  <span class="text-yellow-300 ml-1">⭐ 超新星: 进球时刻</span>
                </span>
                <span class="text-purple-400">点击星体/虚空跳转微调</span>
              </div>
            </div>

            <!-- Tab 3: 战场事件与指令流面板 -->
            <div id="pane-tab-events" class="hidden flex-1 flex flex-col min-h-0 space-y-3">
              <div>
                <div class="flex justify-between items-center text-[11px] text-[#8ca0ba] mb-1 font-mono">
                  <span>本回合交火事件 (Events)</span>
                  <span id="event-turn-badge" class="text-cyan-400">T0</span>
                </div>
                <div id="events-log" class="text-xs font-mono bg-[#0b1017] p-2.5 rounded-xl border border-[#26354a] h-[170px] overflow-y-auto space-y-1">
                  <!-- 动态事件 -->
                </div>
              </div>

              <div>
                <div class="flex justify-between items-center text-[11px] text-[#8ca0ba] mb-1 font-mono">
                  <span>智能体指令流 (Orders)</span>
                  <span id="focus-team-label">全员监控</span>
                </div>
                <div id="orders-log" class="text-xs font-mono bg-[#0b1017] p-2.5 rounded-xl border border-[#26354a] h-[120px] overflow-y-auto text-[#8ca0ba]">
                  <!-- 动态指令 -->
                </div>
              </div>
            </div>

            <!-- Tab 4: 选手 KDA 技术统计面板 -->
            <div id="pane-tab-kda" class="hidden flex-1 flex flex-col min-h-0 space-y-3">
              <!-- 高光之星简报 -->
              <div id="kda-highlight-cards" class="grid grid-cols-2 gap-2 text-xs">
                <!-- 动态卡片 -->
              </div>

              <!-- 实时 KDA 矩阵表 (移动端横向自适应) -->
              <div class="bg-[#0b1017] rounded-xl border border-[#26354a] overflow-x-auto max-h-[260px]">
                <table class="w-full text-left text-xs font-mono">
                  <thead class="bg-[#111822] text-[#8ca0ba] text-[10px] uppercase sticky top-0 border-b border-[#26354a]">
                    <tr>
                      <th class="py-2 px-2 text-center">#</th>
                      <th class="py-2 px-2.5">阵营</th>
                      <th class="py-2 px-2 text-right">进球</th>
                      <th class="py-2 px-2 text-right">转化率</th>
                      <th class="py-2 px-2 text-right">击杀</th>
                      <th class="py-2 px-2 text-right">阵亡</th>
                      <th class="py-2 px-2 text-right">KDA</th>
                    </tr>
                  </thead>
                  <tbody id="kda-tbody" class="divide-y divide-[#1e2a3b]/40 text-[#f0f6fc]">
                    <!-- 动态 KDA 行 -->
                  </tbody>
                </table>
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>

    <!-- 全屏模式下浮动的底部迷你控制坞 (仅在全屏激活时显示) -->
    <div id="fs-bottom-dock" class="hidden absolute bottom-3 left-4 right-4 z-50 justify-between items-center bg-[#0b1017]/90 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-[#26354a] pointer-events-auto">
      <div class="flex items-center gap-2">
        <button id="fs-play-btn" onclick="togglePlay()" class="px-3.5 py-1.5 rounded-xl bg-blue-600 font-bold text-white text-xs">
          ▶ 播放
        </button>
        <button onclick="go(i - 1)" class="px-2.5 py-1.5 rounded-xl bg-[#212e42] text-xs font-bold">◀</button>
        <button onclick="go(i + 1)" class="px-2.5 py-1.5 rounded-xl bg-[#212e42] text-xs font-bold">▶</button>
        <span id="fs-turn-label" class="font-mono text-cyan-400 font-bold text-xs ml-1">T0</span>
      </div>
      <div class="flex-1 max-w-md mx-4">
        <input id="fs-seek" type="range" min="0" max="400" value="0" oninput="go(+this.value)" class="w-full accent-blue-500 h-2 bg-[#111822] rounded-lg cursor-pointer">
      </div>
      <div class="flex items-center gap-2">
        <button onclick="toggleFullscreen()" class="px-3 py-1.5 rounded-xl bg-[#212e42] text-xs text-red-400 font-bold">
          ✕ 退出
        </button>
      </div>
    </div>

  </div>

  <script>
    const MATCH_DATA = {replay_json};
    const MATCH_CONFIG = {cfg_json};
    let R = MATCH_DATA;
    let CUM_STATS = [];

    const C = ['#ff6b7f','#5ab4ff','#7bd99b','#d7a2ff','#ffcb6b','#5fd9d4','#ff9fd0','#b5cc6e','#a9aeff','#f09c63','#e0e0e0','#8fb3c9','#e8d38a','#c98fa8','#8fd6b2'];
    const $ = id => document.getElementById(id);
    let cv, g;
    
    let i = 0, playing = false, last = 0, focus = -1;
    let currentMainTab = 'scores'; // 'scores' | 'celestial' | 'events' | 'kda'
    let celestialMode = 'timeline'; // 'timeline' | 'polar'
    let CELESTIAL_DATA = null;

    const MV = {{N:'上', S:'下', E:'右', W:'左', WAIT:'停'}};
    const AC = {{attack:'攻击', pickup:'拾旗', drop:'丢旗', wait:''}};
    const name = t => (R && R.names && R.names[t]) ? R.names[t] : ('阵营' + t);

    // 预解析对局逐回合技术统计
    function computeCumulativeStats(replayObj) {{
      const teams = replayObj.header.teams;
      const running = [];
      for (let t = 0; t < teams; t++) {{
        running.push({{
          team: t,
          name: (replayObj.names && replayObj.names[t]) ? replayObj.names[t] : ('阵营' + t),
          score: 0,
          pickups: 0,
          kills: 0,
          assists: 0,
          carrier_kills: 0,
          deaths: 0,
        }});
      }}

      const snapshots = [];
      for (let frameIdx = 0; frameIdx < replayObj.frames.length; frameIdx++) {{
        const f = replayObj.frames[frameIdx];
        for (const e of f.events) {{
          if (e.type === 'capture') {{
            if (running[e.team]) running[e.team].score++;
          }} else if (e.type === 'pickup') {{
            const tm = Math.floor(e.unit / 3);
            if (running[tm]) running[tm].pickups++;
          }} else if (e.type === 'death') {{
            const victimTeam = Math.floor(e.unit / 3);
            if (running[victimTeam]) running[victimTeam].deaths++;
            
            const attackers = e.by || [];
            const isCarrier = (e.flag !== null && e.flag !== undefined);
            if (attackers.length === 1) {{
              const killerTeam = Math.floor(attackers[0] / 3);
              if (running[killerTeam]) {{
                running[killerTeam].kills++;
                if (isCarrier) running[killerTeam].carrier_kills++;
              }}
            }} else if (attackers.length > 1) {{
              const primaryTeam = Math.floor(attackers[0] / 3);
              if (running[primaryTeam]) {{
                running[primaryTeam].kills++;
                if (isCarrier) running[primaryTeam].carrier_kills++;
              }}
              for (let a = 1; a < attackers.length; a++) {{
                const assistTeam = Math.floor(attackers[a] / 3);
                if (running[assistTeam]) running[assistTeam].assists++;
              }}
            }}
          }}
        }}

        const snapshot = running.map(st => {{
          const kdaVal = st.deaths > 0 ? ((st.kills + st.assists * 0.5) / st.deaths) : (st.kills + st.assists * 0.5);
          const rateVal = st.pickups > 0 ? ((st.score / st.pickups) * 100) : 0;
          return {{
            team: st.team,
            name: st.name,
            score: st.score,
            pickups: st.pickups,
            kills: st.kills,
            assists: st.assists,
            carrier_kills: st.carrier_kills,
            deaths: st.deaths,
            kda: parseFloat(kdaVal.toFixed(2)),
            capture_rate: parseFloat(rateVal.toFixed(1)),
          }};
        }});
        snapshot.sort((a, b) => b.score - a.score || b.kda - a.kda);
        snapshots.push(snapshot);
      }}
      return snapshots;
    }}

    // 生成固定天体微弱背景繁星
    function generateStarfield(count) {{
      const stars = [];
      let seed = 12345;
      const rnd = () => {{ seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }};
      for (let k = 0; k < count; k++) {{
        stars.push({{
          x: rnd(),
          y: rnd(),
          r: rnd() * 1.4 + 0.6,
          alpha: rnd() * 0.45 + 0.2,
          flicker: rnd() * Math.PI * 2,
          speed: rnd() * 0.04 + 0.02
        }});
      }}
      return stars;
    }}

    // 预解析对局的全周期比分走势与超新星进球时刻
    function prepareCelestialData(replayObj) {{
      if (!replayObj || !replayObj.frames) return null;
      const teams = replayObj.header.teams;
      const frames = replayObj.frames;
      const maxTurn = frames[frames.length - 1] ? frames[frames.length - 1].turn : 400;

      let maxScore = 1;
      const teamSeries = [];
      for (let t = 0; t < teams; t++) {{
        teamSeries.push({{
          team: t,
          name: (replayObj.names && replayObj.names[t]) ? replayObj.names[t] : ('阵营' + t),
          color: C[t % 15],
          points: [],
          captures: []
        }});
      }}

      for (let fIdx = 0; fIdx < frames.length; fIdx++) {{
        const f = frames[fIdx];
        const turn = f.turn;
        for (let t = 0; t < teams; t++) {{
          const sc = f.score[t];
          if (sc > maxScore) maxScore = sc;
          teamSeries[t].points.push({{ frame: fIdx, turn: turn, score: sc }});
        }}
        for (const e of f.events) {{
          if (e.type === 'capture') {{
            const t = e.team;
            if (teamSeries[t]) {{
              teamSeries[t].captures.push({{
                frame: fIdx,
                turn: turn,
                score: f.score[t],
                unit: e.unit,
                flag: e.flag
              }});
            }}
          }}
        }}
      }}

      return {{
        teams,
        maxTurn: Math.max(maxTurn, 100),
        maxScore: Math.max(maxScore, 3),
        teamSeries,
        starfield: generateStarfield(120)
      }};
    }}

    // 主标签切换
    function switchMainTab(tabKey) {{
      currentMainTab = tabKey;
      const tabs = ['scores', 'celestial', 'events', 'kda'];
      tabs.forEach(k => {{
        const btn = $('btn-tab-' + k);
        const pane = $('pane-tab-' + k);
        const isActive = (k === tabKey);
        if (btn) {{
          btn.className = isActive ?
            'main-tab-btn px-2.5 py-1 rounded-lg transition bg-blue-600 text-white shadow-sm whitespace-nowrap' :
            'main-tab-btn px-2.5 py-1 rounded-lg transition text-[#8ca0ba] hover:text-[#f0f6fc] whitespace-nowrap';
        }}
        if (pane) pane.classList.toggle('hidden', !isActive);
      }});

      const cBox = $('celestial-mode-box');
      if (cBox) cBox.classList.toggle('hidden', tabKey !== 'celestial');

      if (tabKey === 'celestial') {{
        resizeCelestialCanvas();
        renderCelestialChart();
      }}
    }}

    function toggleCelestialMode() {{
      celestialMode = (celestialMode === 'timeline' ? 'polar' : 'timeline');
      const icon = $('celestial-mode-icon');
      const text = $('celestial-mode-text');
      const hint = $('celestial-coord-hint');
      if (celestialMode === 'timeline') {{
        if (icon) icon.textContent = '📈';
        if (text) text.textContent = '星轨';
        if (hint) hint.textContent = 'α: 回合 (Turn) · δ: 进球 (Score)';
      }} else {{
        if (icon) icon.textContent = '🧭';
        if (text) text.textContent = '星盘';
        if (hint) hint.textContent = 'θ: 时序角方位 · r: 天体能级轨道';
      }}
      renderCelestialChart();
    }}

    function resetFocus() {{
      focus = -1;
      render();
    }}

    // 全屏模式控制
    function toggleFullscreen() {{
      const elem = $('spectator-root');
      const isFs = !!document.fullscreenElement || !!document.webkitFullscreenElement || elem.classList.contains('is-fullscreen');
      
      if (!isFs) {{
        if (elem.requestFullscreen) {{
          elem.requestFullscreen().catch(() => {{ fallbackFullscreen(); }});
        }} else if (elem.webkitRequestFullscreen) {{
          elem.webkitRequestFullscreen();
        }} else {{
          fallbackFullscreen();
        }}
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen();
        }} else if (document.webkitExitFullscreen) {{
          document.webkitExitFullscreen();
        }} else {{
          fallbackFullscreen();
        }}
      }}
    }}

    function fallbackFullscreen() {{
      const elem = $('spectator-root');
      elem.classList.toggle('is-fullscreen');
      updateFullscreenUI();
    }}

    function updateFullscreenUI() {{
      const elem = $('spectator-root');
      const isFs = !!document.fullscreenElement || !!document.webkitFullscreenElement || elem.classList.contains('is-fullscreen');
      const icon = $('fs-icon');
      const text = $('fs-text');
      if (isFs) {{
        elem.classList.add('is-fullscreen');
        if (icon) icon.textContent = '✕';
        if (text) text.textContent = '退出全屏';
      }} else {{
        elem.classList.remove('is-fullscreen');
        if (icon) icon.textContent = '⛶';
        if (text) text.textContent = '全屏模式';
      }}
      setTimeout(() => {{
        render();
        if (currentMainTab === 'celestial') {{
          resizeCelestialCanvas();
          renderCelestialChart();
        }}
      }}, 80);
    }}

    document.addEventListener('fullscreenchange', updateFullscreenUI);
    document.addEventListener('webkitfullscreenchange', updateFullscreenUI);

    // 天体图画布大小适配
    function resizeCelestialCanvas() {{
      const cv = $('celestial-canvas');
      if (!cv) return;
      const rect = cv.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const w = Math.floor(rect.width);
      const h = Math.floor(rect.height);
      if (w <= 0 || h <= 0) return;
      if (cv.width !== w * dpr || cv.height !== h * dpr) {{
        cv.width = w * dpr;
        cv.height = h * dpr;
      }}
    }}

    function drawSupernova(ctx, x, y, color, size, pulse) {{
      ctx.save();
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = color;
      ctx.shadowBlur = pulse ? 12 : 6;

      const spike = size * 2.2;
      const inner = size * 0.45;
      ctx.beginPath();
      for (let k = 0; k < 8; k++) {{
        const a = (Math.PI / 4) * k;
        const r = (k % 2 === 0) ? spike : inner;
        const px = x + r * Math.cos(a);
        const py = y + r * Math.sin(a);
        if (k === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }}
      ctx.closePath();
      ctx.fill();

      if (pulse) {{
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(x, y, size * 2.8, 0, Math.PI * 2);
        ctx.stroke();
      }}
      ctx.restore();
    }}

    function renderCelestialChart() {{
      const cv = $('celestial-canvas');
      if (!cv || !R || !R.frames || !R.frames[i]) return;
      const g = cv.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const W = cv.width / dpr;
      const H = cv.height / dpr;
      if (W <= 0 || H <= 0) return;

      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.clearRect(0, 0, W, H);

      if (!CELESTIAL_DATA) {{
        CELESTIAL_DATA = prepareCelestialData(R);
      }}
      if (!CELESTIAL_DATA) return;

      const curFrame = R.frames[i];
      const curTurn = curFrame ? curFrame.turn : 0;
      const maxTurn = CELESTIAL_DATA.maxTurn;
      const maxScore = CELESTIAL_DATA.maxScore;

      const scanInd = $('celestial-scan-indicator');
      if (scanInd) {{
        scanInd.textContent = `T${{curTurn}} / ${{maxTurn}} · ${{celestialMode === 'timeline' ? '天球子午线' : '极轨测角仪'}}`;
      }}

      if (celestialMode === 'timeline') {{
        renderCelestialTimeline(g, W, H, curTurn, maxTurn, maxScore);
      }} else {{
        renderCelestialPolar(g, W, H, curTurn, maxTurn, maxScore);
      }}
    }}

    function renderCelestialTimeline(g, W, H, curTurn, maxTurn, maxScore) {{
      const padL = 34, padR = 20, padT = 18, padB = 26;
      const plotW = W - padL - padR;
      const plotH = H - padT - padB;
      const mapX = t => padL + (t / maxTurn) * plotW;
      const mapY = s => padT + (1 - s / maxScore) * plotH;

      // 1. 深空渐变背景
      const grad = g.createRadialGradient(W * 0.65, H * 0.35, 15, W * 0.5, H * 0.5, Math.max(W, H));
      grad.addColorStop(0, '#0d1527');
      grad.addColorStop(0.45, '#070c17');
      grad.addColorStop(1, '#03050a');
      g.fillStyle = grad;
      g.fillRect(0, 0, W, H);

      // 2. 背景微弱繁星闪烁
      if (CELESTIAL_DATA.starfield) {{
        for (let k = 0; k < CELESTIAL_DATA.starfield.length; k++) {{
          const st = CELESTIAL_DATA.starfield[k];
          const pulse = 0.4 + 0.6 * Math.sin(st.flicker + i * st.speed);
          g.fillStyle = `rgba(200, 225, 255, ${{st.alpha * pulse}})`;
          g.fillRect(st.x * W, st.y * H, st.r, st.r);
        }}
      }}

      // 3. 水平得分刻度线
      g.save();
      g.setLineDash([3, 4]);
      g.lineWidth = 1;
      for (let s = 0; s <= maxScore; s++) {{
        const y = mapY(s);
        g.strokeStyle = (s === 0) ? 'rgba(56, 189, 248, 0.22)' : 'rgba(56, 189, 248, 0.08)';
        g.beginPath();
        g.moveTo(padL, y);
        g.lineTo(W - padR, y);
        g.stroke();

        g.font = '9px monospace';
        g.fillStyle = (s === 0) ? '#64748b' : '#8ca0ba';
        g.textAlign = 'right';
        g.textBaseline = 'middle';
        g.fillText(s, padL - 6, y);
      }}

      // 垂直回合刻度线
      const turnStep = maxTurn > 250 ? 100 : (maxTurn > 100 ? 50 : 25);
      g.setLineDash([2, 4]);
      g.strokeStyle = 'rgba(56, 189, 248, 0.07)';
      g.fillStyle = '#64748b';
      g.font = '9px monospace';
      g.textAlign = 'center';
      g.textBaseline = 'top';
      for (let t = 0; t <= maxTurn; t += turnStep) {{
        const x = mapX(t);
        g.beginPath();
        g.moveTo(x, padT);
        g.lineTo(x, H - padB);
        g.stroke();
        g.fillText('T' + t, x, H - padB + 5);
      }}
      g.restore();

      // 4. 各阵营星轨轨迹
      const sortedTeams = [...CELESTIAL_DATA.teamSeries].sort((a, b) => {{
        if (a.team === focus) return 1;
        if (b.team === focus) return -1;
        return (R.frames[i].score[a.team] || 0) - (R.frames[i].score[b.team] || 0);
      }});

      sortedTeams.forEach(tm => {{
        const isTarget = (focus === -1 || focus === tm.team);
        const alpha = isTarget ? 1 : 0.16;
        const lineWidth = (focus === tm.team) ? 2.6 : (isTarget ? 1.6 : 1.0);

        // 未来星轨虚线
        if (isTarget) {{
          g.save();
          g.strokeStyle = tm.color;
          g.globalAlpha = alpha * 0.22;
          g.lineWidth = lineWidth * 0.85;
          g.setLineDash([2, 4]);
          g.beginPath();
          for (let k = 0; k < tm.points.length; k++) {{
            const pt = tm.points[k];
            const px = mapX(pt.turn);
            const py = mapY(pt.score);
            if (k === 0) g.moveTo(px, py);
            else g.lineTo(px, py);
          }}
          g.stroke();
          g.restore();
        }}

        // 当前推演实线
        g.save();
        g.strokeStyle = tm.color;
        g.globalAlpha = alpha;
        g.lineWidth = lineWidth;
        g.setLineDash([]);
        if (isTarget && focus === tm.team) {{
          g.shadowColor = tm.color;
          g.shadowBlur = 8;
        }}
        g.beginPath();
        let ptsCount = 0;
        for (let k = 0; k <= i && k < tm.points.length; k++) {{
          const pt = tm.points[k];
          const px = mapX(pt.turn);
          const py = mapY(pt.score);
          if (k === 0) g.moveTo(px, py);
          else g.lineTo(px, py);
          ptsCount++;
        }}
        if (ptsCount > 0) g.stroke();
        g.restore();

        // 进球超新星 ⭐
        tm.captures.forEach(cap => {{
          const capX = mapX(cap.turn);
          const capY = mapY(cap.score);
          const hasOccurred = (cap.frame <= i);
          if (hasOccurred) {{
            const isPulse = (i >= cap.frame && i <= cap.frame + 5);
            g.globalAlpha = isTarget ? 1 : 0.2;
            drawSupernova(g, capX, capY, tm.color, isPulse ? 6.5 : 4.5, isPulse);
          }} else if (isTarget) {{
            g.save();
            g.strokeStyle = tm.color;
            g.globalAlpha = alpha * 0.25;
            g.beginPath();
            g.arc(capX, capY, 2.5, 0, Math.PI * 2);
            g.stroke();
            g.restore();
          }}
        }});
      }});

      // 5. 扫描子午线
      const scanX = mapX(curTurn);
      g.save();
      const beamGrad = g.createLinearGradient(scanX, padT, scanX, H - padB);
      beamGrad.addColorStop(0, 'rgba(56, 189, 248, 0.05)');
      beamGrad.addColorStop(0.5, 'rgba(56, 189, 248, 0.7)');
      beamGrad.addColorStop(1, 'rgba(56, 189, 248, 0.05)');
      g.strokeStyle = beamGrad;
      g.lineWidth = 1.5;
      g.beginPath();
      g.moveTo(scanX, padT - 4);
      g.lineTo(scanX, H - padB + 4);
      g.stroke();
      g.fillStyle = '#38bdf8';
      g.beginPath();
      g.arc(scanX, padT - 4, 2.5, 0, Math.PI * 2);
      g.fill();
      g.restore();

      // 6. 子午线行星球
      sortedTeams.forEach(tm => {{
        const curScore = R.frames[i].score[tm.team];
        const orbX = scanX;
        const orbY = mapY(curScore);
        const isTargetTm = (focus === -1 || focus === tm.team);

        g.save();
        g.globalAlpha = isTargetTm ? 1 : 0.2;
        if (focus === tm.team) {{
          g.strokeStyle = '#38bdf8';
          g.lineWidth = 1;
          g.beginPath();
          g.arc(orbX, orbY, 7.5, 0, Math.PI * 2);
          g.stroke();
          g.strokeRect(orbX - 9, orbY - 9, 18, 18);
        }}
        g.fillStyle = tm.color;
        g.shadowColor = tm.color;
        g.shadowBlur = 8;
        g.beginPath();
        g.arc(orbX, orbY, focus === tm.team ? 4.8 : 3.2, 0, Math.PI * 2);
        g.fill();
        g.restore();
      }});
    }}

    function renderCelestialPolar(g, W, H, curTurn, maxTurn, maxScore) {{
      const cx = W / 2;
      const cy = (H - 8) / 2;
      const maxRadius = Math.min(W - 40, H - 36) / 2;
      const minRadius = 22;

      const mapPolar = (turn, score) => {{
        const angle = -Math.PI / 2 + (turn / maxTurn) * (Math.PI * 2);
        const r = minRadius + (score / maxScore) * (maxRadius - minRadius);
        return {{ x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), angle, r }};
      }};

      const grad = g.createRadialGradient(cx, cy, 10, cx, cy, maxRadius + 20);
      grad.addColorStop(0, '#0e182f');
      grad.addColorStop(0.5, '#070c17');
      grad.addColorStop(1, '#03050a');
      g.fillStyle = grad;
      g.fillRect(0, 0, W, H);

      if (CELESTIAL_DATA.starfield) {{
        for (let k = 0; k < CELESTIAL_DATA.starfield.length; k++) {{
          const st = CELESTIAL_DATA.starfield[k];
          const pulse = 0.4 + 0.6 * Math.sin(st.flicker + i * st.speed);
          g.fillStyle = `rgba(200, 225, 255, ${{st.alpha * pulse}})`;
          g.fillRect(st.x * W, st.y * H, st.r, st.r);
        }}
      }}

      g.save();
      g.lineWidth = 1;
      for (let s = 0; s <= maxScore; s++) {{
        const r = minRadius + (s / maxScore) * (maxRadius - minRadius);
        g.strokeStyle = (s === 0) ? 'rgba(56, 189, 248, 0.25)' : 'rgba(56, 189, 248, 0.08)';
        g.setLineDash([2, 3]);
        g.beginPath();
        g.arc(cx, cy, r, 0, Math.PI * 2);
        g.stroke();

        g.font = '8px monospace';
        g.fillStyle = '#64748b';
        g.textAlign = 'center';
        g.textBaseline = 'middle';
        g.fillText('δ' + s, cx, cy - r + 7);
      }}

      g.setLineDash([2, 4]);
      g.strokeStyle = 'rgba(56, 189, 248, 0.08)';
      for (let ang = 0; ang < Math.PI * 2; ang += Math.PI / 2) {{
        g.beginPath();
        g.moveTo(cx, cy);
        g.lineTo(cx + maxRadius * Math.cos(ang), cy + maxRadius * Math.sin(ang));
        g.stroke();
      }}
      g.restore();

      g.save();
      const coreGrad = g.createRadialGradient(cx, cy, 0, cx, cy, minRadius);
      coreGrad.addColorStop(0, '#38bdf8');
      coreGrad.addColorStop(0.4, 'rgba(59, 130, 246, 0.35)');
      coreGrad.addColorStop(1, 'transparent');
      g.fillStyle = coreGrad;
      g.beginPath();
      g.arc(cx, cy, minRadius, 0, Math.PI * 2);
      g.fill();
      g.font = '10px monospace';
      g.fillStyle = '#ffffff';
      g.textAlign = 'center';
      g.textBaseline = 'middle';
      g.fillText('✦', cx, cy);
      g.restore();

      const sortedTeams = [...CELESTIAL_DATA.teamSeries].sort((a, b) => {{
        if (a.team === focus) return 1;
        if (b.team === focus) return -1;
        return (R.frames[i].score[a.team] || 0) - (R.frames[i].score[b.team] || 0);
      }});

      sortedTeams.forEach(tm => {{
        const isTarget = (focus === -1 || focus === tm.team);
        const alpha = isTarget ? 1 : 0.16;
        const lineWidth = (focus === tm.team) ? 2.5 : (isTarget ? 1.5 : 1.0);

        if (isTarget) {{
          g.save();
          g.strokeStyle = tm.color;
          g.globalAlpha = alpha * 0.22;
          g.lineWidth = lineWidth * 0.85;
          g.setLineDash([2, 4]);
          g.beginPath();
          for (let k = 0; k < tm.points.length; k++) {{
            const pt = tm.points[k];
            const pos = mapPolar(pt.turn, pt.score);
            if (k === 0) g.moveTo(pos.x, pos.y);
            else g.lineTo(pos.x, pos.y);
          }}
          g.stroke();
          g.restore();
        }}

        g.save();
        g.strokeStyle = tm.color;
        g.globalAlpha = alpha;
        g.lineWidth = lineWidth;
        g.setLineDash([]);
        if (isTarget && focus === tm.team) {{
          g.shadowColor = tm.color;
          g.shadowBlur = 8;
        }}
        g.beginPath();
        let ptsCount = 0;
        for (let k = 0; k <= i && k < tm.points.length; k++) {{
          const pt = tm.points[k];
          const pos = mapPolar(pt.turn, pt.score);
          if (k === 0) g.moveTo(pos.x, pos.y);
          else g.lineTo(pos.x, pos.y);
          ptsCount++;
        }}
        if (ptsCount > 0) g.stroke();
        g.restore();

        tm.captures.forEach(cap => {{
          const pos = mapPolar(cap.turn, cap.score);
          const hasOccurred = (cap.frame <= i);
          if (hasOccurred) {{
            const isPulse = (i >= cap.frame && i <= cap.frame + 5);
            g.globalAlpha = isTarget ? 1 : 0.2;
            drawSupernova(g, pos.x, pos.y, tm.color, isPulse ? 6.5 : 4.5, isPulse);
          }} else if (isTarget) {{
            g.save();
            g.strokeStyle = tm.color;
            g.globalAlpha = alpha * 0.25;
            g.beginPath();
            g.arc(pos.x, pos.y, 2.5, 0, Math.PI * 2);
            g.stroke();
            g.restore();
          }}
        }});
      }});

      const curAngle = -Math.PI / 2 + (curTurn / maxTurn) * (Math.PI * 2);
      g.save();
      g.strokeStyle = 'rgba(56, 189, 248, 0.7)';
      g.lineWidth = 1.5;
      g.beginPath();
      g.moveTo(cx, cy);
      g.lineTo(cx + (maxRadius + 6) * Math.cos(curAngle), cy + (maxRadius + 6) * Math.sin(curAngle));
      g.stroke();
      g.fillStyle = '#38bdf8';
      g.beginPath();
      g.arc(cx + (maxRadius + 6) * Math.cos(curAngle), cy + (maxRadius + 6) * Math.sin(curAngle), 2.5, 0, Math.PI * 2);
      g.fill();
      g.restore();

      sortedTeams.forEach(tm => {{
        const curScore = R.frames[i].score[tm.team];
        const r = minRadius + (curScore / maxScore) * (maxRadius - minRadius);
        const orbX = cx + r * Math.cos(curAngle);
        const orbY = cy + r * Math.sin(curAngle);
        const isTargetTm = (focus === -1 || focus === tm.team);

        g.save();
        g.globalAlpha = isTargetTm ? 1 : 0.2;
        if (focus === tm.team) {{
          g.strokeStyle = '#38bdf8';
          g.lineWidth = 1;
          g.beginPath();
          g.arc(orbX, orbY, 7.5, 0, Math.PI * 2);
          g.stroke();
        }}
        g.fillStyle = tm.color;
        g.shadowColor = tm.color;
        g.shadowBlur = 8;
        g.beginPath();
        g.arc(orbX, orbY, focus === tm.team ? 4.8 : 3.2, 0, Math.PI * 2);
        g.fill();
        g.restore();
      }});
    }}

    function setupCelestialEventListeners() {{
      const cv = $('celestial-canvas');
      if (!cv) return;

      cv.addEventListener('mousemove', handleCelestialHover);
      cv.addEventListener('mouseleave', () => {{
        const hud = $('celestial-hud');
        if (hud) hud.classList.add('hidden');
      }});
      cv.addEventListener('click', handleCelestialClick);

      window.addEventListener('resize', () => {{
        if (currentMainTab === 'celestial') {{
          resizeCelestialCanvas();
          renderCelestialChart();
        }}
      }});
    }}

    function handleCelestialHover(e) {{
      const cv = $('celestial-canvas');
      if (!cv || !CELESTIAL_DATA || !R || !R.frames) return;
      const rect = cv.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let hoverTurn = 0;
      let closestTeam = 0;

      if (celestialMode === 'timeline') {{
        const padL = 34, padR = 20, padT = 18, padB = 26;
        const plotW = rect.width - padL - padR;
        const plotH = rect.height - padT - padB;
        if (mx < padL - 8 || mx > rect.width - padR + 8 || my < padT - 8 || my > rect.height - padB + 8) {{
          $('celestial-hud')?.classList.add('hidden');
          return;
        }}
        const ratio = Math.max(0, Math.min(1, (mx - padL) / plotW));
        hoverTurn = Math.round(ratio * CELESTIAL_DATA.maxTurn);
        const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
        const frameAtT = R.frames[fIdx];
        if (!frameAtT) return;

        let minDy = Infinity;
        for (let t = 0; t < R.header.teams; t++) {{
          const sc = frameAtT.score[t];
          const py = padT + (1 - sc / CELESTIAL_DATA.maxScore) * plotH;
          const dy = Math.abs(my - py);
          if (dy < minDy) {{
            minDy = dy;
            closestTeam = t;
          }}
        }}
      }} else {{
        const cx = rect.width / 2;
        const cy = (rect.height - 8) / 2;
        const dx = mx - cx;
        const dy = my - cy;
        let ang = Math.atan2(dy, dx) + Math.PI / 2;
        if (ang < 0) ang += Math.PI * 2;
        const ratio = ang / (Math.PI * 2);
        hoverTurn = Math.round(ratio * CELESTIAL_DATA.maxTurn);
        const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
        const frameAtT = R.frames[fIdx];
        if (!frameAtT) return;

        const r = Math.sqrt(dx * dx + dy * dy);
        const maxRadius = Math.min(rect.width - 40, rect.height - 36) / 2;
        const minRadius = 22;
        let minDr = Infinity;
        for (let t = 0; t < R.header.teams; t++) {{
          const sc = frameAtT.score[t];
          const tr = minRadius + (sc / CELESTIAL_DATA.maxScore) * (maxRadius - minRadius);
          const dr = Math.abs(r - tr);
          if (dr < minDr) {{
            minDr = dr;
            closestTeam = t;
          }}
        }}
      }}

      const ratio = hoverTurn / CELESTIAL_DATA.maxTurn;
      const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
      const frameAtT = R.frames[fIdx];
      if (!frameAtT) return;

      const hud = $('celestial-hud');
      const title = $('celestial-hud-title');
      const desc = $('celestial-hud-desc');
      if (!hud || !title || !desc) return;

      const tmColor = C[closestTeam % 15];
      const tmName = name(closestTeam);
      const score = frameAtT.score[closestTeam];
      const capNear = CELESTIAL_DATA.teamSeries[closestTeam]?.captures.find(c => Math.abs(c.turn - frameAtT.turn) <= 2);

      title.innerHTML = `
        <span class="w-2.5 h-2.5 rounded-full inline-block" style="background:${{tmColor}}"></span>
        <span>${{tmName}}</span>
        <span class="text-cyan-400 font-mono text-[10px]">T${{frameAtT.turn}}</span>
      `;

      desc.innerHTML = `
        <div class="flex items-center justify-between gap-3">
          <span>当前得分:</span>
          <b class="text-emerald-400 font-bold">${{score}} 进球</b>
        </div>
        ${{capNear ? '<div class="text-yellow-400 font-bold mt-1 flex items-center gap-1"><span>⭐</span><span>交旗进球时刻!</span></div>' : ''}}
      `;

      const hudW = 160;
      let left = mx - hudW / 2;
      if (left < 8) left = 8;
      if (left + hudW > rect.width - 8) left = rect.width - hudW - 8;
      let top = my - 62;
      if (top < 8) top = my + 14;

      hud.style.left = `${{left}}px`;
      hud.style.top = `${{top}}px`;
      hud.classList.remove('hidden');
    }}

    function handleCelestialClick(e) {{
      const cv = $('celestial-canvas');
      if (!cv || !CELESTIAL_DATA || !R || !R.frames) return;
      const rect = cv.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let ratio = 0;
      let clickedTeam = -1;

      if (celestialMode === 'timeline') {{
        const padL = 34, padR = 20, padT = 18, padB = 26;
        const plotW = rect.width - padL - padR;
        const plotH = rect.height - padT - padB;
        if (mx >= padL - 8 && mx <= rect.width - padR + 8) {{
          ratio = Math.max(0, Math.min(1, (mx - padL) / plotW));
        }}
        const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
        const frameAtT = R.frames[fIdx];
        if (frameAtT) {{
          let minDy = Infinity;
          for (let t = 0; t < R.header.teams; t++) {{
            const sc = frameAtT.score[t];
            const py = padT + (1 - sc / CELESTIAL_DATA.maxScore) * plotH;
            const dy = Math.abs(my - py);
            if (dy < 18 && dy < minDy) {{
              minDy = dy;
              clickedTeam = t;
            }}
          }}
        }}
      }} else {{
        const cx = rect.width / 2;
        const cy = (rect.height - 8) / 2;
        const dx = mx - cx;
        const dy = my - cy;
        let ang = Math.atan2(dy, dx) + Math.PI / 2;
        if (ang < 0) ang += Math.PI * 2;
        ratio = ang / (Math.PI * 2);

        const r = Math.sqrt(dx * dx + dy * dy);
        const maxRadius = Math.min(rect.width - 40, rect.height - 36) / 2;
        const minRadius = 22;
        const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
        const frameAtT = R.frames[fIdx];
        if (frameAtT) {{
          let minDr = Infinity;
          for (let t = 0; t < R.header.teams; t++) {{
            const sc = frameAtT.score[t];
            const tr = minRadius + (sc / CELESTIAL_DATA.maxScore) * (maxRadius - minRadius);
            const dr = Math.abs(r - tr);
            if (dr < 18 && dr < minDr) {{
              minDr = dr;
              clickedTeam = t;
            }}
          }}
        }}
      }}

      const targetFrame = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
      go(targetFrame);

      if (clickedTeam >= 0) {{
        focus = (focus === clickedTeam ? -1 : clickedTeam);
      }}
      render();
    }}

    // 渲染实时动态 KDA 表格与高能数据卡片
    function renderKdaTable(stats) {{
      const tbody = $('kda-tbody');
      const cards = $('kda-highlight-cards');
      if (!stats || !stats.length) return;

      const topScore = [...stats].sort((a,b) => b.score - a.score)[0];
      const topKills = [...stats].sort((a,b) => b.kills - a.kills)[0];
      const topCK = [...stats].sort((a,b) => b.carrier_kills - a.carrier_kills)[0];
      const topKDA = [...stats].sort((a,b) => b.kda - a.kda)[0];

      if (cards) {{
        cards.innerHTML = `
          <div class="p-2.5 bg-[#111822] rounded-xl border border-[#26354a]">
            <div class="text-[#8ca0ba] text-[10px] flex justify-between">
              <span>👑 实时得分王</span>
              <span class="text-emerald-400 font-bold">${{topScore.score}} 进球</span>
            </div>
            <div class="text-xs font-bold text-yellow-400 mt-1 truncate">${{topScore.name}}</div>
          </div>
          <div class="p-2.5 bg-[#111822] rounded-xl border border-[#26354a]">
            <div class="text-[#8ca0ba] text-[10px] flex justify-between">
              <span>⚔️ 实时杀神</span>
              <span class="text-red-400 font-bold">${{topKills.kills}} 击杀</span>
            </div>
            <div class="text-xs font-bold text-red-400 mt-1 truncate">${{topKills.name}}</div>
          </div>
        `;
      }}

      if (tbody) {{
        tbody.innerHTML = stats.map((st, rank) => {{
          const color = C[st.team % 15];
          const isTop = (rank === 0);
          return `
            <tr class="hover:bg-[#16202e] transition ${{isTop ? 'bg-blue-500/5' : ''}}">
              <td class="py-1.5 px-2 text-center font-bold ${{rank < 3 ? 'text-yellow-400' : 'text-[#8ca0ba]'}}">${{rank + 1}}</td>
              <td class="py-1.5 px-2.5 font-bold flex items-center gap-1.5 truncate">
                <span class="w-2 h-2 rounded-full inline-block flex-shrink-0" style="background:${{color}}"></span>
                <span class="${{isTop ? 'text-blue-400' : 'text-[#f0f6fc]'}} truncate">${{st.name}}</span>
              </td>
              <td class="py-1.5 px-2 text-right font-bold text-emerald-400">${{st.score}}</td>
              <td class="py-1.5 px-2 text-right text-cyan-400">${{st.capture_rate}}%</td>
              <td class="py-1.5 px-2 text-right font-bold text-red-400">${{st.kills}}</td>
              <td class="py-1.5 px-2 text-right text-[#8ca0ba]">${{st.deaths}}</td>
              <td class="py-1.5 px-2 text-right font-bold ${{st.kda >= 1.5 ? 'text-emerald-400' : 'text-[#8ca0ba]'}}">${{st.kda}}</td>
            </tr>
          `;
        }}).join('');
      }}
    }}

    function ev(e) {{
      switch(e.type) {{
        case 'capture': return `🏆 ${{name(e.team)}} 成功交旗进球！(角色 ${{e.unit}}，旗 ${{e.flag}})`;
        case 'pickup':  return `🚩 角色 ${{e.unit}} [${{name(Math.floor(e.unit/3))}}] 拾取旗帜 ${{e.flag}}`;
        case 'drop':    return `放下旗帜 ${{e.flag}} (角色 ${{e.unit}})`;
        case 'death':   return `💀 角色 ${{e.unit}} [${{name(Math.floor(e.unit/3))}}] 阵亡${{e.flag!==null?' (掉落旗'+e.flag+')':''}}${{e.by && e.by.length ? ' 击杀: ' + e.by.join('、') : ''}}`;
        case 'attack':  return `⚔️ 角色 ${{e.unit}} 攻击 角色 ${{e.target}}`;
        case 'respawn': return `🔄 角色 ${{e.unit}} 基地重生`;
        case 'return':  return `⏳ 旗帜 ${{e.flag}} 刷新回位`;
        default: return JSON.stringify(e);
      }}
    }}

    function render() {{
      if (!cv) cv = $('board');
      if (!g) g = cv.getContext('2d');
      if (!R || !R.frames || !R.frames[i]) return;

      const f = R.frames[i], H = R.header, n = H.size, s = Math.max(8, Math.floor(640 / n));
      cv.width = cv.height = n * s;

      // 地图与网格
      for(let y = 0; y < n; y++) {{
        for(let x = 0; x < n; x++) {{
          g.fillStyle = H.map[y][x] === '#' ? '#2b394d' : ((x + y) % 2 ? '#121822' : '#151e2b');
          g.fillRect(x * s, y * s, s, s);
        }}
      }}

      // 基地光标
      H.bases.forEach((bs, t) => {{
        g.fillStyle = C[t % 15] + '22';
        bs.forEach(([x, y]) => g.fillRect(x * s, y * s, s, s));
      }});

      // 旗帜
      f.flags.forEach((fl, idx) => {{
        if (!fl.pos) return;
        const [x, y] = fl.pos;
        star(x * s + s / 2, y * s + s / 2, s * 0.42, '#ffd700');
        g.font = `bold ${{Math.max(8, Math.floor(s * 0.35))}}px monospace`;
        g.fillStyle = '#000000';
        g.textAlign = 'center';
        g.textBaseline = 'middle';
        g.fillText(idx, x * s + s / 2, y * s + s / 2);
      }});

      // 攻击轨迹激光
      f.events.forEach(e => {{
        if (e.type === 'attack') {{
          const u1 = f.units.find(u => u.id === e.unit);
          const u2 = f.units.find(u => u.id === e.target);
          if (u1 && u2 && u1.pos && u2.pos) {{
            g.strokeStyle = '#f87171';
            g.lineWidth = 1.5;
            g.beginPath();
            g.moveTo(u1.pos[0] * s + s / 2, u1.pos[1] * s + s / 2);
            g.lineTo(u2.pos[0] * s + s / 2, u2.pos[1] * s + s / 2);
            g.stroke();
          }}
        }}
      }});

      // 单位与血条
      for(const u of f.units) {{
        if (!u.pos) continue;
        const t = Math.floor(u.id / 3);
        const [x, y] = u.pos, cx = x * s + s / 2, cy = y * s + s / 2;
        g.globalAlpha = (focus < 0 || focus === t) ? 1 : 0.22;

        if (u.flag !== null) {{
          g.strokeStyle = '#ffd700';
          g.lineWidth = 2.5;
          g.beginPath();
          g.arc(cx, cy, s * 0.46, 0, Math.PI * 2);
          g.stroke();
        }}

        g.fillStyle = C[t % 15];
        g.beginPath();
        g.arc(cx, cy, s * 0.36, 0, Math.PI * 2);
        g.fill();

        g.fillStyle = '#000000';
        g.font = `bold ${{Math.max(7, Math.floor(s * 0.38))}}px sans-serif`;
        g.textAlign = 'center';
        g.textBaseline = 'middle';
        g.fillText(u.id, cx, cy + 0.5);

        // 血条
        g.fillStyle = '#0b1017';
        g.fillRect(x * s + 1, y * s + 1, s - 2, 2);
        g.fillStyle = u.hp > 50 ? '#34d399' : '#f87171';
        g.fillRect(x * s + 1, y * s + 1, (s - 2) * (u.hp / H.rules.hp), 2);
      }}
      g.globalAlpha = 1;

      // 状态同步
      const maxTurn = (R.frames[R.frames.length - 1] ? R.frames[R.frames.length - 1].turn : 400);
      $('turns-counter').textContent = `回合 ${{f.turn}} / ${{maxTurn}}`;
      $('seek').value = i;
      $('seek-value-badge').textContent = `T${{f.turn}}`;
      $('progress-percent').textContent = Math.round((i / (R.frames.length - 1)) * 100) + '%';
      $('event-turn-badge').textContent = `T${{f.turn}}`;

      // 全屏 HUD 同步
      const fsTurn = $('fs-hud-turn');
      if (fsTurn) fsTurn.textContent = `T${{f.turn}} / ${{maxTurn}}`;
      const fsSeek = $('fs-seek');
      if (fsSeek) fsSeek.value = i;
      const fsTL = $('fs-turn-label');
      if (fsTL) fsTL.textContent = `T${{f.turn}}`;

      // 实时领跑
      const order = [...Array(H.teams).keys()].sort((a, b) => f.score[b] - f.score[a]);
      const leaderT = order[0];
      const leaderBadge = $('board-leader-badge');
      if (leaderBadge) {{
        leaderBadge.innerHTML = `👑 领跑: <strong class="text-emerald-400">${{name(leaderT)}}</strong> (${{f.score[leaderT]}}分)`;
      }}

      // 比分面板条目
      $('teams-list').replaceChildren(...order.map(t => {{
        const d = document.createElement('div');
        d.className = 'team-row' + (focus === t ? ' on' : '');
        d.onclick = () => {{ focus = focus === t ? -1 : t; render(); }};
        const alive = f.units.filter(u => Math.floor(u.id / 3) === t).map(u => u.pos ? (u.flag !== null ? '⚑' : '●') : '○').join('');
        d.innerHTML = `
          <span class="flex items-center truncate">
            <span class="sw" style="background:${{C[t % 15]}}"></span>
            <span class="font-bold truncate text-[#f0f6fc]">${{name(t)}}</span>
            <span class="text-[10px] text-[#8ca0ba] ml-1.5 font-mono">${{alive}}</span>
          </span>
          <b class="text-sm font-mono text-emerald-400">${{f.score[t]}}</b>
        `;
        return d;
      }}));

      // 事件监控流
      try {{
        const evs = f.events.filter(e => e.type !== 'attack' || focus < 0 || Math.floor(e.unit / 3) === focus);
        $('events-log').innerHTML = evs.length ? 
          evs.map(e => `<div class="${{e.type === 'capture' ? 'text-emerald-400 font-bold' : e.type === 'death' ? 'text-red-400' : 'text-[#8ca0ba]'}}">${{ev(e)}}</div>`).join('') :
          '<div class="text-[#475569]">本回合无特殊交火事件</div>';
      }} catch (err) {{}}

      // 指令监控流
      try {{
        $('focus-team-label').textContent = focus >= 0 ? `阵营: ${{name(focus)}}` : '全员监控';
        const ords = Object.entries(f.orders || {{}}).filter(([t]) => focus < 0 || +t === focus);
        $('orders-log').innerHTML = ords.length ?
          ords.map(([t, raw]) => {{
            const list = Array.isArray(raw) ? raw : (raw && Array.isArray(raw.units) ? raw.units : []);
            if (!list.length) return '';
            return `<div class="truncate"><strong class="text-[#f0f6fc]">${{name(+t)}}:</strong> ` + 
              list.map(c => `${{c.id}} ${{MV[c.move] ?? '停'}}${{c.act && c.act !== 'wait' ? ' ' + (AC[c.act] || c.act) : ''}}${{c.act === 'attack' ? '→' + c.target : ''}}${{c.note ? '「' + c.note + '」' : ''}}`).join('，') + 
              `</div>`;
          }}).filter(Boolean).join('') :
          '—';
      }} catch (err) {{}}

      // 实时动态更新 KDA
      if (CUM_STATS && CUM_STATS[i]) {{
        renderKdaTable(CUM_STATS[i]);
      }}

      // 天体星图同步刷新
      if (currentMainTab === 'celestial') {{
        renderCelestialChart();
      }}
    }}

    function star(x, y, r, col) {{
      g.fillStyle = col;
      g.beginPath();
      for(let k = 0; k < 10; k++) {{
        const a = Math.PI / 5 * k - Math.PI / 2, rr = k % 2 ? r * 0.45 : r;
        g.lineTo(x + rr * Math.cos(a), y + rr * Math.sin(a));
      }}
      g.fill();
    }}

    function go(k) {{
      pausePlay();
      i = Math.max(0, Math.min(R.frames.length - 1, k));
      render();
    }}

    function pausePlay() {{
      playing = false;
      $('play').innerHTML = '<span>▶ 播放</span>';
      const fsPlay = $('fs-play-btn');
      if (fsPlay) fsPlay.innerHTML = '▶ 播放';
    }}

    function startPlay() {{
      if (i >= R.frames.length - 1) i = 0;
      playing = true;
      $('play').innerHTML = '<span>⏸ 暂停</span>';
      const fsPlay = $('fs-play-btn');
      if (fsPlay) fsPlay.innerHTML = '⏸ 暂停';
      last = performance.now();
    }}

    function togglePlay() {{
      if (playing) pausePlay();
      else startPlay();
    }}

    function tick(t) {{
      if (playing) {{
        const spd = parseFloat($('speed').value) || 1;
        const interval = 200 / spd;
        if (t - last >= interval) {{
          last = t;
          if (i < R.frames.length - 1) {{
            i++;
            render();
          }} else {{
            pausePlay();
          }}
        }}
      }}
      requestAnimationFrame(tick);
    }}

    function setupEventListeners() {{
      $('play').onclick = togglePlay;
      $('prev').onclick = () => go(i - 1);
      $('next').onclick = () => go(i + 1);
      $('seek').oninput = e => go(+e.target.value);
      $('keys').onchange = e => {{ if (e.target.value !== '') go(+e.target.value); }};

      addEventListener('keydown', e => {{
        if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
        if (e.key === 'ArrowRight') {{ e.preventDefault(); go(i + 1); }}
        if (e.key === 'ArrowLeft') {{ e.preventDefault(); go(i - 1); }}
        if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
        if (e.key === 'f' || e.key === 'F') {{ e.preventDefault(); toggleFullscreen(); }}
      }});
    }}

    function init() {{
      cv = $('board');
      g = cv.getContext('2d');
      setupEventListeners();
      setupCelestialEventListeners();

      // 预先准备逐回合累加统计与天体数据
      CUM_STATS = computeCumulativeStats(R);
      CELESTIAL_DATA = prepareCelestialData(R);

      // 下拉菜单关键回合填充
      const keysSelect = $('keys');
      keysSelect.innerHTML = '<option value="">跳到进球/断旗…</option>';
      R.frames.forEach((f, k) => {{
        const es = f.events.filter(e => e.type === 'capture' || (e.type === 'death' && e.flag !== null));
        if (es.length) {{
          const o = document.createElement('option');
          o.value = k;
          o.textContent = `${{f.turn}} 回合：${{es.map(ev).join('；')}}`;
          keysSelect.append(o);
        }}
      }});

      $('seek').max = R.frames.length - 1;
      const fsSeek = $('fs-seek');
      if (fsSeek) fsSeek.max = R.frames.length - 1;

      render();
      requestAnimationFrame(tick);
    }}

    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', init);
    }} else {{
      init();
    }}
  </script>
</body>
</html>
"""


# 1. 生成大厅 Lobby 页面 (index.html 和 lobby.html)
lobby_content = generate_lobby_html(all_meta)
Path("index.html").write_text(lobby_content, encoding='utf-8')
Path("lobby.html").write_text(lobby_content, encoding='utf-8')

docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)
(docs_dir / "index.html").write_text(lobby_content, encoding='utf-8')
(docs_dir / "lobby.html").write_text(lobby_content, encoding='utf-8')

Path(".nojekyll").write_text("", encoding='utf-8')
(docs_dir / ".nojekyll").write_text("", encoding='utf-8')

print("✓ 成功生成对局选择大厅 index.html 与 lobby.html！")

# 2. 为每一场比赛生成专属独立 HTML 文件 (一个比赛一个网页)
for k, v in raw_data.items():
    match_filename = f"match_{k}.html"
    match_html = generate_match_html(k, v, all_meta)
    
    Path(match_filename).write_text(match_html, encoding='utf-8')
    (docs_dir / match_filename).write_text(match_html, encoding='utf-8')
    print(f"✓ 成功生成独立对局页面: {match_filename}")

print("\n全量网页架构重排与独立拆分完成！")
