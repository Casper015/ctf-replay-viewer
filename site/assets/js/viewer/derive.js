// Pure precomputation over a replay. No DOM, no state: easy to test and safe to change
// without touching rendering. Everything is indexed by frame number.

import { teamOfUnit } from '../core/teams.js';

/**
 * @returns {{
 *   teams: number,
 *   stats: TeamStats[][],      stats[frame][team], cumulative up to and including that frame
 *   ranking: (frame:number) => TeamStats[],   sorted by score, then KDA
 *   captures: Moment[],        every capture, in order
 *   moments: Moment[],         captures, carrier kills and lead changes (feed + scrubber)
 *   facing: Float32Array[],    facing[frame][unit] in radians, from the last move
 *   maxScore: number,
 *   respawnFrame: (unit:number, frame:number) => number|null,
 * }}
 */
export function deriveMatch(replay) {
  const { header, frames } = replay;
  const teams = header.teams;
  const unitCount = frames[0].units.length;
  const center = (header.size - 1) / 2;

  const running = Array.from({ length: teams }, (_, team) => ({
    team, score: 0, pickups: 0, kills: 0, assists: 0, carrierKills: 0, deaths: 0,
  }));
  const stats = [];
  const captures = [];
  const moments = [];
  const facing = [];

  // Units start facing the middle of the map
  let face = new Float32Array(unitCount);
  frames[0].units.forEach((u, k) => {
    face[k] = u.pos ? Math.atan2(center - u.pos[1], center - u.pos[0]) : 0;
  });

  let leader = null;
  frames.forEach((f, fi) => {
    for (const e of f.events) {
      if (e.type === 'capture') {
        running[e.team].score++;
        const m = { kind: 'capture', frame: fi, turn: f.turn, team: e.team, unit: e.unit, flag: e.flag };
        captures.push(m);
        moments.push(m);
      } else if (e.type === 'pickup') {
        running[teamOfUnit(e.unit)].pickups++;
      } else if (e.type === 'death') {
        running[teamOfUnit(e.unit)].deaths++;
        const by = e.by || [];
        const carrier = e.flag !== null && e.flag !== undefined;
        if (by.length) {
          const killer = teamOfUnit(by[0]);
          running[killer].kills++;
          if (carrier) running[killer].carrierKills++;
          for (const a of by.slice(1)) running[teamOfUnit(a)].assists++;
        }
        if (carrier) {
          moments.push({
            kind: 'carrierKill', frame: fi, turn: f.turn, unit: e.unit,
            team: teamOfUnit(e.unit), by: by.length ? teamOfUnit(by[0]) : null, flag: e.flag,
          });
        }
      }
    }

    // Sole-leader changes become moments too
    const top = Math.max(...f.score);
    const leaders = f.score.reduce((acc, s, t) => (s === top ? [...acc, t] : acc), []);
    if (top > 0 && leaders.length === 1 && leaders[0] !== leader) {
      if (leader !== null) moments.push({ kind: 'lead', frame: fi, turn: f.turn, team: leaders[0], from: leader });
      leader = leaders[0];
    }

    stats.push(running.map((r) => ({
      ...r,
      kda: (r.kills + r.assists * 0.5) / Math.max(1, r.deaths),
      conversion: r.pickups ? r.score / r.pickups : 0,
    })));

    if (fi > 0) {
      face = Float32Array.from(face);
      const prev = frames[fi - 1].units;
      f.units.forEach((u, k) => {
        const p = prev[k].pos;
        if (u.pos && p && (u.pos[0] !== p[0] || u.pos[1] !== p[1])) {
          face[k] = Math.atan2(u.pos[1] - p[1], u.pos[0] - p[0]);
        }
      });
    }
    facing.push(face);
  });

  const rankingCache = new Map();
  const ranking = (fi) => {
    if (!rankingCache.has(fi)) {
      rankingCache.set(fi, [...stats[fi]].sort((a, b) => b.score - a.score || b.kda - a.kda || a.team - b.team));
    }
    return rankingCache.get(fi);
  };

  const respawnFrame = (unit, fi) => {
    for (let k = fi + 1; k < frames.length; k++) if (frames[k].units[unit].pos) return k;
    return null;
  };

  return {
    teams,
    stats,
    ranking,
    captures,
    moments,
    facing,
    maxScore: Math.max(1, ...frames[frames.length - 1].score),
    respawnFrame,
  };
}
