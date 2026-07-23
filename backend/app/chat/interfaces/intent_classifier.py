"""Interface for Intent Classification."""

from abc import ABC, abstractmethod


class IntentClassifier(ABC):
    """Abstract interface for classifying the intent of a user's question.

    The intent determines which WorkflowStrategy will handle the request.
    """

    @abstractmethod
    async def classify(self, question: str) -> str:
        """Classify the intent of the question.

        Args:
            question: The user's question.

        Returns:
            The name of the intent/workflow (e.g., 'SUMMARIZE', 'GENERAL_QA').
        """
        pass
