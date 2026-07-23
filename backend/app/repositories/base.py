from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository[T]:
    """Base repository class for data access layer."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
