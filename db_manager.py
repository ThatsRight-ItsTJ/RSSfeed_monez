import asyncio
from libsql_client import create_client
import os
import logging
from datetime import datetime, timedelta
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
            current_time = datetime.now(pytz.UTC)
            recent_window = (current_time - timedelta(hours=24)).isoformat()
            
            # Check for recent duplicates
            result = await self.client.execute("""
                SELECT id, last_seen_at FROM feeds 
                WHERE item_hash = ? AND last_seen_at > ?
                LIMIT 1
            """, [item['item_hash'], recent_window])

            if result.rows:
                # Update last_seen_at for recent items
                await self.client.execute("""
                    UPDATE feeds 
                    SET last_seen_at = ? 
                    WHERE id = ?
                """, [current_time.isoformat(), result.rows[0][0]])
                return True

            # Generate ad copy
            ad_copy = self.generate_ad_copy(item.get('feed_type', 'content'), item['title'])
            
            # Insert new item
            await self.client.execute("""
                INSERT INTO feeds (
                    feed_type, title, link, description, 
                    pub_date, item_hash, image_url, source_url,
                    adcopy, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                item.get('feed_type', 'unknown'),
                item['title'],
                item['link'],
                item.get('description', ''),
                item['pub_date'].isoformat(),
                item['item_hash'],
                item.get('image_url'),
                item.get('source_url'),
                ad_copy,
                current_time.isoformat(),
                current_time.isoformat()
            ])
            
            logging.info(f"Added new item: {item['title']} ({item['item_hash']})")
            return True
        except Exception as e:
            logging.error(f"Error adding feed item: {e}")
            return False

    async def get_feed_items(self, feed_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        try:
            if feed_type:
                query = "SELECT * FROM feeds WHERE feed_type = ? ORDER BY last_seen_at DESC LIMIT ?"
                result = await self.client.execute(query, [feed_type, limit])
            else:
                query = "SELECT * FROM feeds ORDER BY last_seen_at DESC LIMIT ?"
                result = await self.client.execute(query, [limit])

            return [dict(zip(result.columns, row)) for row in result.rows]
        except Exception as e:
            logging.error(f"Error getting feed items: {e}")
            return []

    async def get_item_by_hash(self, item_hash: str) -> Optional[Dict]:
        try:
            result = await self.client.execute(
                "SELECT * FROM feeds WHERE item_hash = ? ORDER BY last_seen_at DESC LIMIT 1",
                [item_hash]
            )
            if result.rows:
                return dict(zip(result.columns, result.rows[0]))
            return None
        except Exception as e:
            logging.error(f"Error getting item by hash: {e}")
            return None