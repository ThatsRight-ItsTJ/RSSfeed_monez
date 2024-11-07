import feedparser
import requests
from lxml import html
from typing import List, Dict, Optional
from datetime import datetime
import pytz
import urllib.parse
import hashlib
import logging
from db_manager import DBManager
from utils import make_request, get_headers

def generate_item_hash(title: str, link: str) -> str:
    """Generate a unique hash for each feed item based on title and link."""
    content = f"{title}{link}".encode('utf-8')
    return hashlib.sha256(content).hexdigest()[:7]

def determine_item_class(result: Dict) -> str:
    """Determine the class of the feed item based on its source."""
    source_url = result.get('source_url', '').lower()
    link = result.get('link', '').lower()
    
    if 'itch.io' in source_url:
        return 'itchio_game'
    elif 'gamerpower.com' in source_url:
        if 'loot' in source_url.lower():
            return 'DLC'
        return 'Videogame'
    elif 'classcentral.com' in source_url:
        return 'Ivy_League_Course'
    elif any(domain in source_url for domain in ['real.discount', 'scrollcoupons.com', 'onlinecourses.ooo', 'udemyfreebies.com', 'infognu.com', 'jucktion.com']):
        return 'Udemy_Course'
    
    return 'unknown'

def clean_image_url(url: str) -> str:
    """Clean and validate image URL."""
    if not url:
        return None
    
    # Remove any "/h" suffix
    if url.endswith('/h'):
        url = url[:-2]
    
    # Ensure Udemy image URLs have the correct format
    if 'udemycdn.com' in url:
        # Extract the course ID and image name from the URL
        parts = url.split('/')
        if len(parts) >= 2:
            course_id = parts[-2]
            image_name = parts[-1]
            return f"https://img-c.udemycdn.com/course/750x422/{course_id}_{image_name}"
    
    return url

async def process_feed_with_db(feed_config: Dict, db_manager: DBManager) -> Optional[List[Dict]]:
    """Process a single feed configuration and store items in database."""
    try:
        feed = feedparser.parse(feed_config['rss_url'])
        results = []
        
        for entry in feed.entries[:feed_config['max_entries']]:
            try:
                source_url = feed_config['link']
                
                # For feeds that need XPath processing
                if 'xpath' in feed_config:
                    with requests.Session() as session:
                        content = make_request(entry.link, session)
                        if not content:
                            continue
                            
                        tree = html.fromstring(content)
                        urls = tree.xpath(feed_config['xpath'])
                        
                        if urls:
                            url = urls[0]
                            
                            # Extract image URL using image_xpath
                            image_url = None
                            if 'image_xpath' in feed_config:
                                image_elements = tree.xpath(feed_config['image_xpath'])
                                if image_elements:
                                    raw_image_url = image_elements[0]
                                    image_url = clean_image_url(raw_image_url)
                            
                            # Create result dictionary
                            result = {
                                'title': entry.title,
                                'link': url,
                                'description': entry.get('description', '')[:500] + '...',
                                'pub_date': datetime.now(pytz.UTC),
                                'source_url': source_url,
                                'item_hash': generate_item_hash(entry.title, url)
                            }
                            
                            if image_url:
                                result['image_url'] = image_url
                else:
                    # Direct RSS feed processing (e.g., for Itch.io)
                    result = {
                        'title': entry.title,
                        'link': entry.link,
                        'description': entry.get('description', '')[:500] + '...',
                        'pub_date': datetime.now(pytz.UTC),
                        'source_url': source_url,
                        'item_hash': generate_item_hash(entry.title, entry.link)
                    }
                    
                    # Extract image from enclosures if available
                    if hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if enclosure.get('type', '').startswith('image/'):
                                result['image_url'] = enclosure.href
                                break
                
                # Determine feed type
                result['feed_type'] = determine_item_class(result)
                
                # Store in database
                await db_manager.add_feed_item(result)
                results.append(result)
                
            except Exception as e:
                logging.error(f"Error processing entry {entry.link}: {str(e)}")
                continue
                    
        return results
    except Exception as e:
        logging.error(f"Error processing feed {feed_config['rss_url']}: {str(e)}")
        return None

def get_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URLs to absolute URLs."""
    if url.startswith(('http://', 'https://')):
        return url
    return urllib.parse.urljoin(base_url, url)