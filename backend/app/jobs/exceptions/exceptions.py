"""Exceptions for job dispatching system."""


class JobDispatchException(Exception):
    """Exception raised when a job cannot be dispatched.

    This exception is raised when there is an error enqueuing a job
    for background processing.
    """

    pass


class JobExecutionException(Exception):
    """Exception raised when a job execution fails.

    This exception is raised when a background job encounters an error
    during execution.
    """

    pass
