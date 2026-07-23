"""General QA Workflow (Fallback)."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class GeneralQAWorkflow(WorkflowStrategy):
    """Workflow for answering specific factual questions from the document."""

    @property
    def intent_name(self) -> str:
        return "GENERAL_QA"

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
        return {"top_k": 5, "search_k": 20}

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided document context.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY using the information provided in the context below.
2. Do NOT use outside knowledge.
3. If the answer cannot be derived from the context, state: "I don't have enough information in the uploaded documents."
4. Be concise and direct.
5. You may use conversation history for context about the current question, but prioritize answering the new question directly."""

        user_prompt = f"""CONTEXT:
{context}

USER QUESTION:
{question}

Answer:"""
        return system_prompt, user_prompt
