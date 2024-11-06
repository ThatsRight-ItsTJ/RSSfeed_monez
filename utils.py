import random
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

# Rate limiting settings
REQUEST_DELAY = 1.0  # Minimum delay between requests to same domain
MAX_RETRIES = 3     # Maximum number of retry attempts
RETRY_DELAY = 5     # Delay between retries in seconds

# Store last request time per domain
last_requests = {}

# Extended list of user agents for better rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.59',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.257'
]

def get_domain(url: str) -> str:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    return urlparse(url).netloc

def should_retry_error(status_code: int) -> bool:
    """Determine if we should retry based on status code."""
    return status_code in [429, 500, 502, 503, 504]

def enforce_rate_limit(domain: str) -> None:
    """Enforce rate limiting for specific domain."""
    current_time = datetime.now()
    if domain in last_requests:
        time_since_last = (current_time - last_requests[domain]).total_seconds()
        if time_since_last < REQUEST_DELAY:
            sleep_time = REQUEST_DELAY - time_since_last
            time.sleep(sleep_time)
    last_requests[domain] = current_time

def get_headers() -> Dict[str, str]:
    """Generate headers with a random user agent and additional fields."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1'
    }

def setup_logging() -> None:
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def make_request(url: str, session) -> Optional[str]:
    """Make HTTP request with retry logic and rate limiting."""
    domain = get_domain(url)
    enforce_rate_limit(domain)

    for attempt in range(MAX_RETRIES):
        try:
            headers = get_headers()
            response = session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 403:
                logging.warning(f"Access forbidden for {url}. Site may be blocking requests.")
                return None
            elif should_retry_error(response.status_code):
                if attempt < MAX_RETRIES - 1:
                    logging.warning(f"Attempt {attempt + 1} failed for {url} with status {response.status_code}. Retrying...")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
            else:
                logging.error(f"Request failed for {url} with status code {response.status_code}")
                return None

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}. Retrying...")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            else:
                logging.error(f"All attempts failed for {url}: {str(e)}")
                return None

    return None

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