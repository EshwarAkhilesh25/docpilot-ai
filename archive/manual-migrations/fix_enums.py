import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.db.session import engine
from sqlalchemy import text


async def fix_enums():
    async with engine.begin() as conn:
        # Drop existing enums
        await conn.execute(text("DROP TYPE IF EXISTS filetype CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS processingstatus CASCADE"))

        # Create filetype enum with uppercase values to match Python enum
        await conn.execute(
            text("""
            CREATE TYPE filetype AS ENUM ('PDF', 'AUDIO', 'VIDEO');
        """)
        )

        # Create processingstatus enum with uppercase values to match Python enum
        await conn.execute(
            text("""
            CREATE TYPE processingstatus AS ENUM ('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED');
        """)
        )

        print("Enum types recreated with uppercase values")


asyncio.run(fix_enums())
