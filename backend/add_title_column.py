"""Add title column to conversations table."""
import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def add_title_column():
    """Add title column to conversations table."""
    database_url = os.getenv("DATABASE_URL")

    # Convert SQLAlchemy URL to asyncpg URL
    if database_url and database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(database_url)

    try:
        # Check if column exists
        result = await conn.fetchval("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='conversations' AND column_name='title'
        """)

        if result is None:
            # Add the column
            await conn.execute("""
                ALTER TABLE conversations
                ADD COLUMN title VARCHAR(200)
            """)
            print("SUCCESS: Added 'title' column to conversations table")
        else:
            print("INFO: Column 'title' already exists")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_title_column())
