import re
import feedparser
from typing import List, Dict
from rfeed import Item, Feed, Enclosure
from datetime import datetime
import pytz
import logging
from feed_processor import parse_existing_xml
import hashlib
import uuid
from email.utils import parsedate_to_datetime

def generate_item_hash() -> str:
    """Generate a unique hash for each feed item."""
    unique_id = str(uuid.uuid4())
    return hashlib.sha256(unique_id.encode('utf-8')).hexdigest()[:7]

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

def create_redirect_feed(original_feed: str, feed_title: str) -> str:
    """Create a redirect feed from an original feed."""
    try:
        feed = feedparser.parse(original_feed)
        redirect_items = []

        for entry in feed.entries:
            item_class = None
            item_hash = None
            original_desc = entry.description

            # Extract class and hash from description
            class_match = re.search(r'<class>(.*?)</class>', original_desc)
            hash_match = re.search(r'<hash>(.*?)</hash>', original_desc)
            
            if class_match and hash_match:
                item_class = class_match.group(1)
                item_hash = hash_match.group(1)
            else:
                # Generate new class and hash if not found
                item_class = determine_item_class({'source_url': entry.link})
                item_hash = generate_item_hash()

            # Create redirect URL
            redirect_url = f"https://www.goodoffers.theworkpc.com/?class={item_class}&hash={item_hash}"

            # Create redirect item
            item_kwargs = {
                'title': entry.title,
                'link': redirect_url,
                'description': f"Original content at: {entry.link}",
                'pubDate': parsedate_to_datetime(entry.published) if hasattr(entry, 'published') else datetime.now(pytz.UTC)
            }

            # Add image enclosure if present
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        item_kwargs['enclosure'] = Enclosure(
                            url=enclosure.href,
                            length='0',
                            type='image/jpeg'
                        )
                        break

            redirect_items.append(Item(**item_kwargs))

        # Create redirect feed
        redirect_feed = Feed(
            title=f"{feed_title} (Redirect)",
            link="https://www.goodoffers.theworkpc.com",
            description=f"Redirect feed for {feed_title}",
            language="en-US",
            lastBuildDate=datetime.now(pytz.UTC),
            items=redirect_items
        )

        return redirect_feed.rss()
    except Exception as e:
        logging.error(f"Error creating redirect feed: {str(e)}")
        return ""

def create_merged_rss_feed(results: List[Dict], title: str, description: str, link: str, existing_items: List[Item]) -> str:
    """Create a merged RSS feed from results and existing items."""
    try:
        items = []
        for result in results:
            item_hash = generate_item_hash()
            item_class = determine_item_class(result)
            enhanced_description = f'<class>{item_class}</class>\n<hash>{item_hash}</hash>\n{result["description"]}'
            
            item_kwargs = {
                'title': result['title'],
                'link': result['link'],
                'description': enhanced_description,
                'pubDate': result['pubDate']
            }
            
            if 'image_url' in result:
                item_kwargs['enclosure'] = Enclosure(
                    url=result['image_url'],
                    length='0',
                    type='image/jpeg'
                )
            
            items.append(Item(**item_kwargs))
        
        all_items = []
        for item in items + existing_items:
            if not hasattr(item, 'description'):
                continue
                
            desc = item.description
            needs_update = False
            
            if '<class>' not in desc:
                item_class = determine_item_class({'source_url': item.link})
                desc = f'<class>{item_class}</class>\n{desc}'
                needs_update = True
                
            if '<hash>' not in desc:
                item_hash = generate_item_hash()
                desc = f'<hash>{item_hash}</hash>\n{desc}'
                needs_update = True
                
            if needs_update:
                item.description = desc
                
            all_items.append(item)
        
        unique_items = {item.link: item for item in all_items}.values()
        
        feed = Feed(
            title=title,
            link=link,
            description=description,
            language="en-US",
            lastBuildDate=datetime.now(pytz.UTC),
            items=list(unique_items)
        )
        
        return feed.rss()
    except Exception as e:
        logging.error(f"Error creating merged feed: {str(e)}")
        return ""

def merge_all_feeds(scraped_filename: str, final_merge_filename: str) -> str:
    """Merge multiple RSS feeds into a single feed."""
    try:
        with open(scraped_filename, 'r', encoding='utf-8') as f:
            scraped_content = f.read()
            
        feed = Feed(
            title="Final Merged Feed",
            link="https://example.com/final-feed",
            description="Combined feed from multiple sources",
            language="en-US",
            lastBuildDate=datetime.now(pytz.UTC),
            items=parse_existing_xml(scraped_filename)
        )
        
        merged_content = feed.rss()
        with open(final_merge_filename, 'w', encoding='utf-8') as f:
            f.write(merged_content)
            
        return merged_content
    except Exception as e:
        logging.error(f"Error merging feeds: {str(e)}")
        return ""
