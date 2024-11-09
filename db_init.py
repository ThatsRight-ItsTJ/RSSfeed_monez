import asyncio
from libsql_client import create_client
import os
import logging
from datetime import datetime, timedelta

async def init_db():
    client = create_client(
        url=os.environ["TURSO_DATABASE_URL"],
        auth_token=os.environ["TURSO_AUTH_TOKEN"]
    )

    try:
        # Create feeds table with history tracking
        await client.execute("""
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
        await client.execute("""
            CREATE INDEX IF NOT EXISTS idx_feeds_hash 
            ON feeds(item_hash)
        """)

        await client.execute("""
            CREATE INDEX IF NOT EXISTS idx_feeds_dates 
            ON feeds(first_seen_at, last_seen_at)
        """)

        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())