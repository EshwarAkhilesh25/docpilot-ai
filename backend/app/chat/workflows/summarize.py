"""Summarize Workflow."""

from typing import Any

from app.chat.formatters.markdown_formatter import MarkdownFormatter
from app.chat.interfaces.response_formatter import ResponseFormatter
from app.chat.interfaces.retrieval_strategy import RetrievalStrategy
from app.chat.strategies.whole_document_retrieval import WholeDocumentRetrievalStrategy
from app.chat.workflows.base import WorkflowStrategy


class SummarizeWorkflow(WorkflowStrategy):
    """Workflow for summarizing full documents."""

    @property
    def intent_name(self) -> str:
        return "SUMMARIZE"

    @property
    def minimum_documents(self) -> int:
        return 1

    @property
    def maximum_documents(self) -> int | None:
        return 3  # Prevent token overflow

    @property
    def requires_history(self) -> bool:
        return False

    def get_retrieval_strategy(self) -> RetrievalStrategy:
        return WholeDocumentRetrievalStrategy()

    def get_response_formatter(self) -> ResponseFormatter | None:
        return MarkdownFormatter()

    def get_retrieval_params(self, question: str) -> dict[str, Any]:
        return {"max_chunks": 50}  # Increase to capture more document context

    def build_prompt(
        self,
        question: str,
        context: str,
        history: list[dict],
        document_profiles: list[dict] | None = None,
    ) -> tuple[str, str]:
        # Customize prompt based on document profile if available
        profile_instructions = ""
        if document_profiles:
            doc_types = [p.get("type", "Document") for p in document_profiles]
            if "Resume" in doc_types:
                profile_instructions = "Focus on Skills, Experience, Projects, and Education."
            elif "Medical Report" in doc_types:
                profile_instructions = (
                    "Focus on Diagnosis, Medicines, Tests, and Doctor Recommendations."
                )
            elif "Research Paper" in doc_types:
                profile_instructions = "Focus on Abstract, Methodology, Results, and Conclusion."
            else:
                profile_instructions = "Focus on the main topics, key points, and overall purpose."

        system_prompt = f"""You are an expert analyst who summarizes documents accurately.

IMPORTANT INSTRUCTIONS:
1. Summarize ONLY the provided document text below.
2. Do NOT use any outside knowledge.
3. Organize the summary logically with clear headings (e.g., # Summary, ## Key Points).
4. {profile_instructions}
5. Preserve factual information accurately.
6. Aim for a comprehensive but concise summary."""

        user_prompt = f"""DOCUMENT CONTENT:
{context}

Please provide a detailed summary of the above content."""
        return system_prompt, user_prompt
