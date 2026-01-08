"""Manual migration script to add password authentication fields to users table.

This script adds:
- name column (optional)
- hashed_password column (required)

Run this script once to update the database schema for secure authentication.

Usage:
    python -m src.db.migrations.add_password_auth
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv
from sqlalchemy import text

from src.db.connection import engine

# Load environment variables
load_dotenv()


async def add_password_auth_columns():
    """Add name and hashed_password columns to users table."""
    print("Adding password authentication columns to users table...")

    async with engine.begin() as conn:
        # Check if columns already exist
        result = await conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN ('name', 'hashed_password')
                """
            )
        )
        existing_columns = {row[0] for row in result.fetchall()}

        # Add name column if it doesn't exist
        if "name" not in existing_columns:
            print("  Adding 'name' column...")
            await conn.execute(
                text("ALTER TABLE users ADD COLUMN name VARCHAR(255)")
            )
        else:
            print("  'name' column already exists, skipping...")

        # Add hashed_password column if it doesn't exist
        if "hashed_password" not in existing_columns:
            print("  Adding 'hashed_password' column...")
            await conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255) DEFAULT ''"
                )
            )
        else:
            print("  'hashed_password' column already exists, skipping...")

    print("Migration completed successfully!")
    print()
    print("IMPORTANT: Existing users will have empty passwords.")
    print("   They need to reset their passwords or create new accounts.")


async def main():
    """Run the migration."""
    try:
        await add_password_auth_columns()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
