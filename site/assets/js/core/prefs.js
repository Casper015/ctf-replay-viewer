// Per-viewer preferences in localStorage. Storage can be unavailable (private mode,
// blocked site data), so every access is wrapped and falls back to defaults.

const PREFIX = 'ctf-replays:';

export function getPref(key, fallback = null) {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function setPref(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch {
    /* storage unavailable: preference just won't persist */
  }
}
