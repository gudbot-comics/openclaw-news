  # News website

  Lightweight site for `chatgptopenclaw.com` that auto-updates from Google News.

  ## What this repo contains

  - `index.html`, `styles.css`, `app.js`: Minimal frontend.
  - `scripts/fetch_news.py`: Pulls latest Google News RSS for OpenAI and OpenClaw.
  - `data/news.json`: Generated cache consumed by the frontend.
  - `.github/workflows/update-news.yml`: Runs every 10 minutes and commits fresh headlines.
  - `CNAME`: Domain to serve via GitHub Pages.

  ## Local run

 1. Start a local server:
    - `cd /path/to/news-website`
    - `python3 -m http.server`
    - Open `http://localhost:8000`.
 2. For local testing of the updater:
    - `cd /path/to/news-website`
    - `python3 scripts/fetch_news.py`
    - Refresh the page.

  ## GitHub Pages deployment

  1. Push this project to your GitHub repo.
  2. In GitHub > Settings > Pages:
     - Source: Deploy from a branch.
     - Branch: `main`, folder: `/ (root)`.
     - Save. This makes the static site live.
  3. The news updater workflow (`.github/workflows/update-news.yml`) updates `data/news.json` every 10 minutes and pushes it to the same repo, so pages auto-refresh.
  4. Add your custom domain:
     - Keep `CNAME` with `chatgptopenclaw.com`.
     - Keep `https://chatgptopenclaw.com` configured in repository pages settings.

  ## DNS for your domain

  Point your domain DNS as follows (in GoDaddy DNS):
  - `chatgptopenclaw.com` (root) -> `A` records:
    - `185.199.108.153`
    - `185.199.109.153`
    - `185.199.110.153`
    - `185.199.111.153`
  - `www.chatgptopenclaw.com` -> `CNAME` to your pages target host.

  If using GoDaddy DNS, add the four GitHub Pages A records for the root first, then a CNAME for `www`.

  ## Edit behavior

  - No backend required.
  - No DB required.
  - News source is Google News RSS only.
  - `data/news.json` is refreshed on a schedule and committed by GitHub Actions.
