import asyncio
import logging
from libsql_client import create_client
import os
from datetime import datetime, timedelta
import pytz

class OldEntriesCleaner:
    def __init__(self):
        self.client = None
        self.max_retries = 3
        self.retry_delay = 1
        self.retention_days = 7

    async def get_client(self):
        """Get database client with connection retry logic."""
        if not self.client:
            for attempt in range(self.max_retries):
                try:
                    self.client = create_client(
                        url=os.environ["TURSO_DATABASE_URL"],
                        auth_token=os.environ["TURSO_AUTH_TOKEN"]
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

    async def cleanup_old_entries(self):
        """Clean up entries older than retention_days."""
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.now(pytz.UTC) - timedelta(days=self.retention_days)).isoformat()
            
            # Count entries to be deleted
            count_result = await self.execute_with_retry(
                "SELECT COUNT(*) FROM feeds WHERE created_at < ?",
                [cutoff_date]
            )
            entries_to_delete = count_result.rows[0][0] if count_result.rows else 0
            
            if entries_to_delete == 0:
                logging.info("No old entries found to delete")
                return

            logging.info(f"Found {entries_to_delete} entries older than {self.retention_days} days")

            # Delete old entries
            await self.execute_with_retry(
                "DELETE FROM feeds WHERE created_at < ?",
                [cutoff_date]
            )

            logging.info(f"Successfully deleted {entries_to_delete} old entries")

            # Log cleanup in history
            await self.execute_with_retry(
                "INSERT INTO cleanup_history (cleanup_time, entries_removed, cleanup_type) VALUES (?, ?, ?)",
                [datetime.now(pytz.UTC).isoformat(), entries_to_delete, 'age_based']
            )

        except Exception as e:
            logging.error(f"Error cleaning up old entries: {e}")
        finally:
            if self.client:
                await self.client.close()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create cleanup history table if it doesn't exist
    cleaner = OldEntriesCleaner()
    try:
        await cleaner.execute_with_retry("""
            CREATE TABLE IF NOT EXISTS cleanup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cleanup_time TEXT NOT NULL,
                entries_removed INTEGER NOT NULL,
                cleanup_type TEXT NOT NULL
            )
        """)
        
        # Run cleanup
        await cleaner.cleanup_old_entries()
        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
    finally:
        if cleaner.client:
            await cleaner.client.close()

if __name__ == "__main__":
    asyncio.run(main())