import random
import logging
from typing import Dict, List, Optional
import feedparser
from config import USER_AGENTS
import gzip

def get_headers() -> Dict[str, str]:
    """Generate headers with a random user agent."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def setup_logging() -> None:
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def compare_feed_items(filename: str, new_feed: str) -> List[Dict]:
    """Compare new feed with existing feed to find new items."""
    try:
        # Parse existing feed
        try:
            # Try to read as gzipped first
            try:
                with gzip.open(filename, 'rt', encoding='utf-8') as f:
                    old_feed = feedparser.parse(f.read())
            except:
                # If not gzipped, read as plain text
                with open(filename, 'r', encoding='utf-8') as f:
                    old_feed = feedparser.parse(f.read())
        except FileNotFoundError:
            old_feed = feedparser.FeedParserDict()
            old_feed.entries = []

        # Parse new feed
        new_feed_parsed = feedparser.parse(new_feed)

        # Get existing links
        existing_links = {entry.link for entry in old_feed.entries}

        # Find new items
        new_items = []
        for entry in new_feed_parsed.entries:
            if entry.link not in existing_links:
                new_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'pubDate': entry.get('published', '')
                })

        return new_items
    except Exception as e:
        logging.error(f"Error comparing feeds: {e}")
        return []
