// Keyboard shortcuts for the viewer. The list here is also shown in the shortcuts dialog
// (match.html), so keep both in sync.

import { SPEEDS } from './playback.js';
import { TABS } from './ui/tabs.js';

export function mountKeyboard(store, { playback, board, toggleImmersive }) {
  window.addEventListener('keydown', (e) => {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
    const tag = e.target.tagName;
    if (tag === 'INPUT' && e.target.type !== 'range') return;
    // The scrubber handles its own arrow/Home/End keys natively
    if (tag === 'INPUT' && /^(Arrow|Home|End|Page)/.test(e.key)) return;
    if (tag === 'SELECT' || tag === 'TEXTAREA' || e.target.isContentEditable) return;
    if (document.querySelector('dialog[open]')) return;

    const s = store.get();
    const jump = e.shiftKey ? 10 : 1;
    let handled = true;
    switch (e.key) {
      case ' ':
      case 'k':
        if (tag === 'BUTTON' && e.key === ' ') { handled = false; break; }
        playback.toggle();
        break;
      case 'ArrowRight': playback.step(jump); break;
      case 'ArrowLeft': playback.step(-jump); break;
      case 'Home': playback.seek(0); break;
      case 'End': playback.seek(s.replay.frames.length - 1); break;
      case '.': case '>': seekMoment(1); break;
      case ',': case '<': seekMoment(-1); break;
      case '+': case '=': board.zoomBy(1.5); break;
      case '-': case '_': board.zoomBy(1 / 1.5); break;
      case '0': board.resetView(); break;
      case 'f': case 'F': toggleImmersive(); break;
      case '[': setSpeed(-1); break;
      case ']': setSpeed(1); break;
      case '1': case '2': case '3': case '4': store.set({ tab: TABS[Number(e.key) - 1] }); break;
      case 'Escape':
        if (s.selectedUnit !== null) store.set({ selectedUnit: null, follow: false });
        else if (s.focusTeam >= 0) store.set({ focusTeam: -1 });
        else if (s.immersive) toggleImmersive();
        else handled = false;
        break;
      case '?': document.getElementById('dlg-shortcuts').showModal(); break;
      default: handled = false;
    }
    if (handled) e.preventDefault();
  });

  function seekMoment(dir) {
    const s = store.get();
    const caps = s.derived.captures;
    const target = dir > 0
      ? caps.find((c) => c.frame > s.frame)
      : [...caps].reverse().find((c) => c.frame < s.frame);
    if (target) playback.seek(target.frame);
  }

  function setSpeed(dir) {
    const k = SPEEDS.indexOf(store.get().speed);
    const next = SPEEDS[Math.max(0, Math.min(SPEEDS.length - 1, k + dir))];
    playback.setSpeed(next);
  }
}
