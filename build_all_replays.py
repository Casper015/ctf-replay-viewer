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
    {
        'key': 'g15',
        'id': 'sz15-m055282',
        'tag': '15人全员大决战',
        'badge': '15人 · 49×49 地图 · 45角色',
        'title': '全赛程最高 90 进球纪录！三大模型 14:13:13 压哨绝杀',
        'desc': '45 个单位在中场爆发 90 次夺旗破门。Sonnet 5.5 后程发力，以 14:13:13 的 1 分微弱优势从 Player5 与 Astra 手中压哨夺得头名！'
    },
    {
        'key': 'g8',
        'id': 'sz08-m040053',
        'tag': '8人顶流混战',
        'badge': '8人 · 41×41 地图 · 24角色',
        'title': '四大金刚集体破门！Opus(13) vs Astra(12) vs Sol(11) vs DeepSeek(10)',
        'desc': '8 大主力密集对抗，总得分高达 70 分！前四名全部拿下两位数进球，攻防节奏窒息拉满。'
    },
    {
        'key': 'g4',
        'id': 'sz04-m015252',
        'tag': '4人天王山对决',
        'badge': '4人 · 31×31 地图 · 12角色',
        'title': 'Astra(18) 狂暴火力全开 vs Sol(14) vs P5(13) vs Opus(8)',
        'desc': '四大核心阵营直接相撞，Astra 打出恐怖的 18 进球巅峰表现，Sol 与 Player5 在后方全力围剿，战况极度激烈。'
    },
    {
        'key': 'g3',
        'id': 'sz03-m012514',
        'tag': '3人惊天大翻盘',
        'badge': '3人 · 31×31 地图 · 9角色',
        'title': '半程落后 7 分！Fable 5.1(17) 绝地反超 Sol(16) & P1(14)',
        'desc': '半程 Sol 狂取 12 分建立 7 分巨大领跑优势，Fable 5.1 在后半程连抢 12 分，在终场第 390 回合反超 1 分完成史诗逆转。'
    },
    {
        'key': 'g2',
        'id': 'sz02-m006122',
        'tag': '2人单挑绝杀',
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
    
    # 丰富 stats，加入 KDA 等计算
    enhanced_stats = []
    for team, name in enumerate(seats):
        st = game.stats[team]
        k = round(st['kills'], 1)
        ck = round(st['carrier_kills'], 1)
        d = st['deaths']
        pick = st['pickups']
        cap = st['captures']
        kda = round((k + ck * 0.5) / max(1, d), 2)
        rate = round((cap / max(1, pick)) * 100, 1)
        enhanced_stats.append({
            'team': team,
            'name': name,
            'score': game.score[team],
            'kills': k,
            'carrier_kills': ck,
            'deaths': d,
            'pickups': pick,
            'captures': cap,
            'kda': kda,
            'capture_rate': rate,
        })
    enhanced_stats.sort(key=lambda x: x['score'], reverse=True)
    
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
    all_games[cfg['key']] = cfg
    print(f"  Done: {len(rep['frames'])} frames, {len(rep['names'])} teams")

out_file = Path(r"C:\Users\caspe\OneDrive\Code\AI_Test\all_replays_data.json")
out_file.write_text(json.dumps(all_games, ensure_ascii=False), encoding='utf-8')
print(f"Saved all 5 games to {out_file} (Size: {out_file.stat().st_size / 1024 / 1024:.2f} MB)")
