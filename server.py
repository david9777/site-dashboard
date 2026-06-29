#!/usr/bin/env python3
"""
Dashboard — a Craigslist-style portal for all your sites.

Serves the static page AND a tiny JSON API:

    GET /api/sites    -> the raw sites.json
    GET /api/status   -> { "<url>": true|false, ... }  (server-side health pings)

Sites are defined in sites.json — edit that file to add/remove/reorder.
The status endpoint pings each site from the server (avoids browser CORS)
and caches results so the page can poll cheaply.

Run it:
    python server.py                 # serve on http://localhost:8000
    python server.py --port 9000     # custom port

Pure standard library — no pip install needed.
"""
import json, os, sys, socket, threading, time
import urllib.request, urllib.error
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
SITES = os.path.join(ROOT, "sites.json")
UA = "Dashboard/1.0 (site portal health check)"

# Health-check cache: url -> (ok: bool, checked_at: float)
_STATUS = {}
_STATUS_LOCK = threading.Lock()
CHECK_TTL = 25          # seconds a result stays fresh
CHECK_TIMEOUT = 4       # seconds per probe


def load_sites():
    with open(SITES, "r", encoding="utf-8") as f:
        return json.load(f)


def all_urls(config):
    urls = []
    for cat in config.get("categories", []):
        for site in cat.get("sites", []):
            u = site.get("url")
            if u:
                urls.append(u)
    return urls


def probe(url):
    """Return True if the URL answers, False otherwise. Cheap and forgiving:
    any HTTP response (even 401/403/500) counts as 'up' — the box is alive."""
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=CHECK_TIMEOUT) as r:
            return 100 <= r.status < 600
    except urllib.error.HTTPError:
        return True                      # server responded, just not 2xx
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
        return False
    except Exception:
        return False


def get_status():
    """Return {url: ok} for every configured site, refreshing stale entries
    concurrently so a page load never blocks on slow probes."""
    try:
        urls = all_urls(load_sites())
    except Exception:
        return {}

    now = time.time()
    stale = []
    with _STATUS_LOCK:
        for u in urls:
            cached = _STATUS.get(u)
            if not cached or (now - cached[1]) > CHECK_TTL:
                stale.append(u)

    if stale:
        results = {}
        threads = []

        def worker(u):
            results[u] = probe(u)

        for u in stale:
            t = threading.Thread(target=worker, args=(u,), daemon=True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join(timeout=CHECK_TIMEOUT + 1)

        with _STATUS_LOCK:
            for u, ok in results.items():
                _STATUS[u] = (ok, time.time())

    with _STATUS_LOCK:
        return {u: _STATUS[u][0] for u in urls if u in _STATUS}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/status":
            return self._json(get_status())
        if self.path.split("?")[0] == "/api/sites":
            try:
                return self._json(load_sites())
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        return super().do_GET()

    def log_message(self, fmt, *args):
        pass  # quiet


def main():
    # Hosting platforms (Render, Replit, Heroku) inject the port via $PORT.
    port = int(os.environ.get("PORT", "8000"))
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    url = f"http://localhost:{port}"
    print(f"Dashboard serving {url}")
    print(f"Editing sites: {SITES}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
