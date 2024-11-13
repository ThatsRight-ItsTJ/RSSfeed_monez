import asyncio
import logging
from libsql_client import create_client
import os
from datetime import datetime
import pytz
import aiohttp
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebhookMonitor:
    def __init__(self):
        self.client = None
        self.max_retries = 3
        self.retry_delay = 1
        
        # Verify all required environment variables are present
        required_vars = ['WEBHOOK_IVY_LEAGUE', 'WEBHOOK_UDEMY', 'WEBHOOK_ITCHIO', 
                        'WEBHOOK_VIDEOGAME', 'WEBHOOK_DLC']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        self.webhooks = {
            'Ivy_League_Course': os.getenv('WEBHOOK_IVY_LEAGUE'),
            'Udemy_Course': os.getenv('WEBHOOK_UDEMY'),
            'itchio_game': os.getenv('WEBHOOK_ITCHIO'),
            'Videogame': os.getenv('WEBHOOK_VIDEOGAME'),
            'DLC': os.getenv('WEBHOOK_DLC')
        }
        self.base_url = "https://www.goodoffers.theworkpc.com/?hash="

    async def get_client(self):
        """Get database client with connection retry logic."""
        if not self.client:
            for attempt in range(self.max_retries):
                try:
                    self.client = create_client(
                        url=os.getenv("TURSO_DATABASE_URL"),
                        auth_token=os.getenv("TURSO_AUTH_TOKEN")
                    )
                    return self.client
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
        return self.client

    async def execute_with_retry(self, query: str, params=None):
        """Execute database query with retry logic."""
        for attempt in range(self.max_retries):
            try:
                client = await self.get_client()
                return await client.execute(query, params or [])
            except Exception as e:
                if "WEBSOCKET" in str(e).upper():
                    self.client = None  # Reset client on WebSocket error
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def create_webhook_log_table(self):
        """Create webhook log table if it doesn't exist."""
        await self.execute_with_retry("""
            CREATE TABLE IF NOT EXISTS webhook_sent_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_hash TEXT NOT NULL,
                feed_type TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                UNIQUE(item_hash, feed_type)
            )
        """)

    async def is_item_sent(self, item_hash: str, feed_type: str) -> bool:
        """Check if an item has already been sent to webhooks."""
        result = await self.execute_with_retry("""
            SELECT 1 FROM webhook_sent_log 
            WHERE item_hash = ? AND feed_type = ?
        """, [item_hash, feed_type])
        return bool(result.rows)

    async def mark_item_sent(self, item_hash: str, feed_type: str):
        """Mark an item as sent to webhooks."""
        try:
            await self.execute_with_retry("""
                INSERT INTO webhook_sent_log (item_hash, feed_type, sent_at)
                VALUES (?, ?, ?)
            """, [item_hash, feed_type, datetime.now(pytz.UTC).isoformat()])
        except Exception as e:
            logging.error(f"Error marking item as sent: {e}")

    async def send_webhook(self, webhook_url: str, content: str):
        """Send message to webhook."""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(webhook_url, json={'content': content})
                logging.info(f"Webhook notification sent successfully")
        except Exception as e:
            logging.error(f"Error sending webhook: {e}")

    async def process_new_entries(self):
        """Process new database entries and send webhook notifications."""
        try:
            # Get all entries ordered by creation time
            query = """
                SELECT feed_type, adcopy, item_hash 
                FROM feeds 
                ORDER BY created_at ASC
            """
            
            result = await self.execute_with_retry(query)

            if not result.rows:
                logging.info("No entries found")
                return

            # Process each entry
            for row in result.rows:
                feed_type, adcopy, item_hash = row
                
                # Skip if not a supported feed type or already sent
                if feed_type not in self.webhooks or await self.is_item_sent(item_hash, feed_type):
                    continue

                webhook_url = self.webhooks[feed_type]
                content = f"{adcopy}\n{self.base_url}{item_hash}"
                
                # Send webhook and mark as sent
                await self.send_webhook(webhook_url, content)
                await self.mark_item_sent(item_hash, feed_type)
                logging.info(f"Processed new {feed_type} entry: {item_hash}")

        except Exception as e:
            logging.error(f"Error processing new entries: {e}")

    async def monitor(self):
        """Main monitoring function."""
        try:
            # Ensure webhook log table exists
            await self.create_webhook_log_table()

            # Process new entries
            await self.process_new_entries()

        except Exception as e:
            logging.error(f"Error during monitoring: {e}")
        finally:
            if self.client:
                await self.client.close()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        monitor = WebhookMonitor()
        await monitor.monitor()
    except EnvironmentError as e:
        logging.error(str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())