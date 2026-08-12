"""
dashboard.py

Run with:  streamlit run dashboard.py

Shows every tracked story, which source had it first, and the
timeline of updates as other outlets pick it up.
"""

import streamlit as st

from db import get_connection, init_db

st.set_page_config(page_title="Cyber News Dashboard", layout="wide")

init_db()
conn = get_connection()

st.title("Cybersecurity news dashboard")
st.caption(
    "Stories are grouped from multiple sources. The first outlet to "
    "report is flagged; later entries show as updates."
)

stories = conn.execute(
    "SELECT * FROM stories ORDER BY last_updated_at DESC"
).fetchall()

if not stories:
    st.info("No stories yet — run `python fetch_news.py` first to pull some data in.")
else:
    search = st.text_input("Filter by keyword")

    for story in stories:
        if search and search.lower() not in story["title"].lower():
            continue

        entries = conn.execute(
            "SELECT * FROM entries WHERE story_id = ? ORDER BY fetched_at ASC",
            (story["id"],),
        ).fetchall()
        if not entries:
            continue

        first = next((e for e in entries if e["is_first_source"]), entries[0])
        update_count = len(entries) - 1

        with st.expander(f"{story['title']}  ·  {len(entries)} source(s)"):
            st.markdown(
                f"**First reported by:** {first['source_name']}  \n"
                f"[{first['title']}]({first['url']})"
            )
            if update_count > 0:
                st.markdown(f"**{update_count} update(s) since:**")
                for e in entries:
                    if e["id"] == first["id"]:
                        continue
                    st.markdown(f"- {e['source_name']} — [{e['title']}]({e['url']})")

conn.close()
