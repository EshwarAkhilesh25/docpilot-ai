"""Prompt templates for RAG."""

RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided document context.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY using the information provided in the context below.
2. Do NOT use any outside knowledge or information not present in the context.
3. If the answer cannot be derived from the context, explicitly state: "I don't have enough information in the uploaded documents."
4. Do NOT hallucinate or make up information.
5. Do NOT fabricate facts or combine outside knowledge with retrieved information.
6. Do NOT mention context blocks, page numbers, or reference labels in your answer. Just provide the information naturally.
7. Be concise and direct in your responses.
8. If multiple context blocks provide relevant information, synthesize them into a coherent answer without mentioning the source.
9. If the retrieved context is insufficient or irrelevant to the question, clearly indicate this.
10. Never assume information that is not explicitly stated in the context.
11. Answer ONLY the current question. Do NOT repeat or reference previous questions or answers in the conversation.
12. Provide a fresh answer for each question without including information from previous exchanges.
13. CRITICAL: When conversation history is provided, use it ONLY for context about what has been discussed. Do NOT repeat, summarize, or reference previous answers in your response. Your response must be a direct answer to the current question only.
14. Do NOT include phrases like "As I mentioned before" or "As discussed earlier" - just answer the current question directly.
15. Your response should be self-contained and answer only what is being asked right now."""


RAG_USER_PROMPT = """CONTEXT:
{context}

USER QUESTION:
{question}

Answer:"""


def build_rag_prompts(context: str, question: str) -> tuple[str, str]:
    """Build separate system and user prompts for RAG.

    Args:
        context: The retrieved document context.
        question: The user's question.

    Returns:
        Tuple of (system_prompt, user_prompt).
    """
    system_prompt = RAG_SYSTEM_PROMPT
    user_prompt = RAG_USER_PROMPT.format(context=context, question=question)
    return system_prompt, user_prompt


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string with numbered blocks.

    Args:
        chunks: List of chunk dictionaries with text and metadata.

    Returns:
        Formatted context string with numbered context blocks including page numbers.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        text = chunk.get("text", "")
        page = chunk.get("page", None)

        if page is not None:
            context_parts.append(f"[Context {i}]\nPage: {page}\n{text}")
        else:
            context_parts.append(f"[Context {i}]\n{text}")

    return "\n\n".join(context_parts)


SUMMARY_SYSTEM_PROMPT = """You are a helpful AI assistant that summarizes documents.

IMPORTANT INSTRUCTIONS:
1. Summarize ONLY the provided document text below.
2. Do NOT use any outside knowledge or information not present in the text.
3. Do NOT hallucinate or make up information.
4. Remain concise - aim for 2-4 paragraphs maximum.
5. Preserve factual information accurately.
6. Avoid excessive bullet points - use readable paragraphs instead.
7. Focus on the main topics, key points, and overall purpose of the document.
8. If the text is very short, provide a brief 1-2 sentence summary."""


def get_summary_prompt() -> str:
    """Get the summarization system prompt.

    Returns:
        The summarization prompt string.
    """
    return SUMMARY_SYSTEM_PROMPT
