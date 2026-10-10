// Locale-aware number formatting. Always pass through these so zh/en stay consistent.
import { getLang } from './i18n.js';

const cache = new Map();
function nf(options) {
  const key = getLang() + JSON.stringify(options);
  if (!cache.has(key)) cache.set(key, new Intl.NumberFormat(getLang() === 'zh' ? 'zh-CN' : 'en-US', options));
  return cache.get(key);
}

export const fmtInt = (n) => nf({ maximumFractionDigits: 0 }).format(n);
export const fmtDec = (n, digits = 2) => nf({ minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
export const fmtPct = (ratio) => nf({ style: 'percent', maximumFractionDigits: 0 }).format(ratio);
export const fmtKB = (bytes) => nf({ maximumFractionDigits: 0 }).format(Math.round(bytes / 1024));
