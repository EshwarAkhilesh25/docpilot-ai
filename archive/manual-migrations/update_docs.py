import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text


async def update_doc():
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE documents SET processing_status = completed")
        )
        await session.commit()
        print("Updated documents")


asyncio.run(update_doc())
