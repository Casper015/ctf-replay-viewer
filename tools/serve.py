"""Serve site/ locally with caching disabled, so edits show up on every reload.

  python3 tools/serve.py            # http://localhost:8000
  python3 tools/serve.py 8765       # another port

(`python3 -m http.server -d site` also works, but browsers may keep stale JS modules.)
"""

from __future__ import annotations

import functools
import http.server
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(NoCacheHandler, directory=str(SITE))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"serving {SITE} at http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
