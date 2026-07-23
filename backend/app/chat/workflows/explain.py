"""Explain Workflow."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class ExplainWorkflow(WorkflowStrategy):
    """Workflow for explaining concepts from documents."""

    @property
    def intent_name(self) -> str:
        return "EXPLAIN"

    @property
    def minimum_documents(self) -> int:
        return 1

    @property
    def maximum_documents(self) -> int | None:
        return None

    @property
    def requires_history(self) -> bool:
        return True

    def get_retrieval_strategy(self) -> RetrievalStrategy:
        return HybridRetrievalStrategy()

    def get_response_formatter(self) -> ResponseFormatter | None:
        return MarkdownFormatter()

    def get_retrieval_params(self, question: str) -> dict[str, Any]:
        return {"top_k": 10}

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        system_prompt = """You are an expert tutor specialized in breaking down complex concepts and explaining them clearly.

IMPORTANT INSTRUCTIONS:
1. Explain the concepts asked by the user in a clear, easy-to-understand manner.
2. Use analogies or examples if helpful, but ensure they accurately reflect the provided context.
3. Maintain a helpful and educational tone.
4. ONLY rely on the provided context. If the concept is not covered in the documents, state that you cannot explain it based on the available information."""

        user_prompt = f"""Context from documents:
{context}

User Request: {question}"""

        return system_prompt, user_prompt
