from app.db.session import get_db


async def get_database():
    """Dependency injection for database session."""
    async for session in get_db():
        yield session
