"""Exceptions for job dispatching system."""

from app.jobs.exceptions.exceptions import JobDispatchException, JobExecutionException

__all__ = [
    "JobDispatchException",
    "JobExecutionException",
]
