import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.db.session import engine
from sqlalchemy import text


async def create_enums():
    async with engine.begin() as conn:
        # Create filetype enum
        await conn.execute(
            text("""
            DO $$ BEGIN
                CREATE TYPE filetype AS ENUM ('pdf', 'audio', 'video');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        )

        # Create processingstatus enum
        await conn.execute(
            text("""
            DO $$ BEGIN
                CREATE TYPE processingstatus AS ENUM ('uploaded', 'processing', 'completed', 'failed');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        )

        print("Enum types created successfully")


asyncio.run(create_enums())
