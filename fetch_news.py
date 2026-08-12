"""
fetch_news.py

Run this on a schedule (e.g. every 10-15 minutes via cron) to:
 1. Pull the latest items from every RSS source in sources.py
 2. Decide whether each item is a brand-new story or an update
    to a story we've already seen (using text similarity)
 3. Save everything to news.db

Beginner note: the "clustering" here is intentionally simple — it
compares a new headline to recent headlines using TF-IDF + cosine
similarity, a standard and well-documented technique (search that
term if you want the theory). It's not perfect, but it's easy to
read and tune. See SIMILARITY_THRESHOLD below.
"""

import datetime

import feedparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from db import get_connection, init_db
from sources import RSS_SOURCES

# How similar two headlines need to be (0-1) to count as the same
# story. Start at 0.35 and tune from what you observe — raise it
# if unrelated stories get merged together, lower it if the same
# story keeps showing up as a duplicate instead of an update.
SIMILARITY_THRESHOLD = 0.35

# Only compare a new item against stories first seen within this
# many hours. Keeps the comparison set small and relevant.
LOOKBACK_HOURS = 72


def fetch_all_entries():
    """Pull raw entries from every RSS source. Returns a flat list of dicts."""
    all_entries = []
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
        except Exception as e:
            print(f"  [error] could not fetch {source['name']}: {e}")
            continue

        if not feed.entries:
            print(f"  [warn] {source['name']} returned no entries (feed may have changed)")
            continue

        for item in feed.entries:
            all_entries.append({
                "source_name": source["name"],
                "title": item.get("title", "").strip(),
                "url": item.get("link", "").strip(),
                "published_at": item.get("published", ""),
            })
    return all_entries


def get_recent_stories(conn):
    """Stories first seen within LOOKBACK_HOURS — the candidate pool for matching."""
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(hours=LOOKBACK_HOURS)).isoformat()
    rows = conn.execute(
        "SELECT id, title FROM stories WHERE first_seen_at >= ?", (cutoff,)
    ).fetchall()
    return {row["id"]: row["title"] for row in rows}


def find_matching_story(new_title, recent_stories):
    """
    Compare new_title against recent story titles. Returns the
    matching story_id if similarity clears the threshold, else None
    (meaning: this is a brand-new story).
    """
    if not recent_stories:
        return None

    story_ids = list(recent_stories.keys())
    titles = list(recent_stories.values())

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform(titles + [new_title])
    except ValueError:
        # can happen if titles are empty or only stopwords
        return None

    new_vec = tfidf[-1]
    existing_vecs = tfidf[:-1]
    similarities = cosine_similarity(new_vec, existing_vecs)[0]

    best_idx = similarities.argmax()
    if similarities[best_idx] >= SIMILARITY_THRESHOLD:
        return story_ids[best_idx]
    return None


def save_entry(conn, entry, recent_stories):
    """Insert one entry — as a new story or an update to an existing one."""
    already_have = conn.execute(
        "SELECT id FROM entries WHERE url = ?", (entry["url"],)
    ).fetchone()
    if already_have:
        return False  # nothing new

    now = datetime.datetime.utcnow().isoformat()
    story_id = find_matching_story(entry["title"], recent_stories)

    if story_id is None:
        cur = conn.execute(
            "INSERT INTO stories (title, first_seen_at, last_updated_at) VALUES (?, ?, ?)",
            (entry["title"], now, now),
        )
        story_id = cur.lastrowid
        is_first = 1
        recent_stories[story_id] = entry["title"]  # so later items in this run can match it
    else:
        conn.execute(
            "UPDATE stories SET last_updated_at = ? WHERE id = ?", (now, story_id)
        )
        is_first = 0

    conn.execute(
        """INSERT INTO entries
           (story_id, source_name, title, url, published_at, fetched_at, is_first_source)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (story_id, entry["source_name"], entry["title"], entry["url"],
         entry["published_at"], now, is_first),
    )
    return True


def run():
    init_db()
    conn = get_connection()

    print("Fetching from sources...")
    entries = fetch_all_entries()
    print(f"  pulled {len(entries)} raw entries")

    recent_stories = get_recent_stories(conn)
    saved_count = 0

    for entry in entries:
        if not entry["title"] or not entry["url"]:
            continue
        if save_entry(conn, entry, recent_stories):
            saved_count += 1

    conn.commit()
    conn.close()
    print(f"Done. {saved_count} new entries saved this run.")


if __name__ == "__main__":
    run()
