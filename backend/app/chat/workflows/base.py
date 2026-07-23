"""Base class for Workflow Plugins."""

from abc import ABC, abstractmethod
from typing import Any

from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy


class WorkflowStrategy(ABC):
    """Abstract base class for all AI workflows (e.g. Summarize, MCQ)."""

    @property
    @abstractmethod
    def intent_name(self) -> str:
        """The unique name of the intent handled by this workflow (e.g., 'SUMMARIZE')."""
        pass

    @property
    @abstractmethod
    def minimum_documents(self) -> int:
        """Minimum number of documents required for this workflow."""
        pass

    @property
    @abstractmethod
    def maximum_documents(self) -> int | None:
        """Maximum number of documents supported, or None for unlimited."""
        pass

    @property
    @abstractmethod
    def requires_history(self) -> bool:
        """Whether this workflow needs conversation history."""
        pass

    @abstractmethod
    def get_retrieval_strategy(self) -> RetrievalStrategy:
        """Return the retrieval strategy used for this workflow."""
        pass

    @abstractmethod
    def get_response_formatter(self) -> ResponseFormatter | None:
        """Return the response formatter, or None for raw output."""
        pass

    @abstractmethod
    def get_retrieval_params(self, question: str) -> dict[str, Any]:
        """Return specific parameters (e.g., top_k, search_k) for retrieval."""
        pass

    @abstractmethod
    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        """Build the system and user prompts for the LLM.

        Args:
            question: The user's query.
            context: The retrieved chunks formatted as text.
            history: Conversation history.
            document_profiles: Optional list of document metadata profiles.

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        pass

    def validate_preconditions(self, num_documents: int) -> tuple[bool, str]:
        """Validate if the workflow can run given the context.

        Returns:
            (is_valid, error_message)
        """
        if num_documents < self.minimum_documents:
            return (
                False,
                f"{self.intent_name} requires at least {self.minimum_documents} document(s).",
            )
        if self.maximum_documents is not None and num_documents > self.maximum_documents:
            return (
                False,
                f"{self.intent_name} supports a maximum of {self.maximum_documents} document(s).",
            )
        return True, ""
