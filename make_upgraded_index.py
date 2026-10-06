import json
from pathlib import Path

# 读取全量对局数据（当前目录下）
data_file = Path("all_replays_data.json")
if not data_file.exists():
    data_file = Path(r"C:\Users\caspe\OneDrive\Code\AI_Test\all_replays_data.json")

raw_data = json.loads(data_file.read_text(encoding='utf-8'))

html_template = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CTF 多智能体夺旗 · 官方全景动态回放 & 战力大厅</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1017;
      --panel: #151d28;
      --line: #26354a;
      --ink: #f0f6fc;
      --muted: #8ca0ba;
    }
    * { box-sizing: border-box; }
    body { background-color: var(--bg); color: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0b1017; }
    ::-webkit-scrollbar-thumb { background: #26354a; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }

    .team-row {
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
    }
    .team-row:hover {
      background: #1e293b;
      border-color: #334155;
    }
    .team-row.on {
      background: #1e293b;
      border-color: #3b82f6;
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.25);
    }
    .sw {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 6px;
      flex-shrink: 0;
    }
    .game-card.active {
      border-color: #3b82f6;
      background: rgba(59, 130, 246, 0.08);
      box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
    }
  </style>
</head>
<body class="antialiased p-3 sm:p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    
    <!-- 顶部 Header -->
    <header class="bg-[#151d28] border border-[#26354a] rounded-2xl p-6 shadow-md flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            ✓ 8,000 局冻结赛程验证通过
          </span>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            AMD Ryzen 9 7945HX vs Apple M5
          </span>
          <span class="text-xs text-[#8ca0ba]">官方裁判引擎 v1.0 · Canvas 动态复盘</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#f0f6fc]">
          CTF 多智能体对战平台 · 动态复盘与 KDA 战报大厅
        </h1>
        <p class="text-sm text-[#8ca0ba] mt-1.5">
          15 大顶尖 AI 模型全员交锋 · 逐回合动作级追踪 · 慢动作微操回放 · 完整战损比 KDA 矩阵
        </p>
      </div>

      <div class="flex items-center gap-3">
        <a href="https://github.com/Casper015/ctf-replay-viewer" target="_blank" class="px-4 py-2 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-sm font-medium text-[#f0f6fc] flex items-center gap-2 transition">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          <span>GitHub 仓库</span>
        </a>
      </div>
    </header>

    <!-- 🎮 游戏选择大厅 (Game Selector Lobby) -->
    <section class="bg-[#151d28] border border-[#26354a] rounded-2xl p-5 sm:p-6 shadow-md space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <h2 class="text-lg sm:text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
            <span>🎯</span> 对局选择大厅 (Match Lobby)
          </h2>
          <p class="text-xs text-[#8ca0ba] mt-0.5">点击下方卡片即可立即切换加载对局并刷新回放、实时事件与战绩统计表</p>
        </div>
        <span id="current-loaded-tag" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
          当前加载：15人全员大决战
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5" id="game-card-grid">
        <!-- 动态生成 5 张卡片 -->
      </div>
    </section>

    <!-- 🎬 主播放器区域 -->
    <section class="grid grid-cols-1 lg:grid-cols-12 gap-5">
      
      <!-- 左侧：Canvas 战场与核心控制台 (8 列) -->
      <div class="lg:col-span-8 bg-[#151d28] border border-[#26354a] rounded-2xl p-4 sm:p-5 shadow-md flex flex-col justify-between space-y-4">
        <div>
          <div class="flex justify-between items-center mb-3">
            <div class="flex items-center gap-2">
              <span id="map-badge" class="px-2.5 py-0.5 rounded text-xs font-bold bg-[#212e42] text-blue-400 border border-[#354866]">49×49 地图</span>
              <span id="current-title-label" class="text-xs sm:text-sm font-bold text-[#f0f6fc] truncate max-w-md"></span>
            </div>
            <span id="turns-counter" class="text-xs font-mono font-semibold text-[#8ca0ba]">回合 0 / 400</span>
          </div>

          <!-- Canvas 容器 -->
          <div class="relative w-full aspect-square max-h-[640px] mx-auto bg-[#0b1017] border border-[#26354a] rounded-xl overflow-hidden flex items-center justify-center shadow-inner">
            <canvas id="board" class="block max-w-full max-h-full"></canvas>
          </div>
        </div>

        <!-- 播放器控制栏 -->
        <div class="space-y-3 pt-2">
          
          <!-- 进度滑块 -->
          <div class="space-y-1">
            <div class="flex justify-between text-[11px] text-[#8ca0ba]">
              <span>进度步进</span>
              <span id="progress-percent">0%</span>
            </div>
            <input id="seek" type="range" min="0" value="0" step="1" 
                   class="w-full h-2 bg-[#0b1017] rounded-lg appearance-none cursor-pointer accent-blue-500">
          </div>

          <!-- 播放按钮与速度控制 (加入慢速 0.25x/0.5x，移除 5x 以上) -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
            <div class="flex items-center gap-2">
              <button id="play" class="px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-sm flex items-center gap-1.5 transition select-none cursor-pointer">
                <span>▶ 播放</span>
              </button>
              <button id="prev" class="px-3 py-2 text-xs font-medium rounded-xl bg-[#212e42] hover:bg-[#2b3c56] text-[#f0f6fc] border border-[#354866] transition select-none cursor-pointer">
                ◀ -1T
              </button>
              <button id="next" class="px-3 py-2 text-xs font-medium rounded-xl bg-[#212e42] hover:bg-[#2b3c56] text-[#f0f6fc] border border-[#354866] transition select-none cursor-pointer">
                +1T ▶
              </button>
            </div>

            <!-- 速度调节：0.25x, 0.5x, 1x, 2x, 3x, 4x -->
            <div class="flex items-center gap-2 text-xs">
              <span class="text-[#8ca0ba] font-medium">播放速度:</span>
              <select id="speed" class="bg-[#111822] text-[#f0f6fc] border border-[#354866] rounded-xl px-2.5 py-1.5 text-xs font-mono font-semibold focus:outline-none focus:border-blue-500">
                <option value="0.25">0.25× (慢动作微操)</option>
                <option value="0.5">0.5× (慢速战术分析)</option>
                <option value="1" selected>1× (原速实战)</option>
                <option value="2">2× (流畅倍速)</option>
                <option value="3">3× (快进巡航)</option>
                <option value="4">4× (极速冲刺)</option>
              </select>
            </div>

            <!-- 关键节点快进 -->
            <div class="flex items-center gap-1.5 text-xs w-full sm:w-auto">
              <select id="keys" class="w-full sm:w-auto bg-[#111822] text-[#f0f6fc] border border-[#354866] rounded-xl px-2.5 py-1.5 text-xs focus:outline-none focus:border-blue-500">
                <option value="">跳到关键进球/断旗回合…</option>
              </select>
            </div>
          </div>

          <!-- 底部图例 -->
          <div class="text-[11px] text-[#8ca0ba] flex flex-wrap gap-x-4 gap-y-1 pt-1 border-t border-[#1e2a3b]">
            <span>● 角色 (附带实时血条)</span>
            <span>⭕ 金环 = 正在携旗</span>
            <span>⭐ 星形 = 地面旗帜</span>
            <span>🔲 基地范围</span>
            <span>⚡ 光束 = 攻击命中</span>
            <span>✖ 橙红十字 = 阵亡掉旗</span>
            <span class="text-blue-400">💡 快捷键: 空格=播放/暂停，左右键=逐回合步进</span>
          </div>
        </div>
      </div>

      <!-- 右侧：阵营得分、实时事件与指令 (4 列) -->
      <div class="lg:col-span-4 space-y-4 flex flex-col">
        
        <!-- 阵营当前比分榜 -->
        <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md flex-1">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-xs font-bold text-[#8ca0ba] uppercase tracking-wider">实时阵营与得分 (点击筛选高亮)</h3>
            <span class="text-[11px] text-blue-400">实时领先</span>
          </div>
          <div id="teams-list" class="space-y-1.5 max-h-[260px] overflow-y-auto pr-1">
            <!-- 动态队伍条目 -->
          </div>
        </div>

        <!-- 本回合事件监控流 -->
        <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md flex-1">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-xs font-bold text-[#8ca0ba] uppercase tracking-wider">本回合战况事件 (Events)</h3>
            <span id="event-turn-badge" class="text-[11px] font-mono text-[#8ca0ba]">T0</span>
          </div>
          <div id="events-log" class="text-xs font-mono bg-[#0b1017] p-2.5 rounded-xl border border-[#26354a] h-[160px] overflow-y-auto space-y-1.5">
            <!-- 动态事件 -->
          </div>
        </div>

        <!-- 本回合指令监控 -->
        <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-xs font-bold text-[#8ca0ba] uppercase tracking-wider">角色指令流 (Orders)</h3>
            <span id="focus-team-label" class="text-[11px] text-[#8ca0ba]">全员监控</span>
          </div>
          <div id="orders-log" class="text-xs font-mono bg-[#0b1017] p-2.5 rounded-xl border border-[#26354a] h-[120px] overflow-y-auto text-[#8ca0ba]">
            <!-- 动态指令 -->
          </div>
        </div>

      </div>
    </section>

    <!-- 📊 全场战绩矩阵与 KDA 战力表 -->
    <section class="bg-[#151d28] border border-[#26354a] rounded-2xl p-5 sm:p-6 shadow-md space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <h2 class="text-lg sm:text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
            <span>📊</span> 全场技术统计矩阵与 KDA 战力榜 (Combat Matrix & KDA)
          </h2>
          <p class="text-xs text-[#8ca0ba] mt-0.5">
            详细记录：拿了多少旗 (进球/拾取) · 杀了多少人 (总杀/断旗绝杀) · 阵亡数 · 进球转化率 · KDA 战损比
          </p>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="text-[#8ca0ba]">KDA 战损比计算公式:</span>
          <span class="px-2.5 py-1 rounded bg-[#212e42] text-amber-400 font-mono font-bold border border-[#354866]">(击杀 + 0.5×断旗截杀) / 阵亡</span>
        </div>
      </div>

      <!-- KDA 数据表格 -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs sm:text-sm">
          <thead>
            <tr class="border-b border-[#26354a] text-[#8ca0ba] text-xs font-semibold">
              <th class="py-2.5 px-3 text-center">排名</th>
              <th class="py-2.5 px-3">参赛阵营 / 模型</th>
              <th class="py-2.5 px-3 text-right">进球得分 (交旗)</th>
              <th class="py-2.5 px-3 text-right">捡旗总数</th>
              <th class="py-2.5 px-3 text-right">总击杀数 (Kills)</th>
              <th class="py-2.5 px-3 text-right">断旗截杀 (Carrier Kills)</th>
              <th class="py-2.5 px-3 text-right">阵亡数 (Deaths)</th>
              <th class="py-2.5 px-3 text-right">进球转化率</th>
              <th class="py-2.5 px-3 text-right">KDA 战损比</th>
              <th class="py-2.5 px-3 text-center">综合战术评级</th>
            </tr>
          </thead>
          <tbody id="kda-tbody" class="divide-y divide-[#1e2a3b] font-mono">
            <!-- 动态生成 KDA 行 -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- 🏆 8,000 局 Plackett-Luce 天梯总榜 -->
    <section class="bg-[#151d28] border border-[#26354a] rounded-2xl p-5 sm:p-6 shadow-md space-y-4">
      <div>
        <h2 class="text-lg sm:text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
          <span>🏆</span> 8,000 局 Plackett-Luce 天梯总榜 (Tournament Leaderboard)
        </h2>
        <p class="text-xs text-[#8ca0ba] mt-0.5">8 个阵营档位等权拟合 · 基准模型锚定 0 分 · 换机器前后排位 100% 相同</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
        <div class="p-3.5 bg-[#0b1017] rounded-xl border border-[#26354a]">
          <div class="text-[#8ca0ba]">🥇 绝对冠军 (多人局霸主)</div>
          <div class="text-base font-bold text-yellow-400 font-sans mt-1">Player5</div>
          <div class="text-emerald-400 mt-0.5">PL: +320.8 · 场均 11.24 分 · 延迟 1.0ms</div>
        </div>
        <div class="p-3.5 bg-[#0b1017] rounded-xl border border-[#26354a]">
          <div class="text-[#8ca0ba]">🥈 亚军 (长程机动王)</div>
          <div class="text-base font-bold text-blue-400 font-sans mt-1">GPT-6.1 Sol</div>
          <div class="text-blue-400 mt-0.5">PL: +264.9 · 场均 10.32 分 · 延迟 3.5ms</div>
        </div>
        <div class="p-3.5 bg-[#0b1017] rounded-xl border border-[#26354a]">
          <div class="text-[#8ca0ba]">🥉 季军 (单挑统治者)</div>
          <div class="text-base font-bold text-purple-400 font-sans mt-1">GPT-6 Astra</div>
          <div class="text-purple-400 mt-0.5">PL: +240.9 · 场均 9.97 分 · 延迟 12.1ms</div>
        </div>
      </div>
    </section>

  </div>

  <script>
    const ALL_GAMES = """ + json.dumps(raw_data, ensure_ascii=False) + """;
    let activeKey = 'g15';
    let R = ALL_GAMES[activeKey].replay;
    
    const C = ['#ff6b7f','#5ab4ff','#7bd99b','#d7a2ff','#ffcb6b','#5fd9d4','#ff9fd0','#b5cc6e','#a9aeff','#f09c63','#e0e0e0','#8fb3c9','#e8d38a','#c98fa8','#8fd6b2'];
    const $ = id => document.getElementById(id);
    let cv, g;
    
    let i = 0, playing = false, last = 0, focus = -1;
    const MV = {N:'上', S:'下', E:'右', W:'左', WAIT:'停'};
    const AC = {attack:'攻击', pickup:'拾旗', drop:'丢旗', wait:''};
    const name = t => (R && R.names && R.names[t]) ? R.names[t] : ('阵营' + t);

    // 初始化游戏选择卡片
    function initLobbyCards() {
      const grid = $('game-card-grid');
      let html = '';
      for (const [key, cfg] of Object.entries(ALL_GAMES)) {
        html += `
          <div onclick="selectGame('${key}')" id="card-${key}" class="game-card p-3.5 rounded-xl bg-[#111822] border border-[#26354a] cursor-pointer hover:border-[#3b82f6] transition flex flex-col justify-between space-y-2 select-none">
            <div>
              <div class="flex items-center justify-between gap-1 mb-1">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#212e42] text-blue-400">${cfg.badge.split('·')[0].trim()}</span>
                <span class="text-[10px] text-amber-400 font-bold">${cfg.tag}</span>
              </div>
              <h4 class="text-xs font-bold text-[#f0f6fc] leading-snug line-clamp-2">${cfg.title}</h4>
            </div>
            <p class="text-[11px] text-[#8ca0ba] line-clamp-2 leading-relaxed">${cfg.desc}</p>
          </div>
        `;
      }
      grid.innerHTML = html;
      updateActiveCard();
    }

    function selectGame(key) {
      if (activeKey === key) return;
      activeKey = key;
      R = ALL_GAMES[activeKey].replay;
      pausePlay();
      i = 0;
      focus = -1;
      updateActiveCard();
      loadGameToViewer();
    }

    function updateActiveCard() {
      for (const key of Object.keys(ALL_GAMES)) {
        const el = $('card-' + key);
        if (el) {
          if (key === activeKey) {
            el.className = 'game-card p-3.5 rounded-xl bg-[#1e293b] border-2 border-blue-500 shadow-md cursor-pointer flex flex-col justify-between space-y-2 select-none';
          } else {
            el.className = 'game-card p-3.5 rounded-xl bg-[#111822] border border-[#26354a] cursor-pointer hover:border-[#334155] transition flex flex-col justify-between space-y-2 select-none';
          }
        }
      }
      $('current-loaded-tag').innerText = '当前加载：' + ALL_GAMES[activeKey].tag;
    }

    function loadGameToViewer() {
      const cfg = ALL_GAMES[activeKey];
      $('map-badge').innerText = `${R.header.size}×${R.header.size} 地图 · ${R.header.teams} 阵营`;
      $('current-title-label').innerText = `${cfg.title} (${cfg.id})`;
      $('seek').max = R.frames.length - 1;
      $('seek').value = 0;

      // 下拉菜单关键回合填充
      const keysSelect = $('keys');
      keysSelect.innerHTML = '<option value="">跳到关键进球/断旗回合…</option>';
      R.frames.forEach((f, k) => {
        const es = f.events.filter(e => e.type === 'capture' || (e.type === 'death' && e.flag !== null));
        if (es.length) {
          const o = document.createElement('option');
          o.value = k;
          o.textContent = `${f.turn} 回合：${es.map(ev).join('；')}`;
          keysSelect.append(o);
        }
      });

      renderKdaTable();
      render();
    }

    function renderKdaTable() {
      const tbody = $('kda-tbody');
      const stats = (ALL_GAMES[activeKey].replay && ALL_GAMES[activeKey].replay.enhanced_stats) ? ALL_GAMES[activeKey].replay.enhanced_stats : (ALL_GAMES[activeKey].enhanced_stats || []);
      if (!stats || !stats.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="py-4 text-center text-[#8ca0ba]">暂无统计数据</td></tr>';
        return;
      }
      let html = '';
      stats.forEach((st, rank) => {
        const isTop = rank === 0;
        const color = C[st.team % 15];
        
        let badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-gray-500/10 text-gray-400">稳定发挥</span>';
        if (rank === 0) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-yellow-500/10 text-yellow-400 font-bold">👑 本场 MVP</span>';
        else if (st.kills >= 10) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-red-500/10 text-red-400 font-bold">⚔️ 杀神</span>';
        else if (st.capture_rate >= 80) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 font-bold">🎯 高效护送</span>';
        else if (st.carrier_kills >= 3) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-400 font-bold">🛡️ 铁壁截断</span>';

        html += `
          <tr class="hover:bg-[#1a2433] transition ${isTop ? 'bg-blue-500/5' : ''}">
            <td class="py-2.5 px-3 text-center font-bold ${rank < 3 ? 'text-yellow-400' : 'text-[#8ca0ba]'}">${rank + 1}</td>
            <td class="py-2.5 px-3 font-sans font-bold flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full inline-block" style="background:${color}"></span>
              <span class="${isTop ? 'text-blue-400' : 'text-[#f0f6fc]'}">${st.name}</span>
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-emerald-400 text-sm">${st.score}</td>
            <td class="py-2.5 px-3 text-right text-[#f0f6fc]">${st.pickups}</td>
            <td class="py-2.5 px-3 text-right font-bold text-red-400">${st.kills}</td>
            <td class="py-2.5 px-3 text-right text-amber-400 font-bold">${st.carrier_kills}</td>
            <td class="py-2.5 px-3 text-right text-[#8ca0ba]">${st.deaths}</td>
            <td class="py-2.5 px-3 text-right text-cyan-400">${st.capture_rate}%</td>
            <td class="py-2.5 px-3 text-right font-bold ${st.kda >= 1.5 ? 'text-emerald-400' : st.kda >= 1 ? 'text-blue-400' : 'text-[#8ca0ba]'}">${st.kda}</td>
            <td class="py-2.5 px-3 text-center">${badge}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    function ev(e) {
      switch(e.type) {
        case 'capture': return `🏆 ${name(e.team)} 成功交旗进球！(角色 ${e.unit}，旗 ${e.flag})`;
        case 'pickup':  return `🚩 角色 ${e.unit} [${name(Math.floor(e.unit/3))}] 拾取旗帜 ${e.flag}`;
        case 'drop':    return `放下旗帜 ${e.flag} (角色 ${e.unit})`;
        case 'death':   return `💀 角色 ${e.unit} [${name(Math.floor(e.unit/3))}] 阵亡${e.flag!==null?' (掉落旗'+e.flag+')':''}${e.by && e.by.length ? ' 击杀者: ' + e.by.join('、') : ''}`;
        case 'attack':  return `⚔️ 角色 ${e.unit} 攻击 角色 ${e.target}`;
        case 'respawn': return `🔄 角色 ${e.unit} 基地重生`;
        case 'return':  return `⏳ 旗帜 ${e.flag} 刷新回位`;
        default: return JSON.stringify(e);
      }
    }

    function render() {
      if (!cv) cv = $('board');
      if (!g) g = cv.getContext('2d');
      if (!R || !R.frames || !R.frames[i]) return;

      const f = R.frames[i], H = R.header, n = H.size, s = Math.max(8, Math.floor(640 / n));
      cv.width = cv.height = n * s;

      // 绘制地图底色与墙壁
      for(let y = 0; y < n; y++) {
        for(let x = 0; x < n; x++) {
          g.fillStyle = H.map[y][x] === '#' ? '#2b394d' : ((x + y) % 2 ? '#121822' : '#151e2b');
          g.fillRect(x * s, y * s, s, s);
        }
      }

      // 绘制基地范围
      H.bases.forEach((b, t) => {
        g.fillStyle = C[t % 15] + (focus < 0 || focus === t ? '44' : '15');
        for(const [x, y] of b) g.fillRect(x * s, y * s, s, s);
      });

      // 旗点标记
      g.setLineDash([2, 2]);
      g.strokeStyle = '#ffe08a77';
      for(const [x, y] of H.flag_spots) {
        g.beginPath();
        g.arc((x + 0.5) * s, (y + 0.5) * s, s * 0.42, 0, 7);
        g.stroke();
      }
      g.setLineDash([]);

      // 攻击光束
      for(const e of f.events) {
        if(e.type === 'attack') {
          const a = f.units[e.unit], b = f.units[e.target];
          if(!a || !b) continue;
          const pa = a.pos, pb = b.pos || (f.events.find(z => z.type === 'death' && z.unit === e.target) || {}).pos;
          if(pa && pb) {
            g.strokeStyle = '#fef08a';
            g.lineWidth = Math.max(1.5, s * 0.15);
            g.beginPath();
            g.moveTo((pa[0] + 0.5) * s, (pa[1] + 0.5) * s);
            g.lineTo((pb[0] + 0.5) * s, (pb[1] + 0.5) * s);
            g.stroke();
          }
        }
      }

      // 地面旗帜
      for(const fl of f.flags) {
        if(fl && fl.pos) {
          const [x, y] = fl.pos;
          star((x + 0.5) * s, (y + 0.5) * s, s * 0.42, '#fbbf24');
        }
      }

      // 阵亡十字
      for(const e of f.events) {
        if(e.type === 'death' && e.pos) {
          const [x, y] = e.pos;
          g.strokeStyle = '#f87171';
          g.lineWidth = Math.max(2, s * 0.18);
          g.beginPath();
          g.moveTo(x * s + 2, y * s + 2);
          g.lineTo(x * s + s - 2, y * s + s - 2);
          g.moveTo(x * s + s - 2, y * s + 2);
          g.lineTo(x * s + 2, y * s + s - 2);
          g.stroke();
        }
      }

      // 角色单位
      for(const u of f.units) {
        if(!u || !u.pos) continue;
        const t = Math.floor(u.id / 3), [x, y] = u.pos, cx = (x + 0.5) * s, cy = (y + 0.5) * s;
        g.globalAlpha = focus < 0 || focus === t ? 1 : 0.2;
        
        // 角色圆点
        g.fillStyle = C[t % 15];
        g.beginPath();
        g.arc(cx, cy, s * 0.36, 0, 7);
        g.fill();

        // 携旗金环
        if(u.flag !== null) {
          g.strokeStyle = '#fbbf24';
          g.lineWidth = Math.max(2.5, s * 0.2);
          g.beginPath();
          g.arc(cx, cy, s * 0.52, 0, 7);
          g.stroke();
        }

        // 单位数字
        g.fillStyle = '#0b1017';
        g.font = `bold ${Math.max(7, Math.floor(s * 0.38))}px sans-serif`;
        g.textAlign = 'center';
        g.textBaseline = 'middle';
        g.fillText(u.id, cx, cy + 0.5);

        // 动态血条
        g.fillStyle = '#0b1017';
        g.fillRect(x * s + 1, y * s + 1, s - 2, 2);
        g.fillStyle = u.hp > 50 ? '#34d399' : '#f87171';
        g.fillRect(x * s + 1, y * s + 1, (s - 2) * (u.hp / H.rules.hp), 2);
      }
      g.globalAlpha = 1;

      // 状态文本与控件联动
      const maxTurn = (R.frames[R.frames.length - 1] ? R.frames[R.frames.length - 1].turn : 400);
      $('turns-counter').textContent = `回合 ${f.turn} / ${maxTurn}`;
      $('seek').value = i;
      $('progress-percent').textContent = Math.round((i / (R.frames.length - 1)) * 100) + '%';
      $('event-turn-badge').textContent = `T${f.turn}`;

      // 右侧阵营列表排序更新
      const order = [...Array(H.teams).keys()].sort((a, b) => f.score[b] - f.score[a]);
      $('teams-list').replaceChildren(...order.map(t => {
        const d = document.createElement('div');
        d.className = 'team-row' + (focus === t ? ' on' : '');
        d.onclick = () => { focus = focus === t ? -1 : t; render(); };
        const alive = f.units.filter(u => Math.floor(u.id / 3) === t).map(u => u.pos ? (u.flag !== null ? '⚑' : '●') : '○').join('');
        d.innerHTML = `
          <span class="flex items-center truncate">
            <span class="sw" style="background:${C[t % 15]}"></span>
            <span class="font-bold truncate text-[#f0f6fc]">${name(t)}</span>
            <span class="text-[10px] text-[#8ca0ba] ml-1.5 font-mono">${alive}</span>
          </span>
          <b class="text-sm font-mono text-emerald-400">${f.score[t]}</b>
        `;
        return d;
      }));

      // 事件监控流 (Safe try-catch)
      try {
        const evs = f.events.filter(e => e.type !== 'attack' || focus < 0 || Math.floor(e.unit / 3) === focus);
        $('events-log').innerHTML = evs.length ? 
          evs.map(e => `<div class="${e.type === 'capture' ? 'text-emerald-400 font-bold' : e.type === 'death' ? 'text-red-400' : 'text-[#8ca0ba]'}">${ev(e)}</div>`).join('') :
          '<div class="text-[#475569]">本回合无特殊交火事件</div>';
      } catch (err) {
        console.error('Error rendering events log:', err);
      }

      // 指令监控流 (Safe object/array handling)
      try {
        $('focus-team-label').textContent = focus >= 0 ? `阵营: ${name(focus)}` : '全员监控';
        const ords = Object.entries(f.orders || {}).filter(([t]) => focus < 0 || +t === focus);
        $('orders-log').innerHTML = ords.length ?
          ords.map(([t, raw]) => {
            const list = Array.isArray(raw) ? raw : (raw && Array.isArray(raw.units) ? raw.units : []);
            if (!list.length) return '';
            return `<div class="truncate"><strong class="text-[#f0f6fc]">${name(+t)}:</strong> ` + 
              list.map(c => `${c.id} ${MV[c.move] ?? '停'}${c.act && c.act !== 'wait' ? ' ' + (AC[c.act] || c.act) : ''}${c.act === 'attack' ? '→' + c.target : ''}${c.note ? '「' + c.note + '」' : ''}`).join('，') + 
              `</div>`;
          }).filter(Boolean).join('') :
          '—';
      } catch (err) {
        console.error('Error rendering orders log:', err);
      }
    }

    function star(x, y, r, col) {
      g.fillStyle = col;
      g.beginPath();
      for(let k = 0; k < 10; k++) {
        const a = Math.PI / 5 * k - Math.PI / 2, rr = k % 2 ? r * 0.45 : r;
        g.lineTo(x + rr * Math.cos(a), y + rr * Math.sin(a));
      }
      g.fill();
    }

    function go(k) {
      pausePlay();
      i = Math.max(0, Math.min(R.frames.length - 1, k));
      render();
    }

    function pausePlay() {
      playing = false;
      const playBtn = $('play');
      if (playBtn) playBtn.innerHTML = '<span>▶ 播放</span>';
    }

    function startPlay() {
      if (i >= R.frames.length - 1) i = 0;
      playing = true;
      const playBtn = $('play');
      if (playBtn) playBtn.innerHTML = '<span>⏸ 暂停</span>';
      last = performance.now();
    }

    function togglePlay() {
      if (playing) {
        pausePlay();
      } else {
        startPlay();
      }
    }

    function tick(t) {
      if (playing) {
        const spd = parseFloat($('speed').value) || 1;
        // 速度映射：1x 对应 200ms 每帧；0.25x 对应 800ms 每帧；4x 对应 50ms 每帧
        const interval = 200 / spd;
        if (t - last >= interval) {
          last = t;
          if (i < R.frames.length - 1) {
            i++;
            render();
          } else {
            pausePlay();
          }
        }
      }
      requestAnimationFrame(tick);
    }

    // 绑定事件
    function setupEventListeners() {
      $('play').onclick = togglePlay;
      $('prev').onclick = () => go(i - 1);
      $('next').onclick = () => go(i + 1);
      $('seek').oninput = e => go(+e.target.value);
      $('keys').onchange = e => { if (e.target.value !== '') go(+e.target.value); };

      addEventListener('keydown', e => {
        if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
        if (e.key === 'ArrowRight') { e.preventDefault(); go(i + 1); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); go(i - 1); }
        if (e.key === ' ') { e.preventDefault(); togglePlay(); }
      });
    }

    function init() {
      cv = $('board');
      g = cv.getContext('2d');
      setupEventListeners();
      initLobbyCards();
      loadGameToViewer();
      requestAnimationFrame(tick);
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  </script>
</body>
</html>
"""

Path("index.html").write_text(html_template, encoding='utf-8')
docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)
(docs_dir / "index.html").write_text(html_template, encoding='utf-8')
print("Successfully generated upgraded index.html and docs/index.html with bulletproof playback!")
