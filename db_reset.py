import asyncio
from libsql_client import create_client
import os
import logging

# Set environment variables
os.environ["TURSO_DATABASE_URL"] = "libsql://main-goodoffers-db-offren.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzExMjg1MzYsImlkIjoiNzgwNDY1YjktNzc5Yi00YjNhLTgwYzUtZWVlN2Q5NzUxNWI3In0.v7X1lyPpxDOUk123E3EHjTBJ8_LBtFvwOkVylqz9edu2dQjznSe87oBFtRSrNk1PD6OCpmNoiBP31NnGY4HEDA"

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