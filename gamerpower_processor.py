import feedparser
import requests
from lxml import html
import logging
import time
from typing import List, Dict, Any
import urllib.parse
from datetime import datetime
import pytz
from rfeed import Item, Feed, Enclosure
from utils import get_headers
from email.utils import parsedate_to_datetime
from feed_processor import parse_existing_xml
from config import (
    GAMERPOWER_GAMES_CONFIG,
    GAMERPOWER_LOOT_CONFIG,
    MAX_RETRIES,
    RETRY_DELAY
)

def fetch_url_with_retry(url: str) -> requests.Response:
    """Fetch URL with retry mechanism."""
    for attempt in range(MAX_RETRIES):
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise
    return requests.Response()

def get_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URLs to absolute URLs."""
    if url.startswith(('http://', 'https://')):
        return url
    return urllib.parse.urljoin(base_url, url)

def process_single_gamerpower_feed(config: Dict) -> List[Dict[str, Any]]:
    """Process a single GamerPower RSS feed and extract items."""
    results = []
    logging.info(f"Parsing GamerPower RSS feed: {config['rss_url']}")
    feed = feedparser.parse(config['rss_url'])

    if not feed.entries:
        logging.warning(f"No entries found in the GamerPower RSS feed: {config['rss_url']}")
        return results

    for entry in feed.entries[:config['max_entries']]:
        url = entry.get('link')
        if not url:
            logging.warning(f"Entry does not have a link: {entry.get('title', 'Untitled')}")
            continue

        logging.info(f"Processing entry: {url}")

        try:
            response = fetch_url_with_retry(url)
            tree = html.fromstring(response.content)
            elements = tree.xpath(config['xpath'])

            if elements:
                content = elements[0]
                full_url = urllib.parse.urljoin(config['base_url'], content)
                
                # Extract image URL using image_xpath
                image_url = None
                if 'image_xpath' in config:
                    image_elements = tree.xpath(config['image_xpath'])
                    if image_elements:
                        image_url = get_absolute_url(image_elements[0], config['base_url'])
                
                if 'published' in entry:
                    pub_date = parsedate_to_datetime(entry.published)
                else:
                    pub_date = datetime.now(pytz.UTC)
                    
                result = {
                    'title': entry.get('title', 'Untitled'),
                    'description': entry.get('description', '')[:500] + '...',
                    'link': full_url,
                    'pubDate': pub_date
                }
                
                # Add image URL if found
                if image_url:
                    result['image_url'] = image_url
                
                results.append(result)
                logging.info(f"Found matching content using XPath for {url}")
            else:
                logging.warning(f"No content found using XPath for {url}")

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")

    return results

def create_gamerpower_feed(results: List[Dict[str, Any]], config: Dict, filename: str) -> str:
    """Create RSS feed from GamerPower results, merging with existing items."""
    # Get existing items from the file
    existing_items = parse_existing_xml(filename)
    
    # Create new items from results
    new_items = []
    for result in results:
        item_kwargs = {
            'title': result['title'],
            'link': result['link'],
            'description': result['description'],
            'pubDate': result['pubDate']
        }
        
        # Add image enclosure if available
        if 'image_url' in result:
            item_kwargs['enclosure'] = Enclosure(
                url=result['image_url'],
                length='0',  # Length is required but not critical for images
                type='image/jpeg'  # Default to JPEG, could be made more specific if needed
            )
        
        new_items.append(Item(**item_kwargs))
    
    # Combine new and existing items, removing duplicates
    all_items = new_items + existing_items
    unique_items = {item.link: item for item in all_items}.values()

    feed = Feed(
        title=config['title'],
        link=config['link'],
        description=config['description'],
        language="en-US",
        lastBuildDate=datetime.now(pytz.UTC),
        items=list(unique_items)
    )

    return feed.rss()
