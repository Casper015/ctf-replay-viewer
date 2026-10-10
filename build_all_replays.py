import json
import sys
from pathlib import Path

HERE = Path(r"C:\Users\caspe\OneDrive\Code\AI_Test\ctf-stress-pack")
sys.path.insert(0, str(HERE.resolve()))
sys.path.insert(0, str((HERE / "arena").resolve()))
import engine
import run_stress

cxx = run_stress.detect_compiler()
commands = run_stress.compile_all(cxx)
sched = {s['id']: s for s in (json.loads(l) for l in open(HERE / 'schedule.jsonl', encoding='utf-8'))}

game_configs = [
    # --- 15 人超级决战 ---
    {
        'key': 'g15_rec',
        'id': 'sz15-m055282',
        'tag': '15人·90球历史纪录战',
        'badge': '15人 · 49×49 地图 · 45角色',
        'title': '全赛程最高 90 进球纪录！三大顶流 14:13:13 压哨绝杀',
        'desc': '45 个单位在中场爆发 90 次夺旗破门。Sonnet 5.5 后程发力，以 14:13:13 的 1 分微弱优势从 Player5 与 Astra 手中压哨夺得头名！'
    },
    {
        'key': 'g15_p5',
        'id': 'sz15-m057668',
        'tag': '15人·个人16球暴走',
        'badge': '15人 · 49×49 地图 · 45角色',
        'title': 'GPT-6.1 Sol 独揽 16 分全场暴走！全盘 84 次交旗惨烈拼杀',
        'desc': 'Sol 展现恐怖护送转化率单人拿下 16 球，Player5、Astra、Player4 全力夹击，全场 45 单位爆发 84 次破门。'
    },

    # --- 8 人激战（精选 3 场高能看点局） ---
    {
        'key': 'g8_record',
        'id': 'sz08-m040053',
        'tag': '8人·70球破门纪录战',
        'badge': '8人 · 41×41 地图 · 24角色',
        'title': '四大金刚集体破门上双！Opus(13) vs Astra(12) vs Sol(11) vs DeepSeek(10)',
        'desc': '全赛程 8 人局总进球纪录！8 大主力密集对抗，总得分高达 70 分，前四名全部拿下两位数进球，攻防节奏窒息拉满。'
    },
    {
        'key': 'g8_astra_opus',
        'id': 'sz08-m037636',
        'tag': '8人·15:14神魔大战',
        'badge': '8人 · 41×41 地图 · 24角色',
        'title': 'Astra(15) 压哨 1 分险胜 Opus(14)！四大模型全破 10 分火拼',
        'desc': '64 次破门高潮迭起！Astra 与 Opus 5.5 展开门前对攻拉锯战，Fable(12) 与 Player5(11) 紧追不舍，最终 Astra 1 分险胜！'
    },
    {
        'key': 'g8_p5_sol',
        'id': 'sz08-m041527',
        'tag': '8人·冠亚军 1 分死斗',
        'badge': '8人 · 41×41 地图 · 24角色',
        'title': '总天梯冠亚军正面对决！Player5(13) 终盘 1 分险胜 Sol(12)',
        'desc': '天梯排名第 1 的 Player5 迎战第 2 的 GPT-6.1 Sol！双方互掐到最后一回合，Player5 凭借稳健防守以 13:12 终盘力克 Sol。'
    },

    # --- 4 人交锋（精选 4 场高能看点局） ---
    {
        'key': 'g4_record',
        'id': 'sz04-m015252',
        'tag': '4人·53球破门纪录战',
        'badge': '4人 · 31×31 地图 · 12角色',
        'title': 'Astra 狂轰 18 进球统治全场！四大核心打出 53 球纪录',
        'desc': '全赛程 4 人局最高进球纪录！Astra 爆发单兵顶级侵略性独进 18 球，Sol(14) 与 Player5(13) 全力阻击，战况激烈窒息。'
    },
    {
        'key': 'g4_duel',
        'id': 'sz04-m016157',
        'tag': '4人·18:17双雄死斗',
        'badge': '4人 · 31×31 地图 · 12角色',
        'title': '史诗双雄交锋！Player5(18) vs GPT-6.1 Sol(17) 1 球绝杀',
        'desc': '天梯前二两强包揽全场 35 球！比分全程交替上升，直到第 395 回合 Player5 门前断旗反击以 18:17 压哨锁定胜局！'
    },
    {
        'key': 'g4_tie',
        'id': 'sz04-m021109',
        'tag': '4人·16:16巅峰握手',
        'badge': '4人 · 31×31 地图 · 12角色',
        'title': '巅峰对决双冠军！Player5(16) 与 GPT-6 Astra(16) 握手言和',
        'desc': '总进球达 51 球！Player5 与 Astra 在 31×31 地图展开狂暴换家拉锯，终场打出极其罕见的 16:16 双雄平局神作！'
    },
    {
        'key': 'g4_three_way',
        'id': 'sz04-m016034',
        'tag': '4人·12:12:12三足鼎立',
        'badge': '4人 · 31×31 地图 · 12角色',
        'title': '三足鼎立奇迹战！Fable(12) = DeepSeek(12) = Sol(12)',
        'desc': '极其戏剧性的三队并列第一！Fable 5.1、DeepSeek V4.1 与 GPT-6.1 Sol 各自斩获 12 进球，攻防博弈形成完美的三角牵制！'
    },

    # --- 3 人 / 2 人 经典对局 ---
    {
        'key': 'g3',
        'id': 'sz03-m012514',
        'tag': '3人·7分逆风大翻盘',
        'badge': '3人 · 31×31 地图 · 9角色',
        'title': '半程落后 7 分！Fable 5.1(17) 绝地反超 Sol(16) & P1(14)',
        'desc': '半程 Sol 狂取 12 分建立 7 分巨大领跑优势，Fable 5.1 在后半程连抢 12 分，在终场第 390 回合反超 1 分完成史诗逆转。'
    },
    {
        'key': 'g2',
        'id': 'sz02-m006122',
        'tag': '2人·60球单挑拉锯',
        'badge': '2人 · 23×23 地图 · 6角色',
        'title': '60 次夺旗进球！Player5(31) vs Opus 5.5(29) 10 次更迭绝杀',
        'desc': '全场 400 回合打满，平均每 6.6 回合进球一次！第 260 回合 Opus 曾领先 4 分，Player5 在第 392 回合门前绝杀断旗逆风翻盘。'
    }
]

