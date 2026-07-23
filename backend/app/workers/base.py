"""Base worker class for background tasks."""


class BaseWorker:
    """Base worker for asynchronous background processing."""

    async def process(self) -> None:
        """Process the background task."""
        raise NotImplementedError("Subclasses must implement process method")
