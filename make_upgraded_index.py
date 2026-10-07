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
  <title>CTF 多智能体夺旗 · 官方全景动态回放 & 实时战力大厅</title>
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
    .match-item {
      transition: all 0.15s ease;
      border: 1px solid #26354a;
      background: #111822;
    }
    .match-item:hover {
      background: #182333;
      border-color: #3b82f6;
    }
    .match-item.active {
      border-color: #3b82f6;
      background: rgba(59, 130, 246, 0.12);
      box-shadow: 0 0 12px rgba(59, 130, 246, 0.25);
    }
    #celestial-canvas {
      image-rendering: auto;
      touch-action: none;
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
            ✓ 8,000 局冻结赛程全量通过
          </span>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            AMD Ryzen 9 7945HX vs Apple M5
          </span>
          <span class="text-xs text-[#8ca0ba]">官方裁判引擎 v1.0 · Canvas 动态复盘</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#f0f6fc]">
          CTF 多智能体对战平台 · 动态复盘与实时 KDA 战报大厅
        </h1>
        <p class="text-sm text-[#8ca0ba] mt-1.5">
          15 大顶尖 AI 模型全员交锋 · 逐回合动作级追踪 · 慢动作微操回放 · 随播放步进实时动态刷新战损比矩阵
        </p>
      </div>

      <div class="flex items-center gap-3">
        <a href="https://github.com/Casper015/ctf-replay-viewer" target="_blank" class="px-4 py-2 rounded-xl bg-[#212e42] hover:bg-[#2b3c56] border border-[#354866] text-sm font-medium text-[#f0f6fc] flex items-center gap-2 transition">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          <span>GitHub 仓库</span>
        </a>
      </div>
    </header>

    <!-- 🎮 游戏选择大厅 (Match Lobby List - 列表化设计，支持未来扩充无限场次) -->
    <section class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 sm:p-5 shadow-md space-y-3.5">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h2 class="text-lg sm:text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
            <span>🎯</span> 对局选择大厅 (Match Lobby)
          </h2>
          <p class="text-xs text-[#8ca0ba] mt-0.5">采用无限扩充 List 架构 · 支持按人数分类与关键词搜索 · 点击任意条目免刷新秒级切换</p>
        </div>
        
        <!-- 搜索与场次指示 -->
        <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <div class="relative flex-1 sm:w-60">
            <input id="match-search" type="text" placeholder="搜索模型、对局ID、特征…" 
                   class="w-full bg-[#0b1017] text-[#f0f6fc] text-xs rounded-xl px-3 py-1.5 border border-[#26354a] focus:outline-none focus:border-blue-500 pl-8 placeholder-[#64748b]">
            <svg class="w-3.5 h-3.5 absolute left-2.5 top-2 text-[#64748b]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
          <span id="match-count-badge" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-[#212e42] text-blue-400 border border-[#354866]">
            共 6 场对局
          </span>
        </div>
      </div>

      <!-- 快捷人数筛选 Tabs -->
      <div class="flex flex-wrap items-center gap-1.5 text-xs pt-1 border-t border-[#1e2a3b]" id="filter-tabs">
        <button onclick="setFilter('all')" class="filter-btn px-3 py-1 rounded-lg bg-blue-600 text-white font-semibold transition" data-filter="all">全部对局</button>
        <button onclick="setFilter('15')" class="filter-btn px-3 py-1 rounded-lg bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] transition" data-filter="15">15人决战</button>
        <button onclick="setFilter('8')" class="filter-btn px-3 py-1 rounded-lg bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] transition" data-filter="8">8人混战</button>
        <button onclick="setFilter('4')" class="filter-btn px-3 py-1 rounded-lg bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] transition" data-filter="4">4人交锋</button>
        <button onclick="setFilter('3')" class="filter-btn px-3 py-1 rounded-lg bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] transition" data-filter="3">3人逆转</button>
        <button onclick="setFilter('2')" class="filter-btn px-3 py-1 rounded-lg bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] transition" data-filter="2">2人单挑</button>
      </div>

      <!-- 可滚动对局列表 (Scrollable Match List) -->
      <div class="max-h-60 overflow-y-auto space-y-1.5 pr-1 rounded-xl border border-[#26354a] p-1.5 bg-[#0b1017]/60" id="match-list-container">
        <!-- 动态生成对局列表条目 -->
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
              <span>对战进度步进</span>
              <span id="progress-percent" class="font-mono text-blue-400 font-bold">0%</span>
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
              <span class="text-[#8ca0ba] font-medium">播放倍速:</span>
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
            <span class="text-blue-400">💡 快捷键: 空格=播放/暂停，左右方向键=逐回合微调</span>
          </div>
        </div>
      </div>

      <!-- 右侧：阵营得分、实时事件与指令 (4 列) -->
      <div class="lg:col-span-4 space-y-4 flex flex-col">
        
        <!-- 阵营当前比分与天体走势图 (Tab 容器) -->
        <div class="bg-[#151d28] border border-[#26354a] rounded-2xl p-4 shadow-md flex-1 flex flex-col">
          <!-- Tab 导航栏与状态指示 -->
          <div class="flex items-center justify-between border-b border-[#26354a] pb-2.5 mb-3 flex-shrink-0">
            <div class="flex items-center gap-1.5 bg-[#0b1017] p-1 rounded-xl border border-[#1e2a3b]">
              <button id="tab-btn-scores" onclick="switchScoreTab('list')" 
                class="px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-blue-600 text-white shadow-sm">
                <span>📋</span>
                <span>实时比分</span>
              </button>
              <button id="tab-btn-celestial" onclick="switchScoreTab('celestial')" 
                class="px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-[#8ca0ba] hover:text-[#f0f6fc]">
                <span class="text-purple-400">🌌</span>
                <span>天体走势图</span>
                <span class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
              </button>
            </div>

            <!-- 右侧小工具 / 模式切换 -->
            <div class="flex items-center gap-2">
              <span id="score-header-badge" class="text-[11px] text-blue-400 font-mono">实时领先</span>
              <div id="celestial-controls" class="hidden flex items-center gap-1.5">
                <button id="btn-celestial-mode" onclick="toggleCelestialMode()" 
                  title="切换投影视图：时序星轨 / 极坐标星盘"
                  class="px-2 py-0.5 rounded-lg text-[11px] font-mono bg-[#111822] text-cyan-400 hover:bg-[#1a2536] border border-[#26354a] transition flex items-center gap-1">
                  <span id="celestial-mode-icon">📈</span>
                  <span id="celestial-mode-text">时序星轨</span>
                </button>
                <button onclick="resetCelestialFocus()" title="重置队伍聚焦筛选" 
                  class="px-1.5 py-0.5 rounded-lg text-[11px] bg-[#111822] text-[#8ca0ba] hover:text-white border border-[#26354a] transition">
                  ↺ 全景
                </button>
              </div>
            </div>
          </div>

          <!-- Tab 1 内容: 实时阵营列表 -->
          <div id="score-pane-list" class="flex-1 flex flex-col min-h-0">
            <div id="teams-list" class="space-y-1.5 max-h-[260px] overflow-y-auto pr-1">
              <!-- 动态队伍条目 -->
            </div>
          </div>

          <!-- Tab 2 内容: 天体走势图 Canvas & HUD -->
          <div id="score-pane-celestial" class="hidden flex-1 flex flex-col min-h-0">
            <div class="relative w-full h-[255px] rounded-xl overflow-hidden bg-[#050811] border border-[#1e2a3b] shadow-inner">
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

            <!-- 图例辅助说明 -->
            <div class="flex items-center justify-between text-[10px] text-[#8ca0ba] pt-2 px-1 flex-shrink-0">
              <div class="flex items-center gap-2">
                <span class="flex items-center gap-1">
                  <span class="inline-block w-2 h-2 rounded-full bg-cyan-400"></span>
                  <span>星轨: 得分轨迹</span>
                </span>
                <span class="flex items-center gap-1 text-yellow-300">
                  <span>⭐</span>
                  <span>超新星: 进球时刻</span>
                </span>
              </div>
              <span class="text-blue-400">点击画布队伍聚焦 / 回合跳跃</span>
            </div>
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

    <!-- 📊 实时战绩矩阵与 KDA 战力表 (完全随播放帧动态更新) -->
    <section class="bg-[#151d28] border border-[#26354a] rounded-2xl p-5 sm:p-6 shadow-md space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <div class="flex items-center gap-2.5">
            <h2 class="text-lg sm:text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
              <span>📊</span> 实时技术统计矩阵与 KDA 战力榜
            </h2>
            <span id="kda-turn-badge" class="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              当前回合: T0 / 400
            </span>
          </div>
          <p class="text-xs text-[#8ca0ba] mt-0.5">
            随播放进度实时累加统计：拿了多少旗 (交旗进球/捡旗/转化率) · 杀了多少人 (击杀/助攻/断旗截杀) · 阵亡数 · 实时 KDA 战损比
          </p>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="text-[#8ca0ba]">KDA 战损比计算模型:</span>
          <span class="px-2.5 py-1 rounded bg-[#212e42] text-amber-400 font-mono font-bold border border-[#354866]">(击杀 + 0.5×助攻) / max(1, 阵亡)</span>
        </div>
      </div>

      <!-- 🌟 当前回合高能数据卡片 (实时同步) -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs" id="kda-highlight-cards">
        <!-- 动态生成 4 张实时王座卡片 -->
      </div>

      <!-- 实时 KDA 数据表格 -->
      <div class="overflow-x-auto rounded-xl border border-[#26354a]">
        <table class="w-full text-left border-collapse text-xs sm:text-sm">
          <thead>
            <tr class="bg-[#101722] border-b border-[#26354a] text-[#8ca0ba] text-xs font-semibold">
              <th class="py-3 px-3 text-center">实时排名</th>
              <th class="py-3 px-3">参赛模型 / 阵营</th>
              <th class="py-3 px-3 text-right">🏆 进球得分 (交旗)</th>
              <th class="py-3 px-3 text-right">🚩 捡旗总数</th>
              <th class="py-3 px-3 text-right">🎯 护送转化率</th>
              <th class="py-3 px-3 text-right">⚔️ 击杀 (Kills)</th>
              <th class="py-3 px-3 text-right">🤝 助攻 (Assists)</th>
              <th class="py-3 px-3 text-right">🛡️ 断旗截杀</th>
              <th class="py-3 px-3 text-right">💀 阵亡 (Deaths)</th>
              <th class="py-3 px-3 text-right">📊 实时 KDA</th>
              <th class="py-3 px-3 text-center">🎖️ 实时战术评级</th>
            </tr>
          </thead>
          <tbody id="kda-tbody" class="divide-y divide-[#1e2a3b] font-mono bg-[#0e141f]">
            <!-- 动态生成实时 KDA 行 -->
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
    let activeKey = 'g15_rec';
    let R = ALL_GAMES[activeKey].replay;
    let CUM_STATS = []; // 存储当前对局每回合的实时累加统计数据
    
    let currentFilter = 'all';
    let currentSearchKeyword = '';

    let currentScoreTab = 'list'; // 'list' | 'celestial'
    let celestialMode = 'timeline'; // 'timeline' | 'polar'
    let CELESTIAL_DATA = null;

    const C = ['#ff6b7f','#5ab4ff','#7bd99b','#d7a2ff','#ffcb6b','#5fd9d4','#ff9fd0','#b5cc6e','#a9aeff','#f09c63','#e0e0e0','#8fb3c9','#e8d38a','#c98fa8','#8fd6b2'];
    const $ = id => document.getElementById(id);
    let cv, g;
    
    let i = 0, playing = false, last = 0, focus = -1;
    const MV = {N:'上', S:'下', E:'右', W:'左', WAIT:'停'};
    const AC = {attack:'攻击', pickup:'拾旗', drop:'丢旗', wait:''};
    const name = t => (R && R.names && R.names[t]) ? R.names[t] : ('阵营' + t);

    // 预先逐帧计算当前对局的实时累加技术统计 (耗时 < 2ms)
    function computeCumulativeStats(replayObj) {
      const teams = replayObj.header.teams;
      const running = [];
      for (let t = 0; t < teams; t++) {
        running.push({
          team: t,
          name: (replayObj.names && replayObj.names[t]) ? replayObj.names[t] : ('阵营' + t),
          score: 0,
          pickups: 0,
          kills: 0,
          assists: 0,
          carrier_kills: 0,
          deaths: 0,
        });
      }

      const snapshots = [];
      for (let frameIdx = 0; frameIdx < replayObj.frames.length; frameIdx++) {
        const f = replayObj.frames[frameIdx];
        for (const e of f.events) {
          if (e.type === 'capture') {
            if (running[e.team]) running[e.team].score++;
          } else if (e.type === 'pickup') {
            const tm = Math.floor(e.unit / 3);
            if (running[tm]) running[tm].pickups++;
          } else if (e.type === 'death') {
            const victimTeam = Math.floor(e.unit / 3);
            if (running[victimTeam]) running[victimTeam].deaths++;
            
            const attackers = e.by || [];
            const isCarrier = (e.flag !== null && e.flag !== undefined);
            if (attackers.length === 1) {
              const killerTeam = Math.floor(attackers[0] / 3);
              if (running[killerTeam]) {
                running[killerTeam].kills++;
                if (isCarrier) running[killerTeam].carrier_kills++;
              }
            } else if (attackers.length > 1) {
              const primaryTeam = Math.floor(attackers[0] / 3);
              if (running[primaryTeam]) {
                running[primaryTeam].kills++;
                if (isCarrier) running[primaryTeam].carrier_kills++;
              }
              for (let a = 1; a < attackers.length; a++) {
                const assistTeam = Math.floor(attackers[a] / 3);
                if (running[assistTeam]) running[assistTeam].assists++;
              }
            }
          }
        }

        // 保存 frameIdx 状态快照
        const snapshot = running.map(st => {
          const kdaVal = st.deaths > 0 ? ((st.kills + st.assists * 0.5) / st.deaths) : (st.kills + st.assists * 0.5);
          const rateVal = st.pickups > 0 ? ((st.score / st.pickups) * 100) : 0;
          return {
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
          };
        });
        // 动态根据当前进球数降序、KDA 降序排列
        snapshot.sort((a, b) => b.score - a.score || b.kda - a.kda);
        snapshots.push(snapshot);
      }
      return snapshots;
    }

    // 生成固定的宇宙微弱背景繁星星表 (120 颗固定背景星)
    function generateStarfield(count) {
      const stars = [];
      let seed = 12345;
      const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
      for (let k = 0; k < count; k++) {
        stars.push({
          x: rnd(),
          y: rnd(),
          r: rnd() * 1.4 + 0.6,
          alpha: rnd() * 0.45 + 0.2,
          flicker: rnd() * Math.PI * 2,
          speed: rnd() * 0.04 + 0.02
        });
      }
      return stars;
    }

    // 预解析对局的全周期比分走势与超新星进球时刻
    function prepareCelestialData(replayObj) {
      if (!replayObj || !replayObj.frames) return null;
      const teams = replayObj.header.teams;
      const frames = replayObj.frames;
      const maxTurn = frames[frames.length - 1] ? frames[frames.length - 1].turn : 400;

      let maxScore = 1;
      const teamSeries = [];
      for (let t = 0; t < teams; t++) {
        teamSeries.push({
          team: t,
          name: (replayObj.names && replayObj.names[t]) ? replayObj.names[t] : ('阵营' + t),
          color: C[t % 15],
          points: [],
          captures: []
        });
      }

      for (let fIdx = 0; fIdx < frames.length; fIdx++) {
        const f = frames[fIdx];
        const turn = f.turn;
        for (let t = 0; t < teams; t++) {
          const sc = f.score[t];
          if (sc > maxScore) maxScore = sc;
          teamSeries[t].points.push({ frame: fIdx, turn: turn, score: sc });
        }
        for (const e of f.events) {
          if (e.type === 'capture') {
            const t = e.team;
            if (teamSeries[t]) {
              teamSeries[t].captures.push({
                frame: fIdx,
                turn: turn,
                score: f.score[t],
                unit: e.unit,
                flag: e.flag
              });
            }
          }
        }
      }

      return {
        teams,
        maxTurn: Math.max(maxTurn, 100),
        maxScore: Math.max(maxScore, 3), // 至少 3 档刻度以保持天体纵深感
        teamSeries,
        starfield: generateStarfield(120)
      };
    }

    function switchScoreTab(tab) {
      currentScoreTab = tab;
      const isList = (tab === 'list');
      
      const btnScores = $('tab-btn-scores');
      const btnCelestial = $('tab-btn-celestial');
      if (btnScores && btnCelestial) {
        btnScores.className = isList ? 
          'px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-blue-600 text-white shadow-sm' :
          'px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-[#8ca0ba] hover:text-[#f0f6fc]';
        btnCelestial.className = !isList ? 
          'px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-purple-600 text-white shadow-sm' :
          'px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-[#8ca0ba] hover:text-[#f0f6fc]';
      }

      const pList = $('score-pane-list');
      const pCel = $('score-pane-celestial');
      if (pList) pList.classList.toggle('hidden', !isList);
      if (pCel) pCel.classList.toggle('hidden', isList);

      const hBadge = $('score-header-badge');
      const cControls = $('celestial-controls');
      if (hBadge) hBadge.classList.toggle('hidden', !isList);
      if (cControls) cControls.classList.toggle('hidden', isList);

      if (!isList) {
        resizeCelestialCanvas();
        renderCelestialChart();
      }
    }

    function toggleCelestialMode() {
      celestialMode = (celestialMode === 'timeline' ? 'polar' : 'timeline');
      const icon = $('celestial-mode-icon');
      const text = $('celestial-mode-text');
      const hint = $('celestial-coord-hint');
      if (celestialMode === 'timeline') {
        if (icon) icon.textContent = '📈';
        if (text) text.textContent = '时序星轨';
        if (hint) hint.textContent = 'α: 回合 (Turn) · δ: 进球 (Score)';
      } else {
        if (icon) icon.textContent = '🧭';
        if (text) text.textContent = '环轨星盘';
        if (hint) hint.textContent = 'θ: 时序角方位 · r: 天体能级轨道';
      }
      renderCelestialChart();
    }

    function resetCelestialFocus() {
      focus = -1;
      render();
    }

    function resizeCelestialCanvas() {
      const cv = $('celestial-canvas');
      if (!cv) return;
      const rect = cv.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const w = Math.floor(rect.width);
      const h = Math.floor(rect.height);
      if (w <= 0 || h <= 0) return;
      if (cv.width !== w * dpr || cv.height !== h * dpr) {
        cv.width = w * dpr;
        cv.height = h * dpr;
      }
    }

    function drawSupernova(ctx, x, y, color, size, pulse) {
      ctx.save();
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = color;
      ctx.shadowBlur = pulse ? 12 : 6;

      const spike = size * 2.2;
      const inner = size * 0.45;
      ctx.beginPath();
      for (let k = 0; k < 8; k++) {
        const a = (Math.PI / 4) * k;
        const r = (k % 2 === 0) ? spike : inner;
        const px = x + r * Math.cos(a);
        const py = y + r * Math.sin(a);
        if (k === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.closePath();
      ctx.fill();

      if (pulse) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(x, y, size * 2.8, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();
    }

    function renderCelestialChart() {
      const cv = $('celestial-canvas');
      if (!cv || !R || !R.frames || !R.frames[i]) return;
      const g = cv.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const W = cv.width / dpr;
      const H = cv.height / dpr;
      if (W <= 0 || H <= 0) return;

      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.clearRect(0, 0, W, H);

      if (!CELESTIAL_DATA) {
        CELESTIAL_DATA = prepareCelestialData(R);
      }
      if (!CELESTIAL_DATA) return;

      const curFrame = R.frames[i];
      const curTurn = curFrame ? curFrame.turn : 0;
      const maxTurn = CELESTIAL_DATA.maxTurn;
      const maxScore = CELESTIAL_DATA.maxScore;

      const scanInd = $('celestial-scan-indicator');
      if (scanInd) {
        scanInd.textContent = `T${curTurn} / ${maxTurn} · ${celestialMode === 'timeline' ? '天球子午线' : '极轨测角仪'}`;
      }

      if (celestialMode === 'timeline') {
        renderCelestialTimeline(g, W, H, curTurn, maxTurn, maxScore);
      } else {
        renderCelestialPolar(g, W, H, curTurn, maxTurn, maxScore);
      }
    }

    function renderCelestialTimeline(g, W, H, curTurn, maxTurn, maxScore) {
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
      if (CELESTIAL_DATA.starfield) {
        for (let k = 0; k < CELESTIAL_DATA.starfield.length; k++) {
          const st = CELESTIAL_DATA.starfield[k];
          const pulse = 0.4 + 0.6 * Math.sin(st.flicker + i * st.speed);
          g.fillStyle = `rgba(200, 225, 255, ${(st.alpha * pulse).toFixed(2)})`;
          g.fillRect(st.x * W, st.y * H, st.r, st.r);
        }
      }

      // 3. 天体坐标系网格 (水平得分刻度线)
      g.save();
      g.setLineDash([3, 4]);
      g.lineWidth = 1;
      for (let s = 0; s <= maxScore; s++) {
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
      }

      // 垂直回合刻度线
      const turnStep = maxTurn > 250 ? 100 : (maxTurn > 100 ? 50 : 25);
      g.setLineDash([2, 4]);
      g.strokeStyle = 'rgba(56, 189, 248, 0.07)';
      g.fillStyle = '#64748b';
      g.font = '9px monospace';
      g.textAlign = 'center';
      g.textBaseline = 'top';
      for (let t = 0; t <= maxTurn; t += turnStep) {
        const x = mapX(t);
        g.beginPath();
        g.moveTo(x, padT);
        g.lineTo(x, H - padB);
        g.stroke();
        g.fillText('T' + t, x, H - padB + 5);
      }
      g.restore();

      // 4. 各阵营星轨轨迹与进球超新星
      const sortedTeams = [...CELESTIAL_DATA.teamSeries].sort((a, b) => {
        if (a.team === focus) return 1;
        if (b.team === focus) return -1;
        return (R.frames[i].score[a.team] || 0) - (R.frames[i].score[b.team] || 0);
      });

      sortedTeams.forEach(tm => {
        const isTarget = (focus === -1 || focus === tm.team);
        const alpha = isTarget ? 1 : 0.16;
        const lineWidth = (focus === tm.team) ? 2.6 : (isTarget ? 1.6 : 1.0);

        // 未来星轨 (虚线命运线)
        if (isTarget) {
          g.save();
          g.strokeStyle = tm.color;
          g.globalAlpha = alpha * 0.22;
          g.lineWidth = lineWidth * 0.85;
          g.setLineDash([2, 4]);
          g.beginPath();
          for (let k = 0; k < tm.points.length; k++) {
            const pt = tm.points[k];
            const px = mapX(pt.turn);
            const py = mapY(pt.score);
            if (k === 0) g.moveTo(px, py);
            else g.lineTo(px, py);
          }
          g.stroke();
          g.restore();
        }

        // 当前推演星轨 (实线光弧)
        g.save();
        g.strokeStyle = tm.color;
        g.globalAlpha = alpha;
        g.lineWidth = lineWidth;
        g.setLineDash([]);
        if (isTarget && focus === tm.team) {
          g.shadowColor = tm.color;
          g.shadowBlur = 8;
        }
        g.beginPath();
        let ptsCount = 0;
        for (let k = 0; k <= i && k < tm.points.length; k++) {
          const pt = tm.points[k];
          const px = mapX(pt.turn);
          const py = mapY(pt.score);
          if (k === 0) g.moveTo(px, py);
          else g.lineTo(px, py);
          ptsCount++;
        }
        if (ptsCount > 0) g.stroke();
        g.restore();

        // 进球超新星 ⭐
        tm.captures.forEach(cap => {
          const capX = mapX(cap.turn);
          const capY = mapY(cap.score);
          const hasOccurred = (cap.frame <= i);
          if (hasOccurred) {
            const isPulse = (i >= cap.frame && i <= cap.frame + 5);
            g.globalAlpha = isTarget ? 1 : 0.2;
            drawSupernova(g, capX, capY, tm.color, isPulse ? 6.5 : 4.5, isPulse);
          } else if (isTarget) {
            // 未来的星云进球锚点
            g.save();
            g.strokeStyle = tm.color;
            g.globalAlpha = alpha * 0.25;
            g.beginPath();
            g.arc(capX, capY, 2.5, 0, Math.PI * 2);
            g.stroke();
            g.restore();
          }
        });
      });

      // 5. 实时扫描天球子午线 (Meridian Beam)
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

      // 子午线顶部天极标识
      g.fillStyle = '#38bdf8';
      g.beginPath();
      g.arc(scanX, padT - 4, 2.5, 0, Math.PI * 2);
      g.fill();
      g.restore();

      // 6. 子午线上的各阵营实时行星球 (Planetary Orbs)
      sortedTeams.forEach(tm => {
        const curScore = R.frames[i].score[tm.team];
        const orbX = scanX;
        const orbY = mapY(curScore);
        const isTargetTm = (focus === -1 || focus === tm.team);

        g.save();
        g.globalAlpha = isTargetTm ? 1 : 0.2;
        if (focus === tm.team) {
          // 聚焦时的天体瞄准十字准星与准度框
          g.strokeStyle = '#38bdf8';
          g.lineWidth = 1;
          g.beginPath();
          g.arc(orbX, orbY, 7.5, 0, Math.PI * 2);
          g.stroke();
          g.strokeRect(orbX - 9, orbY - 9, 18, 18);
        }
        g.fillStyle = tm.color;
        g.shadowColor = tm.color;
        g.shadowBlur = 8;
        g.beginPath();
        g.arc(orbX, orbY, focus === tm.team ? 4.8 : 3.2, 0, Math.PI * 2);
        g.fill();
        g.restore();
      });
    }

    function renderCelestialPolar(g, W, H, curTurn, maxTurn, maxScore) {
      const cx = W / 2;
      const cy = (H - 8) / 2;
      const maxRadius = Math.min(W - 40, H - 36) / 2;
      const minRadius = 22;

      const mapPolar = (turn, score) => {
        const angle = -Math.PI / 2 + (turn / maxTurn) * (Math.PI * 2);
        const r = minRadius + (score / maxScore) * (maxRadius - minRadius);
        return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), angle, r };
      };

      // 1. 深空背景
      const grad = g.createRadialGradient(cx, cy, 10, cx, cy, maxRadius + 20);
      grad.addColorStop(0, '#0e182f');
      grad.addColorStop(0.5, '#070c17');
      grad.addColorStop(1, '#03050a');
      g.fillStyle = grad;
      g.fillRect(0, 0, W, H);

      // 2. 背景微星星表
      if (CELESTIAL_DATA.starfield) {
        for (let k = 0; k < CELESTIAL_DATA.starfield.length; k++) {
          const st = CELESTIAL_DATA.starfield[k];
          const pulse = 0.4 + 0.6 * Math.sin(st.flicker + i * st.speed);
          g.fillStyle = `rgba(200, 225, 255, ${(st.alpha * pulse).toFixed(2)})`;
          g.fillRect(st.x * W, st.y * H, st.r, st.r);
        }
      }

      // 3. 星盘同心能级轨道层
      g.save();
      g.lineWidth = 1;
      for (let s = 0; s <= maxScore; s++) {
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
      }

      // 象限径向射线 (0, 90, 180, 270 度)
      g.setLineDash([2, 4]);
      g.strokeStyle = 'rgba(56, 189, 248, 0.08)';
      for (let ang = 0; ang < Math.PI * 2; ang += Math.PI / 2) {
        g.beginPath();
        g.moveTo(cx, cy);
        g.lineTo(cx + maxRadius * Math.cos(ang), cy + maxRadius * Math.sin(ang));
        g.stroke();
      }
      g.restore();

      // 4. 银心核心天体 (Galactic Core)
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

      // 5. 各阵营螺旋旋臂轨迹
      const sortedTeams = [...CELESTIAL_DATA.teamSeries].sort((a, b) => {
        if (a.team === focus) return 1;
        if (b.team === focus) return -1;
        return (R.frames[i].score[a.team] || 0) - (R.frames[i].score[b.team] || 0);
      });

      sortedTeams.forEach(tm => {
        const isTarget = (focus === -1 || focus === tm.team);
        const alpha = isTarget ? 1 : 0.16;
        const lineWidth = (focus === tm.team) ? 2.5 : (isTarget ? 1.5 : 1.0);

        // 未来星轨螺旋
        if (isTarget) {
          g.save();
          g.strokeStyle = tm.color;
          g.globalAlpha = alpha * 0.22;
          g.lineWidth = lineWidth * 0.85;
          g.setLineDash([2, 4]);
          g.beginPath();
          for (let k = 0; k < tm.points.length; k++) {
            const pt = tm.points[k];
            const pos = mapPolar(pt.turn, pt.score);
            if (k === 0) g.moveTo(pos.x, pos.y);
            else g.lineTo(pos.x, pos.y);
          }
          g.stroke();
          g.restore();
        }

        // 当前已推演星轨
        g.save();
        g.strokeStyle = tm.color;
        g.globalAlpha = alpha;
        g.lineWidth = lineWidth;
        g.setLineDash([]);
        if (isTarget && focus === tm.team) {
          g.shadowColor = tm.color;
          g.shadowBlur = 8;
        }
        g.beginPath();
        let ptsCount = 0;
        for (let k = 0; k <= i && k < tm.points.length; k++) {
          const pt = tm.points[k];
          const pos = mapPolar(pt.turn, pt.score);
          if (k === 0) g.moveTo(pos.x, pos.y);
          else g.lineTo(pos.x, pos.y);
          ptsCount++;
        }
        if (ptsCount > 0) g.stroke();
        g.restore();

        // 超新星爆发 ⭐
        tm.captures.forEach(cap => {
          const pos = mapPolar(cap.turn, cap.score);
          const hasOccurred = (cap.frame <= i);
          if (hasOccurred) {
            const isPulse = (i >= cap.frame && i <= cap.frame + 5);
            g.globalAlpha = isTarget ? 1 : 0.2;
            drawSupernova(g, pos.x, pos.y, tm.color, isPulse ? 6.5 : 4.5, isPulse);
          } else if (isTarget) {
            g.save();
            g.strokeStyle = tm.color;
            g.globalAlpha = alpha * 0.25;
            g.beginPath();
            g.arc(pos.x, pos.y, 2.5, 0, Math.PI * 2);
            g.stroke();
            g.restore();
          }
        });
      });

      // 6. 测角雷达扫描指针 (Astrolabe Rule)
      const curAngle = -Math.PI / 2 + (curTurn / maxTurn) * (Math.PI * 2);
      g.save();
      g.strokeStyle = 'rgba(56, 189, 248, 0.7)';
      g.lineWidth = 1.5;
      g.beginPath();
      g.moveTo(cx, cy);
      g.lineTo(cx + (maxRadius + 6) * Math.cos(curAngle), cy + (maxRadius + 6) * Math.sin(curAngle));
      g.stroke();

      // 外环刻度指示珠
      g.fillStyle = '#38bdf8';
      g.beginPath();
      g.arc(cx + (maxRadius + 6) * Math.cos(curAngle), cy + (maxRadius + 6) * Math.sin(curAngle), 2.5, 0, Math.PI * 2);
      g.fill();
      g.restore();

      // 7. 测角指针上的各阵营行星星体
      sortedTeams.forEach(tm => {
        const curScore = R.frames[i].score[tm.team];
        const r = minRadius + (curScore / maxScore) * (maxRadius - minRadius);
        const orbX = cx + r * Math.cos(curAngle);
        const orbY = cy + r * Math.sin(curAngle);
        const isTargetTm = (focus === -1 || focus === tm.team);

        g.save();
        g.globalAlpha = isTargetTm ? 1 : 0.2;
        if (focus === tm.team) {
          g.strokeStyle = '#38bdf8';
          g.lineWidth = 1;
          g.beginPath();
          g.arc(orbX, orbY, 7.5, 0, Math.PI * 2);
          g.stroke();
        }
        g.fillStyle = tm.color;
        g.shadowColor = tm.color;
        g.shadowBlur = 8;
        g.beginPath();
        g.arc(orbX, orbY, focus === tm.team ? 4.8 : 3.2, 0, Math.PI * 2);
        g.fill();
        g.restore();
      });
    }

    // 交互监听与 HUD 提示
    function setupCelestialEventListeners() {
      const cv = $('celestial-canvas');
      if (!cv) return;

      cv.addEventListener('mousemove', handleCelestialHover);
      cv.addEventListener('mouseleave', hideCelestialHud);
      cv.addEventListener('click', handleCelestialClick);

      window.addEventListener('resize', () => {
        if (currentScoreTab === 'celestial') {
          resizeCelestialCanvas();
          renderCelestialChart();
        }
      });
    }

    function hideCelestialHud() {
      const hud = $('celestial-hud');
      if (hud) hud.classList.add('hidden');
    }

    function handleCelestialHover(e) {
      const cv = $('celestial-canvas');
      if (!cv || !CELESTIAL_DATA || !R || !R.frames) return;
      const rect = cv.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let hoverTurn = 0;
      let closestTeam = 0;

      if (celestialMode === 'timeline') {
        const padL = 34, padR = 20, padT = 18, padB = 26;
        const plotW = rect.width - padL - padR;
        const plotH = rect.height - padT - padB;
        if (mx < padL - 8 || mx > rect.width - padR + 8 || my < padT - 8 || my > rect.height - padB + 8) {
          hideCelestialHud();
          return;
        }
        const ratio = Math.max(0, Math.min(1, (mx - padL) / plotW));
        hoverTurn = Math.round(ratio * CELESTIAL_DATA.maxTurn);
        const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
        const frameAtT = R.frames[fIdx];
        if (!frameAtT) return;

        let minDy = Infinity;
        for (let t = 0; t < R.header.teams; t++) {
          const sc = frameAtT.score[t];
          const py = padT + (1 - sc / CELESTIAL_DATA.maxScore) * plotH;
          const dy = Math.abs(my - py);
          if (dy < minDy) {
            minDy = dy;
            closestTeam = t;
          }
        }
      } else {
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
        for (let t = 0; t < R.header.teams; t++) {
          const sc = frameAtT.score[t];
          const tr = minRadius + (sc / CELESTIAL_DATA.maxScore) * (maxRadius - minRadius);
          const dr = Math.abs(r - tr);
          if (dr < minDr) {
            minDr = dr;
            closestTeam = t;
          }
        }
      }

      // 获取对应帧与技术信息
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
        <span class="w-2.5 h-2.5 rounded-full inline-block" style="background:${tmColor}"></span>
        <span>${tmName}</span>
        <span class="text-cyan-400 font-mono text-[10px]">T${frameAtT.turn}</span>
      `;

      desc.innerHTML = `
        <div class="flex items-center justify-between gap-3">
          <span>当前得分:</span>
          <b class="text-emerald-400 font-bold">${score} 进球</b>
        </div>
        ${capNear ? `<div class="text-yellow-400 font-bold mt-1 flex items-center gap-1"><span>⭐</span><span>交旗进球时刻!</span></div>` : ''}
      `;

      const hudW = 160;
      let left = mx - hudW / 2;
      if (left < 8) left = 8;
      if (left + hudW > rect.width - 8) left = rect.width - hudW - 8;
      let top = my - 62;
      if (top < 8) top = my + 14;

      hud.style.left = `${left}px`;
      hud.style.top = `${top}px`;
      hud.classList.remove('hidden');
    }

    function handleCelestialClick(e) {
      const cv = $('celestial-canvas');
      if (!cv || !CELESTIAL_DATA || !R || !R.frames) return;
      const rect = cv.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let ratio = 0;
      let clickedTeam = -1;

      if (celestialMode === 'timeline') {
        const padL = 34, padR = 20, padT = 18, padB = 26;
        const plotW = rect.width - padL - padR;
        const plotH = rect.height - padT - padB;
        if (mx >= padL - 8 && mx <= rect.width - padR + 8) {
          ratio = Math.max(0, Math.min(1, (mx - padL) / plotW));
        }
        const fIdx = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
        const frameAtT = R.frames[fIdx];
        if (frameAtT) {
          let minDy = Infinity;
          for (let t = 0; t < R.header.teams; t++) {
            const sc = frameAtT.score[t];
            const py = padT + (1 - sc / CELESTIAL_DATA.maxScore) * plotH;
            const dy = Math.abs(my - py);
            if (dy < 18 && dy < minDy) {
              minDy = dy;
              clickedTeam = t;
            }
          }
        }
      } else {
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
        if (frameAtT) {
          let minDr = Infinity;
          for (let t = 0; t < R.header.teams; t++) {
            const sc = frameAtT.score[t];
            const tr = minRadius + (sc / CELESTIAL_DATA.maxScore) * (maxRadius - minRadius);
            const dr = Math.abs(r - tr);
            if (dr < 18 && dr < minDr) {
              minDr = dr;
              clickedTeam = t;
            }
          }
        }
      }

      // 跳转对应帧
      const targetFrame = Math.min(R.frames.length - 1, Math.max(0, Math.round(ratio * (R.frames.length - 1))));
      go(targetFrame);

      // 如果点在队伍轨迹/星体附近，切换队伍聚焦
      if (clickedTeam >= 0) {
        focus = (focus === clickedTeam ? -1 : clickedTeam);
      }
      render();
    }

    // 初始化/渲染对局 List 列表 (支持无限场次扩展)
    function renderMatchList() {
      const container = $('match-list-container');
      const kw = currentSearchKeyword.toLowerCase().trim();
      let count = 0;
      let html = '';

      for (const [key, cfg] of Object.entries(ALL_GAMES)) {
        const teamsCount = cfg.replay?.header?.teams || 0;
        
        // 分类过滤
        if (currentFilter !== 'all' && String(teamsCount) !== currentFilter) {
          continue;
        }

        // 搜索关键词过滤
        if (kw) {
          const text = (cfg.id + ' ' + cfg.tag + ' ' + cfg.title + ' ' + cfg.desc + ' ' + (cfg.replay?.names || []).join(' ')).toLowerCase();
          if (!text.includes(kw)) continue;
        }

        count++;
        const stats = cfg.enhanced_stats || cfg.replay?.enhanced_stats || [];
        const topModel = stats[0]?.name || '胜者决出';
        const topScore = stats[0]?.score || 0;
        const isActive = (key === activeKey);

        html += `
          <div onclick="selectGame('${key}')" id="match-row-${key}" 
               class="match-item p-2.5 sm:p-3 rounded-xl cursor-pointer flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 select-none ${isActive ? 'active' : ''}">
            <div class="flex items-start sm:items-center gap-2.5 flex-1 min-w-0">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#212e42] text-blue-400 border border-[#354866] whitespace-nowrap">
                ${cfg.badge.split('·')[0].trim()}
              </span>
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <h4 class="text-xs sm:text-sm font-bold text-[#f0f6fc] truncate">${cfg.title}</h4>
                  <span class="text-[10px] font-mono text-[#8ca0ba]">${cfg.id}</span>
                </div>
                <p class="text-[11px] text-[#8ca0ba] line-clamp-1 mt-0.5">${cfg.desc}</p>
              </div>
            </div>

            <div class="flex items-center justify-between sm:justify-end gap-3 w-full sm:w-auto text-xs border-t sm:border-t-0 border-[#1e2a3b] pt-1.5 sm:pt-0">
              <div class="text-right">
                <span class="text-[11px] text-[#8ca0ba]">终盘头名:</span>
                <span class="font-bold text-yellow-400 ml-1">${topModel}</span>
              </div>
              <span class="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono font-bold border border-emerald-500/20 whitespace-nowrap">
                ${topScore} 进球
              </span>
              <span class="text-xs ${isActive ? 'text-blue-400 font-bold' : 'text-transparent'}">●</span>
            </div>
          </div>
        `;
      }

      container.innerHTML = html || '<div class="py-6 text-center text-xs text-[#8ca0ba]">无匹配对局，请尝试更换筛选条件</div>';
      $('match-count-badge').textContent = `已筛选 ${count} 场 / 共 ${Object.keys(ALL_GAMES).length} 场`;
    }

    function setFilter(type) {
      currentFilter = type;
      document.querySelectorAll('.filter-btn').forEach(btn => {
        if (btn.dataset.filter === type) {
          btn.className = 'filter-btn px-3 py-1 rounded-lg bg-blue-600 text-white font-semibold transition';
        } else {
          btn.className = 'filter-btn px-3 py-1 rounded-lg bg-[#111822] text-[#8ca0ba] hover:text-[#f0f6fc] border border-[#26354a] transition';
        }
      });
      renderMatchList();
    }

    function selectGame(key) {
      if (activeKey === key) return;
      activeKey = key;
      R = ALL_GAMES[activeKey].replay;
      pausePlay();
      i = 0;
      focus = -1;
      renderMatchList();
      loadGameToViewer();
    }

    function loadGameToViewer() {
      const cfg = ALL_GAMES[activeKey];
      $('map-badge').innerText = `${R.header.size}×${R.header.size} 地图 · ${R.header.teams} 阵营`;
      $('current-title-label').innerText = `${cfg.title} (${cfg.id})`;
      $('seek').max = R.frames.length - 1;
      $('seek').value = 0;

      // 实时计算预装载当前对局的逐回合累加统计
      CUM_STATS = computeCumulativeStats(R);
      CELESTIAL_DATA = prepareCelestialData(R);
      if (currentScoreTab === 'celestial') {
        resizeCelestialCanvas();
      }

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

      render();
    }

    // 渲染实时动态 KDA 表格与高能数据卡片 (依据当前 frame 的实时累计数据)
    function renderKdaTable(stats) {
      const tbody = $('kda-tbody');
      const cards = $('kda-highlight-cards');
      const f = R.frames[i];
      const maxTurn = (R.frames[R.frames.length - 1] ? R.frames[R.frames.length - 1].turn : 400);

      $('kda-turn-badge').textContent = `当前回合: T${f.turn} / ${maxTurn}`;

      if (!stats || !stats.length) {
        tbody.innerHTML = '<tr><td colspan="11" class="py-6 text-center text-[#8ca0ba]">暂无实时技术统计数据</td></tr>';
        if (cards) cards.innerHTML = '';
        return;
      }

      // 计算本回合实时高光之星
      const topScore = [...stats].sort((a,b) => b.score - a.score)[0];
      const topKills = [...stats].sort((a,b) => b.kills - a.kills)[0];
      const topCK = [...stats].sort((a,b) => b.carrier_kills - a.carrier_kills)[0];
      const topKDA = [...stats].sort((a,b) => b.kda - a.kda)[0];

      if (cards) {
        cards.innerHTML = `
          <div class="p-3 bg-[#111822] rounded-xl border border-[#26354a]">
            <div class="text-[#8ca0ba] text-[11px] flex justify-between">
              <span>👑 实时得分王</span>
              <span class="text-emerald-400 font-bold">${topScore.score} 进球</span>
            </div>
            <div class="text-sm font-bold text-yellow-400 mt-1 truncate">${topScore.name}</div>
            <div class="text-[11px] text-[#8ca0ba] mt-0.5">转化率 ${topScore.capture_rate}% (${topScore.pickups} 捡旗)</div>
          </div>

          <div class="p-3 bg-[#111822] rounded-xl border border-[#26354a]">
            <div class="text-[#8ca0ba] text-[11px] flex justify-between">
              <span>⚔️ 实时杀神</span>
              <span class="text-red-400 font-bold">${topKills.kills} 击杀</span>
            </div>
            <div class="text-sm font-bold text-red-400 mt-1 truncate">${topKills.name}</div>
            <div class="text-[11px] text-[#8ca0ba] mt-0.5">${topKills.assists} 助攻 · ${topKills.deaths} 阵亡</div>
          </div>

          <div class="p-3 bg-[#111822] rounded-xl border border-[#26354a]">
            <div class="text-[#8ca0ba] text-[11px] flex justify-between">
              <span>🛡️ 实时断旗截杀</span>
              <span class="text-amber-400 font-bold">${topCK.carrier_kills} 断旗杀</span>
            </div>
            <div class="text-sm font-bold text-amber-400 mt-1 truncate">${topCK.name}</div>
            <div class="text-[11px] text-[#8ca0ba] mt-0.5">拦截敌方持旗突防</div>
          </div>

          <div class="p-3 bg-[#111822] rounded-xl border border-[#26354a]">
            <div class="text-[#8ca0ba] text-[11px] flex justify-between">
              <span>📊 实时最佳 KDA</span>
              <span class="text-cyan-400 font-bold">${topKDA.kda} 战损比</span>
            </div>
            <div class="text-sm font-bold text-cyan-400 mt-1 truncate">${topKDA.name}</div>
            <div class="text-[11px] text-[#8ca0ba] mt-0.5">${topKDA.kills}杀 / ${topKDA.deaths}死</div>
          </div>
        `;
      }

      let html = '';
      stats.forEach((st, rank) => {
        const isTop = (rank === 0 && st.score > 0);
        const color = C[st.team % 15];
        
        let badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-gray-500/10 text-gray-400">稳定发挥</span>';
        if (isTop) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-yellow-500/10 text-yellow-400 font-bold">👑 当前领跑</span>';
        else if (st.kills >= 15) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-red-500/10 text-red-400 font-bold">⚔️ 杀神</span>';
        else if (st.capture_rate >= 75 && st.score >= 3) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 font-bold">🎯 高效护送</span>';
        else if (st.carrier_kills >= 5) badge = '<span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-400 font-bold">🛡️ 铁壁截断</span>';

        html += `
          <tr class="hover:bg-[#16202e] transition ${isTop ? 'bg-blue-500/5' : ''}">
            <td class="py-2.5 px-3 text-center font-bold ${rank < 3 ? 'text-yellow-400' : 'text-[#8ca0ba]'}">${rank + 1}</td>
            <td class="py-2.5 px-3 font-sans font-bold flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full inline-block flex-shrink-0" style="background:${color}"></span>
              <span class="${isTop ? 'text-blue-400' : 'text-[#f0f6fc]'} truncate">${st.name}</span>
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-emerald-400 text-sm">${st.score}</td>
            <td class="py-2.5 px-3 text-right text-[#f0f6fc]">${st.pickups}</td>
            <td class="py-2.5 px-3 text-right text-cyan-400">${st.capture_rate}%</td>
            <td class="py-2.5 px-3 text-right font-bold text-red-400">${st.kills}</td>
            <td class="py-2.5 px-3 text-right text-[#8ca0ba]">${st.assists}</td>
            <td class="py-2.5 px-3 text-right text-amber-400 font-bold">${st.carrier_kills}</td>
            <td class="py-2.5 px-3 text-right text-[#8ca0ba]">${st.deaths}</td>
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

      // 实时动态渲染 KDA 表格与高能数据卡片
      if (CUM_STATS && CUM_STATS[i]) {
        renderKdaTable(CUM_STATS[i]);
      }

      // 实时动态同步渲染比分走势天体图 (若当前处于天体图 Tab)
      if (currentScoreTab === 'celestial') {
        renderCelestialChart();
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

      const searchInput = $('match-search');
      if (searchInput) {
        searchInput.oninput = e => {
          currentSearchKeyword = e.target.value;
          renderMatchList();
        };
      }

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
      setupCelestialEventListeners();
      renderMatchList();
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
print("Successfully generated upgraded index.html with Real-time KDA and Match List view!")
