import asyncio
from libsql_client import create_client
import os
import logging

async def reset_db():
    client = create_client(
        url=os.environ["TURSO_DATABASE_URL"],
        auth_token=os.environ["TURSO_AUTH_TOKEN"]
    )

    try:
        # Drop existing tables
        await client.execute("DROP TABLE IF EXISTS feeds")
        logging.info("Existing tables dropped successfully")
        
    except Exception as e:
        logging.error(f"Error dropping tables: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reset_db())