import asyncio
from libsql_client import create_client
import os
import logging

async def init_db():
    client = create_client(
        url=os.environ["TURSO_DATABASE_URL"],
        auth_token=os.environ["TURSO_AUTH_TOKEN"]
    )

    try:
        # Drop existing table if it exists
        await client.execute("DROP TABLE IF EXISTS feeds")
        
        # Create feeds table with title as unique constraint
        await client.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_type TEXT NOT NULL,
                title TEXT NOT NULL UNIQUE,
                link TEXT NOT NULL,
                description TEXT,
                pub_date TEXT NOT NULL,
                item_hash TEXT NOT NULL,
                image_url TEXT,
                source_url TEXT,
                adcopy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())
