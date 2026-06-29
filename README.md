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

## How status works

`server.py` pings each `url` from the server side (avoids browser CORS),
caches the result for ~25s, and the page polls `/api/status` every 30s.
Any HTTP response counts as "up" (green); connection refused / timeout is
"down" (red); grey means not checked yet.

## Files

| file          | purpose                                            |
|---------------|----------------------------------------------------|
| `sites.json`  | the only thing you edit — your list of sites       |
| `index.html`  | the Craigslist-style page (filter box + columns)   |
| `server.py`   | static server + `/api/sites` + `/api/status`       |
