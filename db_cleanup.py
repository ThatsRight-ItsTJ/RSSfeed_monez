import asyncio
import logging
from libsql_client import create_client
import os
from datetime import datetime
import pytz

# Set environment variables
os.environ["TURSO_DATABASE_URL"] = "libsql://main-goodoffers-db-offren.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzExMjg1MzYsImlkIjoiNzgwNDY1YjktNzc5Yi00YjNhLTgwYzUtZWVlN2Q5NzUxNWI3In0.v7X1lyPpxDOUk123E3EHjTBJ8_LBtFvwOkVylqz9edu2dQjznSe87oBFtRSrNk1PD6OCpmNoiBP31NnGY4HEDA"

class DBCleaner:
    def __init__(self):
        self.client = None
        self.max_retries = 3
        self.retry_delay = 1

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

    async def cleanup_duplicates(self):
        """Clean up duplicate entries based on title and link."""
        try:
            # Find duplicates
            duplicates = await self.execute_with_retry("""
                WITH duplicates AS (
                    SELECT id,
                           title,
                           link,
                           ROW_NUMBER() OVER (
                               PARTITION BY title, link
                               ORDER BY last_seen_at DESC
                           ) as row_num
                    FROM feeds
                )
                SELECT id FROM duplicates WHERE row_num > 1
            """)

            if not duplicates.rows:
                logging.info("No duplicates found")
                return

            duplicate_ids = [row[0] for row in duplicates.rows]
            logging.info(f"Found {len(duplicate_ids)} duplicate entries")

            # Delete duplicates
            deleted = await self.execute_with_retry(
                "DELETE FROM feeds WHERE id IN (" + ",".join("?" * len(duplicate_ids)) + ")",
                duplicate_ids
            )

            logging.info(f"Deleted {len(duplicate_ids)} duplicate entries")

            # Log cleanup timestamp
            await self.execute_with_retry(
                "INSERT INTO cleanup_log (cleanup_time, entries_removed) VALUES (?, ?)",
                [datetime.now(pytz.UTC).isoformat(), len(duplicate_ids)]
            )

        except Exception as e:
            logging.error(f"Error cleaning up duplicates: {e}")
        finally:
            if self.client:
                await self.client.close()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create cleanup_log table if it doesn't exist
    cleaner = DBCleaner()
    try:
        await cleaner.execute_with_retry("""
            CREATE TABLE IF NOT EXISTS cleanup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cleanup_time TEXT NOT NULL,
                entries_removed INTEGER NOT NULL
            )
        """)
        
        # Run cleanup
        await cleaner.cleanup_duplicates()
        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
    finally:
        if cleaner.client:
            await cleaner.client.close()

if __name__ == "__main__":
    asyncio.run(main())