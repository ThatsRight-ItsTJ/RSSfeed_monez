import os
import logging
import asyncio
from config import (
    GAMERPOWER_GAMES_CONFIG,
    GAMERPOWER_LOOT_CONFIG,
    ITCHIO_GAMES_CONFIG,
    IVY_LEAGUE_CONFIG,
    FEEDS
)
from feed_processor import process_feed_with_db
from feed_generator import create_merged_rss_feed, create_redirect_feed
from utils import setup_logging, compare_feed_items
from gamerpower_processor import process_single_gamerpower_feed, create_gamerpower_feed
from webhook_manager import WebhookManager
from db_manager import DBManager

async def generate_feed_and_redirect(config, results, webhook_manager, db_manager, feed_type="merged"):
    """Generate both original and redirect feeds."""
    if results:
        try:
            # Ensure feeds directory exists
            os.makedirs('public/feeds', exist_ok=True)
            
            if feed_type == "gamerpower":
                feed = create_gamerpower_feed(results, config, config['filename'])
            else:
                feed = create_merged_rss_feed(
                    results,
                    config['title'],
                    config['description'],
                    config['link'],
                    []
                )
            
            if not feed:
                logging.error(f"Failed to generate feed for {config['filename']}")
                return
                
            # Add XML declaration if missing
            if not feed.startswith('<?xml'):
                feed = '<?xml version="1.0" encoding="UTF-8"?>\n' + feed
                
            feed_path = os.path.join('public/feeds', config['filename'])
            
            # Compare with previous feed to find new items
            new_items = compare_feed_items(feed_path, feed)
                
            # Save original feed
            with open(feed_path, 'w', encoding='utf-8') as f:
                f.write(feed)
            logging.info(f"Generated {feed_path}")
            
            # Create and save redirect feed
            redirect_feed = create_redirect_feed(feed, config['title'])
            if redirect_feed:
                redirect_filename = f"redirect_{config['filename']}"
                redirect_path = os.path.join('public/feeds', redirect_filename)
                with open(redirect_path, 'w', encoding='utf-8') as f:
                    f.write(redirect_feed)
                logging.info(f"Generated {redirect_path}")

            # Store new items in database and notify webhooks
            if new_items:
                for item in new_items:
                    await db_manager.add_feed_item(item)
                feed_key = os.path.splitext(config['filename'])[0]
                await webhook_manager.notify_feed_update(feed_key, new_items)
                
        except Exception as e:
            logging.error(f"Error generating feed {config['filename']}: {str(e)}")

async def main():
    setup_logging()
    logging.info("Starting feed generation")

    webhook_manager = WebhookManager()
    db_manager = DBManager()

    try:
        # Process GamerPower feeds
        for config in [GAMERPOWER_GAMES_CONFIG, GAMERPOWER_LOOT_CONFIG]:
            results = process_single_gamerpower_feed(config)
            await generate_feed_and_redirect(config, results, webhook_manager, db_manager, "gamerpower")

        # Process Itch.io feed
        results = await process_feed_with_db(ITCHIO_GAMES_CONFIG, db_manager)
        await generate_feed_and_redirect(ITCHIO_GAMES_CONFIG, results, webhook_manager, db_manager)

        # Process Ivy League feed
        results = await process_feed_with_db(IVY_LEAGUE_CONFIG, db_manager)
        await generate_feed_and_redirect(IVY_LEAGUE_CONFIG, results, webhook_manager, db_manager)

        # Process Udemy feeds
        all_results = []
        for feed_config in FEEDS:
            results = await process_feed_with_db(feed_config, db_manager)
            if results:
                all_results.extend(results)

        if all_results:
            try:
                feed = create_merged_rss_feed(
                    all_results,
                    "Merged Udemy Courses Feed",
                    "Combined feed of free Udemy courses from multiple sources",
                    "https://www.udemy.com",
                    []
                )
                
                if feed:
                    if not feed.startswith('<?xml'):
                        feed = '<?xml version="1.0" encoding="UTF-8"?>\n' + feed
                    
                    feed_path = os.path.join('public/feeds', 'scraped_xml_feed.xml')
                    
                    # Compare with previous feed to find new items
                    new_items = compare_feed_items(feed_path, feed)
                    
                    # Save original feed
                    with open(feed_path, 'w', encoding='utf-8') as f:
                        f.write(feed)
                    logging.info(f"Generated {feed_path}")
                    
                    # Create and save redirect feed
                    redirect_feed = create_redirect_feed(feed, "Merged Udemy Courses Feed")
                    if redirect_feed:
                        redirect_path = os.path.join('public/feeds', 'redirect_scraped_xml_feed.xml')
                        with open(redirect_path, 'w', encoding='utf-8') as f:
                            f.write(redirect_feed)
                        logging.info(f"Generated {redirect_path}")

                    # Store new items in database and notify webhooks
                    if new_items:
                        for item in new_items:
                            await db_manager.add_feed_item(item)
                        await webhook_manager.notify_feed_update('scraped_xml_feed', new_items)
                        
            except Exception as e:
                logging.error(f"Error generating merged feed: {str(e)}")
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())