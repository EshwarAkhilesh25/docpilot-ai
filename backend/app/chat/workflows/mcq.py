"""MCQ Generation Workflow."""

from typing import Any

from app.chat.formatters.json_formatter import JSONFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class MCQWorkflow(WorkflowStrategy):
    """Workflow for generating Multiple Choice Questions."""

    @property
    def intent_name(self) -> str:
        return "MCQ"

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
        return JSONFormatter()

    def get_retrieval_params(self, question: str) -> dict[str, Any]:
        return {
            "top_k": 15,  # Need high coverage for good questions
            "search_k": 40,
        }

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        system_prompt = """You are an expert educator who creates challenging and accurate Multiple Choice Questions based on provided documents.

IMPORTANT INSTRUCTIONS:
1. Base all questions strictly on the provided context. Do NOT use outside knowledge.
2. Ensure there is only one unambiguously correct answer per question.
3. Provide plausible distractors (incorrect options).
4. Output the result ONLY as a valid JSON array of objects. Do not include any other text.
5. Format:
[
  {
    "question": "What is the main component of X?",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "explanation": "The text states that X is primarily composed of A."
  }
]"""

        user_prompt = f"""CONTEXT:
{context}

USER REQUEST:
{question}

Generate the MCQs as requested."""
        return system_prompt, user_prompt
