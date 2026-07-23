"""Action Items Workflow."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class ActionItemsWorkflow(WorkflowStrategy):
    """Workflow for extracting action items from documents."""

    @property
    def intent_name(self) -> str:
        return "ACTION_ITEMS"

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
        return {"top_k": 10}

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        system_prompt = """You are an expert assistant specialized in identifying action items, tasks, and next steps from text.

IMPORTANT INSTRUCTIONS:
1. Extract any action items, tasks, deadlines, or next steps mentioned in the text.
2. Present the action items as a checklist using Markdown checkboxes (e.g. - [ ] Task name).
3. Include the assignee and deadline if mentioned.
4. ONLY rely on the provided context. If no action items exist, state that clearly."""

        user_prompt = f"""Context from documents:
{context}

User Request: {question}"""

        return system_prompt, user_prompt
