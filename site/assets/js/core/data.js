// Data access. The catalog is small and loaded first; match replays are fetched on demand.
// Paths are relative to the page, so the site works from any sub-path (GitHub Pages).

const CATALOG_URL = 'data/catalog.json';
const cache = new Map();

async function getJson(url) {
  if (!cache.has(url)) {
    const request = fetch(url).then((res) => {
      if (!res.ok) throw new Error(`${res.status} ${res.statusText} (${url})`);
      return res.json();
    });
    // Don't cache failures, so a retry can succeed
    request.catch(() => cache.delete(url));
    cache.set(url, request);
  }
  return cache.get(url);
}

/** @returns {Promise<{version:number, matches: CatalogEntry[]}>} see docs/data-format.md */
export const loadCatalog = () => getJson(CATALOG_URL);

/** @returns {Promise<Replay>} see docs/data-format.md */
export const loadReplay = (entry) => getJson(entry.file);

export async function findEntry(key) {
  const { matches } = await loadCatalog();
  return matches.find((m) => m.key === key) || null;
}

/**
 * AI commentary for a match in one language, or null when there is none.
 * @returns {Promise<Commentary|null>} see docs/data-format.md (Commentary)
 */
export async function loadCommentary(entry, lang) {
  if (!entry.commentary?.includes(lang)) return null;
  return getJson(`data/commentary/${encodeURIComponent(entry.key)}/${encodeURIComponent(lang)}.json`);
}
