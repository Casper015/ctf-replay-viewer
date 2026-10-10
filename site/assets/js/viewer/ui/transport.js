// Transport bar: play/pause, single steps, scrubber with capture marks, turn readout, speed.

import { $, h } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';
import { fmtInt } from '../../core/format.js';
import { teamColor, teamName } from '../../core/teams.js';
import { SPEEDS } from '../playback.js';

export function mountTransport(store, { playback }) {
  const playBtn = $('#btn-play');
  const backBtn = $('#btn-step-back');
  const fwdBtn = $('#btn-step-fwd');
  const range = $('#scrub');
  const scrubber = $('#scrubber');
  const marks = $('#scrub-marks');
  const time = $('#time');
  const speed = $('#speed');

  const { replay, derived } = store.get();
  const last = replay.frames.length - 1;
  const totalTurns = replay.frames[last].turn;
  range.max = String(last);

  // Capture marks: one tick per capture in the scoring team's color
  const renderMarks = () => marks.replaceChildren(...derived.captures.map((c) => h('i', {
    style: { left: `${(c.frame / last) * 100}%`, '--c': teamColor(c.team) },
    title: t('viewer.captureMark', { team: teamName(replay.names[c.team]), turn: c.turn }),
  })));
  renderMarks();

  speed.replaceChildren(...SPEEDS.map((v) => h('option', { value: String(v) }, `${v}×`)));
  speed.value = String(store.get().speed);

  playBtn.addEventListener('click', () => playback.toggle());
  backBtn.addEventListener('click', () => playback.step(-1));
  fwdBtn.addEventListener('click', () => playback.step(1));
  range.addEventListener('input', () => playback.seek(Number(range.value)));
  speed.addEventListener('change', () => playback.setSpeed(Number(speed.value)));

  function renderPlay(s) {
    playBtn.innerHTML = icon(s.playing ? 'pause' : 'play', 'icon icon--lg');
    const label = t(s.playing ? 'viewer.pause' : 'viewer.play');
    playBtn.setAttribute('aria-label', label);
    playBtn.title = `${label} (Space)`;
  }

  function renderFrame(s) {
    const f = replay.frames[s.frame];
    range.value = String(s.frame);
    scrubber.style.setProperty('--pct', `${(s.frame / last) * 100}%`);
    range.setAttribute('aria-valuetext', t('viewer.turnOf', { turn: f.turn, total: totalTurns }));
    time.innerHTML = `<span class="num">${fmtInt(f.turn)}</span><span class="transport__total">/ ${fmtInt(totalTurns)}</span>`;
    backBtn.disabled = s.frame === 0;
    fwdBtn.disabled = s.frame === last;
  }

  function renderLabels() {
    range.setAttribute('aria-label', t('viewer.scrubLabel'));
    speed.setAttribute('aria-label', t('viewer.speed'));
    speed.title = t('viewer.speed');
    backBtn.setAttribute('aria-label', t('viewer.stepBack'));
    backBtn.title = `${t('viewer.stepBack')} (←)`;
    fwdBtn.setAttribute('aria-label', t('viewer.stepForward'));
    fwdBtn.title = `${t('viewer.stepForward')} (→)`;
  }

  store.subscribe(['playing'], renderPlay);
  store.subscribe(['frame'], renderFrame);
  store.subscribe(['speed'], (s) => { speed.value = String(s.speed); });
  onLangChange(() => {
    renderMarks();
    renderLabels();
    renderPlay(store.get());
    renderFrame(store.get());
  });

  backBtn.innerHTML = icon('stepBack');
  fwdBtn.innerHTML = icon('stepForward');
  renderLabels();
  renderPlay(store.get());
  renderFrame(store.get());
}
