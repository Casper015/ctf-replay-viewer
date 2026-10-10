// Viewer state. One store, many small modules that subscribe to the keys they care about.
// This is the contract between modules: if you add state, document it here.
//
//   entry        catalog entry for this match (see docs/data-format.md)
//   replay       full replay { header, names, frames, ... }
//   derived      precomputed stats/moments from derive.js
//   frame        index into replay.frames (integer)
//   playing      boolean
//   speed        playback multiplier, one of SPEEDS in playback.js
//   focusTeam    team index to highlight, or -1 for none
//   selectedUnit unit id shown in the unit card, or null
//   follow       camera follows selectedUnit while zoomed
//   tab          'standings' | 'chart' | 'feed' | 'stats'
//   chartMode    'lines' | 'orbit'
//   immersive    board-only fullscreen layout

export function createStore(initial) {
  let state = { ...initial };
  const subscribers = new Set();

  return {
    get: () => state,
    set(patch) {
      const prev = state;
      state = { ...state, ...patch };
      const changed = Object.keys(patch).filter((k) => prev[k] !== state[k]);
      if (changed.length) subscribers.forEach((fn) => fn(state, changed));
    },
    /**
     * subscribe(fn) or subscribe(['frame', 'focusTeam'], fn).
     * fn(state, changedKeys) runs only when one of the listed keys changed.
     */
    subscribe(keys, fn) {
      if (typeof keys === 'function') [fn, keys] = [keys, null];
      const wrapped = keys ? (s, changed) => changed.some((k) => keys.includes(k)) && fn(s, changed) : fn;
      subscribers.add(wrapped);
      return () => subscribers.delete(wrapped);
    },
  };
}
