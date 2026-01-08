"""Add thread_id column to conversations table for OpenAI Agent SDK."""
import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def add_thread_id_column():
    """Add thread_id column to conversations table."""
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
            WHERE table_name='conversations' AND column_name='thread_id'
        """)

        if result is None:
            # Add the column
            await conn.execute("""
                ALTER TABLE conversations
                ADD COLUMN thread_id VARCHAR(100)
            """)

            # Add index for better query performance
            await conn.execute("""
                CREATE INDEX idx_conversations_thread_id ON conversations(thread_id)
            """)

            print("SUCCESS: Added 'thread_id' column to conversations table")
        else:
            print("INFO: Column 'thread_id' already exists")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_thread_id_column())
