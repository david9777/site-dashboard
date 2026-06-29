# Dashboard

A Craigslist-style portal that lists every site you've built, with a live
green/red status dot for each. Completely standalone — it only *links* to your
other apps, it never touches or bundles them.

## Run

```bash
cd C:/Users/DSamson/.claude/Dashboard
python server.py            # http://localhost:8000
python server.py --port 9000
```

Pure Python standard library — nothing to install.

## Add / edit sites

Everything lives in **`sites.json`**. Edit it and refresh the page — no restart
needed. Shape:

```json
{
  "title": "my sites",
  "tagline": "everything I've built, in one place",
  "categories": [
    {
      "name": "legal tools",
      "sites": [
        { "name": "SettlementSearch", "url": "http://localhost:8765", "blurb": "short description" }
      ]
    }
  ]
}
```

- **categories** become the columns (red headers, Craigslist-style).
- **url** is what the link opens *and* what the status dot pings.
- **blurb** is optional one-line description.

Use public deployed URLs (e.g. `https://settlesearch.onrender.com`) or local
ports — mix freely.

## Hosting

The dashboard is **pure static** — `index.html` + `sites.json` are all you need
to serve. Host it anywhere with no backend:

- **GitHub Pages** — push this repo, enable Pages → always-on, free, stable URL.
- **Netlify Drop** (app.netlify.com/drop) — drag the folder, instant HTTPS link.
- **Cloudflare Pages**, S3, etc.

Static hosts are always-on (no cold starts), which makes them ideal for an
emailed link or a wall/kiosk display. `server.py` is still handy for running
locally (`python server.py`).

## How status works

Two modes, automatic:

- **With `server.py`** (local): the server pings each `url` server-side,
  caches ~25s, and the page polls `/api/status`.
- **Static host** (no backend): the browser pings each `url` directly. Any
  response = up (green), network failure/timeout = down (red), grey = not
  checked yet.

Browser-side checks only work for **public URLs** — `localhost` entries will
read as down for anyone off your machine, so use public URLs for a published
dashboard.

## Files

| file          | purpose                                            |
|---------------|----------------------------------------------------|
| `sites.json`  | the only thing you edit — your list of sites       |
| `index.html`  | the Craigslist-style page (filter box + columns)   |
| `server.py`   | static server + `/api/sites` + `/api/status`       |
