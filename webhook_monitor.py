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

    async def get_last_run_time(self) -> Optional[str]:
        """Get the timestamp of the last run."""
        try:
            result = await self.execute_with_retry("""
                SELECT last_run FROM webhook_monitor_log 
                ORDER BY last_run DESC LIMIT 1
            """)
            if result.rows:
                return result.rows[0][0]
            return None
        except Exception as e:
            logging.error(f"Error getting last run time: {e}")
            return None

    async def update_last_run_time(self, timestamp: str):
        """Update the last run timestamp."""
        try:
            await self.execute_with_retry("""
                INSERT INTO webhook_monitor_log (last_run) VALUES (?)
            """, [timestamp])
        except Exception as e:
            logging.error(f"Error updating last run time: {e}")

    async def send_webhook(self, webhook_url: str, content: str):
        """Send message to webhook."""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(webhook_url, json={'content': content})
                logging.info(f"Webhook notification sent successfully")
        except Exception as e:
            logging.error(f"Error sending webhook: {e}")

    async def process_new_entries(self, last_run: Optional[str]):
        """Process new database entries and send webhook notifications."""
        try:
            # Get new entries since last run
            query = """
                SELECT feed_type, adcopy, item_hash 
                FROM feeds 
                WHERE created_at > ?
                ORDER BY created_at ASC
            """
            
            result = await self.execute_with_retry(
                query, 
                [last_run or '1970-01-01 00:00:00']
            )

            if not result.rows:
                logging.info("No new entries found")
                return

            # Process each new entry
            for row in result.rows:
                feed_type, adcopy, item_hash = row
                if feed_type in self.webhooks:
                    webhook_url = self.webhooks[feed_type]
                    content = f"{adcopy}\n{self.base_url}{item_hash}"
                    await self.send_webhook(webhook_url, content)
                    logging.info(f"Processed new {feed_type} entry: {item_hash}")

        except Exception as e:
            logging.error(f"Error processing new entries: {e}")

    async def monitor(self):
        """Main monitoring function."""
        try:
            # Create log table if it doesn't exist
            await self.execute_with_retry("""
                CREATE TABLE IF NOT EXISTS webhook_monitor_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_run TEXT NOT NULL
                )
            """)

            # Get last run time
            last_run = await self.get_last_run_time()
            if last_run:
                logging.info(f"Last run: {last_run}")
            else:
                logging.info("First run - will process all entries")

            # Process new entries
            await self.process_new_entries(last_run)

            # Update last run time
            current_time = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
            await self.update_last_run_time(current_time)
            logging.info(f"Updated last run time to: {current_time}")

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