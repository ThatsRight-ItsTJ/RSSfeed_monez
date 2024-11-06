import asyncio
from libsql_client import create_client
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from api_client import AdCopyGenerator

class DBManager:
    def __init__(self):
        self.client = create_client(
            url=os.environ["TURSO_DATABASE_URL"],
            auth_token=os.environ["TURSO_AUTH_TOKEN"]
        )
        self.ad_copy_generator = AdCopyGenerator()
        logging.basicConfig(level=logging.INFO)

    async def close(self):
        await self.client.close()

    async def cleanup_old_entries(self) -> None:
        """Delete entries older than 7 days."""
        try:
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            query = "DELETE FROM feeds WHERE created_at < ?"
            await self.client.execute(query, [seven_days_ago])
            logging.info("Cleaned up entries older than 7 days")
        except Exception as e:
            logging.error(f"Error cleaning up old entries: {e}")

    def generate_prompt(self, feed_type: str, title: str) -> str:
        """Generate prompt for AI to create ad copy."""
        return f"Generate a two sentence Adcopy for a {feed_type} called {title}. Mention how the {feed_type} is being given away for free."

    async def add_feed_item(self, item: Dict) -> bool:
        try:
            # Run cleanup before adding new items
            await self.cleanup_old_entries()
            
            # Generate prompt for the item
            prompt = self.generate_prompt(item.get('feed_type', 'unknown'), item['title'])
            
            # Generate ad copy
            ad_copy = await self.ad_copy_generator.generate_ad_copy(prompt)
            
            query = """
                INSERT INTO feeds (
                    feed_type, title, link, description, 
                    pub_date, item_hash, image_url, source_url,
                    prompt, adcopy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_hash) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    image_url=excluded.image_url,
                    prompt=excluded.prompt,
                    adcopy=excluded.adcopy
            """
            
            await self.client.execute(query, [
                item.get('feed_type', 'unknown'),
                item['title'],
                item['link'],
                item.get('description', ''),
                item['pub_date'].isoformat(),
                item['item_hash'],
                item.get('image_url'),
                item.get('source_url'),
                prompt,
                ad_copy
            ])
            
            logging.info(f"Added/Updated item: {item['title']} ({item['item_hash']})")
            return True
        except Exception as e:
            logging.error(f"Error adding feed item: {e}")
            return False

    async def get_feed_items(self, feed_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        try:
            if feed_type:
                query = "SELECT * FROM feeds WHERE feed_type = ? ORDER BY pub_date DESC LIMIT ?"
                result = await self.client.execute(query, [feed_type, limit])
            else:
                query = "SELECT * FROM feeds ORDER BY pub_date DESC LIMIT ?"
                result = await self.client.execute(query, [limit])

            return [dict(zip(result.columns, row)) for row in result.rows]
        except Exception as e:
            logging.error(f"Error getting feed items: {e}")
            return []

    async def get_item_by_hash(self, item_hash: str) -> Optional[Dict]:
        try:
            result = await self.client.execute(
                "SELECT * FROM feeds WHERE item_hash = ? LIMIT 1",
                [item_hash]
            )
            if result.rows:
                return dict(zip(result.columns, result.rows[0]))
            return None
        except Exception as e:
            logging.error(f"Error getting item by hash: {e}")
            return None

    async def update_adcopy(self, item_hash: str, adcopy: str) -> bool:
        """Update the adcopy for a specific item."""
        try:
            await self.client.execute(
                "UPDATE feeds SET adcopy = ? WHERE item_hash = ?",
                [adcopy, item_hash]
            )
            logging.info(f"Updated adcopy for item {item_hash}")
            return True
        except Exception as e:
            logging.error(f"Error updating adcopy: {e}")
            return False