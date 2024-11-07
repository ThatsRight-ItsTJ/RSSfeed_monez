import asyncio
from libsql_client import create_client
import os
import logging
from datetime import datetime
import pytz
from typing import Dict, List, Optional

class DBManager:
    def __init__(self):
        self.client = create_client(
            url=os.environ["TURSO_DATABASE_URL"],
            auth_token=os.environ["TURSO_AUTH_TOKEN"]
        )
        logging.basicConfig(level=logging.INFO)

    async def close(self):
        await self.client.close()

    def generate_ad_copy(self, feed_type: str, title: str) -> str:
        """Generate ad copy using template."""
        return f"🔥 FREE {feed_type} ALERT! 🔥 Get instant access to our premium {title} without spending a single penny - available completely FREE for a limited time only! Don't miss this incredible opportunity to unlock your {feed_type} at zero cost - claim your copy of {title} right now while it's still FREE!"

    async def add_feed_item(self, item: Dict) -> bool:
        try:
            # Generate ad copy from template
            ad_copy = self.generate_ad_copy(item.get('feed_type', 'content'), item['title'])
            
            query = """
                INSERT INTO feeds (
                    feed_type, title, link, description, 
                    pub_date, item_hash, image_url, source_url,
                    adcopy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_hash) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    image_url=excluded.image_url,
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