// Shareable URLs: match.html?m=<key>&t=<turn>. The turn is written back (without adding
// history entries) whenever playback pauses, so a copied link opens on the same moment.

export function readUrlState() {
  const q = new URLSearchParams(location.search);
  const turn = Number(q.get('t'));
  return {
    key: q.get('m') || q.get('match') || null,
    turn: Number.isFinite(turn) && turn > 0 ? turn : 0,
  };
}

export function syncUrl(store) {
  let timer = 0;
  const write = () => {
    const s = store.get();
    const q = new URLSearchParams(location.search);
    q.set('m', s.entry.key);
    const turn = s.replay.frames[s.frame].turn;
    if (turn > 0) q.set('t', String(turn));
    else q.delete('t');
    q.delete('lang');
    history.replaceState(null, '', `${location.pathname}?${q}${location.hash}`);
  };
  store.subscribe(['frame', 'playing'], (s) => {
    if (s.playing) return;
    clearTimeout(timer);
    timer = setTimeout(write, 250);
  });
}

/** Frame index for a turn number (frames are one per turn, but don't rely on it). */
export function frameForTurn(replay, turn) {
  const k = replay.frames.findIndex((f) => f.turn >= turn);
  return k < 0 ? replay.frames.length - 1 : k;
}
