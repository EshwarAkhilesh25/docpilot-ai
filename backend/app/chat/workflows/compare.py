"""Compare Documents Workflow."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class CompareWorkflow(WorkflowStrategy):
    """Workflow for comparing two or more documents."""

    @property
    def intent_name(self) -> str:
        return "COMPARE"

    @property
    def minimum_documents(self) -> int:
        return 1

    @property
    def maximum_documents(self) -> int | None:
        return None

    @property
    def requires_history(self) -> bool:
        return False

    def get_retrieval_strategy(self) -> RetrievalStrategy:
        return HybridRetrievalStrategy()

    def get_response_formatter(self) -> ResponseFormatter | None:
        return MarkdownFormatter()

    def get_retrieval_params(self, question: str) -> dict[str, Any]:
        return {"top_k": 20}

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        system_prompt = """You are an expert analyst specialized in comparing documents.

IMPORTANT INSTRUCTIONS:
1. Analyze the provided context from the documents and highlight similarities, differences, and contrasting viewpoints.
2. Structure your comparison logically. You may use tables or bulleted lists for clarity.
3. Clearly attribute points to their respective sources when possible.
4. ONLY rely on the provided context. Do not invent information."""

        user_prompt = f"""Context from documents:
{context}

User Request: {question}"""

        return system_prompt, user_prompt
