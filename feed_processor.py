import feedparser
import requests
from lxml import html
from typing import List, Dict, Optional
from datetime import datetime
import pytz
from rfeed import Item, Feed, Enclosure
import logging
from utils import get_headers
from email.utils import parsedate_to_datetime
import urllib.parse
import hashlib
import uuid
from db_manager import DBManager

def generate_item_hash(title: str, link: str) -> str:
    """Generate a unique hash for each feed item based on title and link."""
    content = f"{title}{link}".encode('utf-8')
    return hashlib.sha256(content).hexdigest()[:7]

def determine_item_class(result: Dict) -> str:
    """Determine the class of the feed item based on its source."""
    source_url = result.get('source_url', '').lower()
    
    if 'itch.io' in source_url:
        return 'itchio_game'
    elif 'gamerpower.com' in source_url and '/dlc/' in result.get('link', '').lower():
        return 'DLC'
    elif 'gamerpower.com' in source_url:
        return 'Videogame'
    elif 'classcentral.com' in source_url:
        return 'Ivy_League_Course'
    elif any(domain in source_url for domain in ['real.discount', 'scrollcoupons.com', 'onlinecourses.ooo', 'udemyfreebies.com', 'infognu.com', 'jucktion.com']):
        return 'Udemy_Course'
    
    return 'unknown'

async def process_feed_with_db(feed_config: Dict, db_manager: DBManager) -> Optional[List[Dict]]:
    """Process a single feed configuration and store items in database."""
    try:
        feed = feedparser.parse(feed_config['rss_url'])
        results = []
        
        for entry in feed.entries[:feed_config['max_entries']]:
            try:
                # Add source URL to track origin
                source_url = feed_config['link']
                
                if 'xpath' in feed_config:
                    response = requests.get(entry.link, headers=get_headers(), timeout=10)
                    if response.status_code == 200:
                        tree = html.fromstring(response.content)
                        urls = tree.xpath(feed_config['xpath'])
                        
                        if urls:
                            url = urls[0]
                            
                            # Extract image URL using image_xpath
                            image_url = None
                            if 'image_xpath' in feed_config:
                                image_elements = tree.xpath(feed_config['image_xpath'])
                                if image_elements:
                                    image_url = get_absolute_url(image_elements[0], entry.link)
                            
                            # Convert the published date to a datetime object
                            if 'published' in entry:
                                pub_date = parsedate_to_datetime(entry.published)
                            else:
                                pub_date = datetime.now(pytz.UTC)
                            
                            # Generate hash for the item
                            item_hash = generate_item_hash(entry.title, url)
                            
                            # Determine item class
                            feed_type = determine_item_class({'source_url': source_url, 'link': url})
                            
                            result = {
                                'title': entry.title,
                                'link': url,
                                'description': entry.get('description', ''),
                                'pub_date': pub_date,
                                'source_url': source_url,
                                'item_hash': item_hash,
                                'feed_type': feed_type
                            }
                            
                            if image_url:
                                result['image_url'] = image_url
                            
                            # Store in database
                            await db_manager.add_feed_item(result)
                            results.append(result)
                            
            except Exception as e:
                logging.error(f"Error processing entry {entry.link}: {str(e)}")
                
        return results
    except Exception as e:
        logging.error(f"Error processing feed {feed_config['rss_url']}: {str(e)}")
        return None

def get_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URLs to absolute URLs."""
    if url.startswith(('http://', 'https://')):
        return url
    return urllib.parse.urljoin(base_url, url)

def parse_existing_xml(filename: str) -> List[Item]:
    """Parse existing XML feed and return items."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            feed = feedparser.parse(f.read())
            items = []
            for entry in feed.entries:
                item_kwargs = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'pubDate': parsedate_to_datetime(entry.published)
                }
                
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    enclosure = entry.enclosures[0]
                    if 'url' in enclosure:
                        item_kwargs['enclosure'] = Enclosure(
                            url=enclosure.url,
                            length=enclosure.get('length', '0'),
                            type=enclosure.get('type', 'image/jpeg')
                        )
                
                items.append(Item(**item_kwargs))
            return items
    except FileNotFoundError:
        return []
    except Exception as e:
        logging.error(f"Error parsing existing XML: {str(e)}")
        return []