import pytest

import asyncio
from app.db.session import get_db


@pytest.mark.asyncio
async def test_db():
    async for session in get_db():
        print("Database connection successful")
        print(f"Session type: {type(session)}")
        break


asyncio.run(test_db())
