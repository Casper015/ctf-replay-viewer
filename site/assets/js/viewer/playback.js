// Playback clock. Owns timing only: which frame is current and how far the board's
// tween into that frame has progressed. Rendering reads progress(now) every animation frame.

export const SPEEDS = [0.25, 0.5, 1, 2, 3, 4];
const TURN_MS = 200;        // one turn at 1×
const STEP_TWEEN_MS = 160;  // tween length for single manual steps

export function createPlayback(store) {
  let enteredAt = 0;
  let tweenMs = 0;

  const count = () => store.get().replay.frames.length;
  const clamp = (k) => Math.max(0, Math.min(count() - 1, k));

  function enter(frame, ms) {
    enteredAt = performance.now();
    tweenMs = ms;
    store.set({ frame });
  }

  function seek(frame, { animate = false } = {}) {
    const target = clamp(Math.round(frame));
    const cur = store.get().frame;
    enter(target, animate && Math.abs(target - cur) === 1 ? STEP_TWEEN_MS : 0);
  }

  function play() {
    if (store.get().frame >= count() - 1) seek(0);
    enteredAt = performance.now();
    tweenMs = 0;
    store.set({ playing: true });
  }

  function pause() {
    store.set({ playing: false });
  }

  return {
    seek,
    play,
    pause,
    toggle: () => (store.get().playing ? pause() : play()),
    step(delta) {
      pause();
      seek(store.get().frame + delta, { animate: true });
    },
    setSpeed(speed) {
      store.set({ speed });
    },
    /** 0..1: how far units have travelled from the previous frame into the current one. */
    progress(now) {
      return tweenMs > 0 ? Math.min(1, Math.max(0, (now - enteredAt) / tweenMs)) : 1;
    },
    /** Call once per animation frame. */
    tick(now) {
      const s = store.get();
      if (!s.playing) return;
      const interval = TURN_MS / s.speed;
      if (now - enteredAt < interval) return;
      if (s.frame >= count() - 1) {
        pause();
        return;
      }
      // Keep cadence steady, but don't try to catch up after a long stall (background tab)
      const behind = now - enteredAt - interval;
      enteredAt = behind < interval ? now - behind : now;
      tweenMs = interval;
      store.set({ frame: s.frame + 1 });
    },
  };
}
