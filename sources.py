"""
Cybersecurity RSS sources for the news dashboard.

Add or remove entries here — this is the only file most people
will ever need to touch to change what gets tracked.

NOTE: RSS URLs occasionally change or get renamed. If a source
stops returning results, search "<site name> rss feed url" to
find the current one and update it here.
"""

RSS_SOURCES = [
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
    {"name": "Bleeping Computer", "url": "https://www.bleepingcomputer.com/feed/"},
    {"name": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/"},
    {"name": "Dark Reading", "url": "https://www.darkreading.com/rss.xml"},
    {"name": "CISA", "url": "https://www.cisa.gov/rss.xml"},
    {"name": "Talos Intelligence", "url": "https://blog.talosintelligence.com/rss/"},
]
