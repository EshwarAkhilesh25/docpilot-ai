"""Timeline Workflow."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class TimelineWorkflow(WorkflowStrategy):
    """Workflow for extracting dates and creating a timeline."""

    @property
    def intent_name(self) -> str:
        return "TIMELINE"

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
        system_prompt = """You are an expert assistant specialized in extracting chronological information and important dates.

IMPORTANT INSTRUCTIONS:
1. Extract all important dates, events, or chronological sequences from the provided context.
2. Order them chronologically if possible.
3. Present the information clearly as a timeline or a structured list of dates and events.
4. ONLY rely on the provided context. If no dates or events are found, state that clearly."""

        user_prompt = f"""Context from documents:
{context}

User Request: {question}"""

        return system_prompt, user_prompt
