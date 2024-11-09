import asyncio
from libsql_client import create_client
import os
import logging
from datetime import datetime, timedelta

# Set environment variables
os.environ["TURSO_DATABASE_URL"] = "libsql://main-goodoffers-db-offren.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzExMjg1MzYsImlkIjoiNzgwNDY1YjktNzc5Yi00YjNhLTgwYzUtZWVlN2Q5NzUxNWI3In0.v7X1lyPpxDOUk123E3EHjTBJ8_LBtFvwOkVylqz9edu2dQjznSe87oBFtRSrNk1PD6OCpmNoiBP31NnGY4HEDA"

class DBInitializer:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1
        self.client = None

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

    async def execute_with_retry(self, query: str):
        """Execute database query with retry logic."""
        for attempt in range(self.max_retries):
            try:
                client = await self.get_client()
                return await client.execute(query)
            except Exception as e:
                if "WEBSOCKET" in str(e).upper():
                    self.client = None  # Reset client on WebSocket error
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def init_db(self):
        """Initialize database with retry logic."""
        try:
            # Create feeds table with history tracking
            await self.execute_with_retry("""
                CREATE TABLE IF NOT EXISTS feeds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    description TEXT,
                    pub_date TEXT NOT NULL,
                    item_hash TEXT NOT NULL,
                    image_url TEXT,
                    source_url TEXT,
                    adcopy TEXT,
                    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better performance
            await self.execute_with_retry("""
                CREATE INDEX IF NOT EXISTS idx_feeds_hash 
                ON feeds(item_hash)
            """)

            await self.execute_with_retry("""
                CREATE INDEX IF NOT EXISTS idx_feeds_dates 
                ON feeds(first_seen_at, last_seen_at)
            """)

            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
        finally:
            if self.client:
                await self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initializer = DBInitializer()
    asyncio.run(initializer.init_db())