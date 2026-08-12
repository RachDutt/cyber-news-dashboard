# Cyber news dashboard — MVP

A small pipeline that pulls cybersecurity news from multiple RSS
sources, groups articles about the same story together, flags
which source reported it *first*, and shows the rest as updates.

## What's in this folder

- `sources.py` — the list of RSS feeds to track. Edit this to add/remove sources.
- `db.py` — sets up the local database (SQLite — a single file, no server needed).
- `fetch_news.py` — the ingestion script. Run this to pull new articles in.
- `dashboard.py` — the web dashboard. Run this to browse what's been collected.
- `requirements.txt` — the Python packages this project needs.

## One-time setup

1. **Install Python 3.10+** if you don't have it: https://www.python.org/downloads/
   Check with: `python3 --version`

2. **Open a terminal in this folder** and create a virtual environment
   (this keeps this project's packages separate from everything else on your machine):
   ```
   python3 -m venv venv
   source venv/bin/activate        # on Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Running it

1. **Pull in news** (do this first, and re-run it periodically):
   ```
   python fetch_news.py
   ```
   You'll see output like `pulled 42 raw entries` / `Done. 38 new entries saved this run.`
   This creates a `news.db` file in this folder — that's your entire database.

2. **Open the dashboard:**
   ```
   streamlit run dashboard.py
   ```
   This opens a browser tab at `http://localhost:8501` showing every story,
   grouped, with the first source flagged and updates listed underneath.

3. **Keep it updating automatically** — the simplest way while you're learning
   is to just re-run `python fetch_news.py` every so often. Once you're
   comfortable, look into `cron` (Mac/Linux) or Task Scheduler (Windows) to
   run it automatically every 10-15 minutes.

## If a source stops returning results

RSS URLs occasionally change. `fetch_news.py` will print a `[warn]` for any
source that returns nothing — search `"<site name> rss feed url"` to find
the current one and update `sources.py`.

## Tuning the clustering

Open `fetch_news.py` and look at `SIMILARITY_THRESHOLD` near the top
(starts at `0.35`). This controls how similar two headlines need to be
to count as "the same story":
- If you see **unrelated stories getting merged together** → raise it (e.g. `0.45`)
- If you see **the same story appearing as duplicates** instead of updates → lower it (e.g. `0.25`)

There's no perfect number — run it for a few days, watch the dashboard,
and adjust based on what you actually see.

## What's next (not built yet)

This is the Phase 1 MVP: prove the ingestion + clustering works and is
useful to look at. Natural next steps once this feels solid:
- Add severity/category tagging using an LLM API call per new story
- Move from SQLite to Postgres if you need multiple people accessing it at once
- Add more sources (see the earlier conversation for source ideas)
- Build the video-script-generation step on top of this data
