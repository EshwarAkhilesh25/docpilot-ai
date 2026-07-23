"""Key Findings Workflow."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class KeyFindingsWorkflow(WorkflowStrategy):
    """Workflow for extracting key findings from documents."""

    @property
    def intent_name(self) -> str:
        return "KEY_FINDINGS"

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
        return {"top_k": 15}

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        system_prompt = """You are an expert analyst specialized in extracting critical insights and key findings from text.

IMPORTANT INSTRUCTIONS:
1. Extract and list the most important findings, insights, or takeaways from the provided text.
2. Structure your response using bullet points for clarity.
3. Be concise but comprehensive.
4. ONLY rely on the provided context. If no relevant key findings are present, state that clearly."""

        user_prompt = f"""Context from documents:
{context}

User Request: {question}"""

        return system_prompt, user_prompt
