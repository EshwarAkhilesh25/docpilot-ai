"""Concrete implementations of job dispatchers."""

from app.jobs.dispatchers.in_process_dispatcher import InProcessJobDispatcher

__all__ = [
    "InProcessJobDispatcher",
]
