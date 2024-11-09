import os
import asyncio
import logging
from db_manager import DBManager
from datetime import datetime
import pytz

# Set environment variables
os.environ["TURSO_DATABASE_URL"] = "libsql://main-goodoffers-db-offren.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzExMjg1MzYsImlkIjoiNzgwNDY1YjktNzc5Yi00YjNhLTgwYzUtZWVlN2Q5NzUxNWI3In0.v7X1lyPpxDOUk123E3EHjTBJ8_LBtFvwOkVylqz9edu2dQjznSe87oBFtRSrNk1PD6OCpmNoiBP31NnGY4HEDA"

async def test_hash_search():
    logging.basicConfig(level=logging.INFO)
    db = DBManager()
    
    try:
        # 1. First simulate storing an item with a known hash
        test_item = {
            'title': 'Test Game',
            'link': 'https://original-content.com/game',
            'description': 'Test description',
            'pub_date': datetime.now(pytz.UTC),
            'item_hash': 'test123',
            'feed_type': 'Videogame',
            'source_url': 'https://www.gamerpower.com'
        }
        
        # Store the test item
        logging.info("Storing test item...")
        success = await db.add_feed_item(test_item)
        if not success:
            logging.error("Failed to store test item")
            return

        # 2. Simulate frontend search using hash
        logging.info("Searching for item by hash...")
        found_item = await db.get_item_by_hash('-834083')
        
        if found_item:
            logging.info("Found item:")
            logging.info(f"Title: {found_item['title']}")
            logging.info(f"Original URL: {found_item['link']}")
            logging.info(f"Feed Type: {found_item['feed_type']}")
        else:
            logging.error("Item not found!")

        # 3. Test with non-existent hash
        logging.info("\nTesting with non-existent hash...")
        not_found = await db.get_item_by_hash('nonexistent')
        if not_found is None:
            logging.info("Correctly returned None for non-existent hash")
        
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(test_hash_search())