def generate_replay_dict(gid):
    s = sched[gid]
    size, map_seed, flag_seed, seats = s['size'], s['map_seed'], s['flag_seed'], s['seats']
    class FrozenGame(engine.Game):
        def __init__(self, n, seed):
            super().__init__(n, seed, flag_seed=flag_seed)
    game = FrozenGame(size, map_seed)
    bots = [run_stress.StressBot(commands[n], n, "record") for n in seats]
    
    frames = [game.frame()]
    try:
        while not game.done:
            turn = game.turn + 1
            starts = [b.send(game.encode(i)) for i, b in enumerate(bots)]
            orders = {}
            for i, (b, st) in enumerate(zip(bots, starts)):
                line = b.receive(st)
                if line is None:
                    orders[i] = {}
                    continue
                try:
                    orders[i] = game.decode(i, line)
                    b.strikes = 0
                except ValueError:
                    orders[i] = {}
            game.step(orders)
            frames.append(game.frame(orders=orders))
    finally:
        for b in bots:
            b.close()
            
    result = game.result()
    reps = [b.report() for b in bots]
    result.update(seed=map_seed, flag_seed=flag_seed, names=list(seats), bots=reps)
    
    # 逐帧精确提取技术统计与 KDA 计算
    stats_map = {t: {'name': name, 'kills': 0, 'assists': 0, 'carrier_kills': 0, 'deaths': 0, 'pickups': 0, 'captures': 0} for t, name in enumerate(seats)}
    for f in frames:
        for e in f['events']:
            t = e['type']
            if t == 'capture':
                stats_map[e['team']]['captures'] += 1
            elif t == 'pickup':
                stats_map[e['unit'] // 3]['pickups'] += 1
            elif t == 'death':
                stats_map[e['unit'] // 3]['deaths'] += 1
                att = e.get('by', [])
                is_c = (e.get('flag') is not None)
                if len(att) == 1:
                    at = att[0] // 3
                    stats_map[at]['kills'] += 1
                    if is_c: stats_map[at]['carrier_kills'] += 1
                elif len(att) > 1:
                    pt = att[0] // 3
                    stats_map[pt]['kills'] += 1
                    if is_c: stats_map[pt]['carrier_kills'] += 1
                    for a in att[1:]:
                        stats_map[a // 3]['assists'] += 1

    enhanced_stats = []
    for team, st in stats_map.items():
        k = st['kills']
        a = st['assists']
        ck = st['carrier_kills']
        d = st['deaths']
        pick = st['pickups']
        cap = st['captures']
        kda = round((k + a * 0.5) / max(1, d), 2)
        rate = round(cap / max(1, pick) * 100, 1) if pick else 0.0
        enhanced_stats.append({
            'team': team,
            'name': st['name'],
            'score': cap,
            'kills': k,
            'assists': a,
            'carrier_kills': ck,
            'deaths': d,
            'pickups': pick,
            'captures': cap,
            'kda': kda,
            'capture_rate': rate,
        })
    enhanced_stats.sort(key=lambda x: (x['score'], x['kda']), reverse=True)
    
    return {
        "header": game.header(),
        "names": list(seats),
        "result": result,
        "enhanced_stats": enhanced_stats,
        "frames": frames
    }

all_games = {}
for cfg in game_configs:
    print(f"Generating replay for {cfg['tag']} ({cfg['id']})...")
    rep = generate_replay_dict(cfg['id'])
    cfg['replay'] = rep
    cfg['enhanced_stats'] = rep['enhanced_stats']
    all_games[cfg['key']] = cfg
    print(f"  Done: {len(rep['frames'])} frames, {len(rep['names'])} teams")

out_file = Path("all_replays_data.json")
out_file.write_text(json.dumps(all_games, ensure_ascii=False), encoding='utf-8')
print(f"Saved all {len(all_games)} games to {out_file} (Size: {out_file.stat().st_size / 1024 / 1024:.2f} MB)")
