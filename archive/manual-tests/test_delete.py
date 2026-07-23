if __name__ == "__main__":
    import asyncio
    from app.db.session import get_db_session
    from sqlalchemy import text

    async def test():
        async with get_db_session() as session:
            result = await session.execute(
                text("SELECT id, original_filename FROM documents LIMIT 1")
            )
            row = result.fetchone()
            print(row if row else "No documents found")

    asyncio.run(test())
