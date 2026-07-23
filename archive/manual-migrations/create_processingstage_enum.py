import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.db.session import engine
from sqlalchemy import text


async def create_processingstage_enum():
    async with engine.begin() as conn:
        # Create processingstage enum with uppercase values to match Python enum
        await conn.execute(
            text("""
            DO $$ BEGIN
                CREATE TYPE processingstage AS ENUM ('UPLOADED', 'EXTRACTING', 'CHUNKING', 'EMBEDDING', 'INDEXING', 'COMPLETED', 'FAILED');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        )

        print("ProcessingStage enum type created successfully")


asyncio.run(create_processingstage_enum())
