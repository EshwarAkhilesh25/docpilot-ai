"""Chat service for RAG-based document Q&A."""

import logging
import time
import uuid
from collections.abc import Callable
from datetime import UTC
from uuid import UUID

from app.chat.exceptions import ChatException, ContextLengthExceededException
from app.chat.interfaces.llm_provider import LLMProvider
from app.chat.models.chat_response import ChatResponse
from app.chat.models.citation import Citation
from app.chat.models.source import Source
from app.chat.prompts.templates import build_rag_prompts, format_context
from app.core.config import get_settings
from app.retrieval.interfaces.retriever import Retriever
from app.retrieval.models.relevant_chunk import RelevantChunk

logger = logging.getLogger(__name__)

settings = get_settings()


class ChatService:
    """Service for RAG-based chat with documents.

    This service implements the complete RAG pipeline:
    1. Retrieve relevant chunks using semantic search
    2. Build context from retrieved chunks
    3. Generate answer using LLM with retrieved context
    4. Persist conversation history
    5. Return response with sources
    """

    def __init__(
        self,
        uow_factory: Callable,
        retriever: Retriever,
        llm_provider: LLMProvider,
        max_context_length: int = 8000,
        max_history_messages: int = 5,
    ):
        """Initialize the chat service.

        Args:
            uow_factory: Factory function to create UnitOfWork instances.
            retriever: Retriever for semantic search.
            llm_provider: LLM provider for text generation.
            max_context_length: Maximum context length in characters.
            max_history_messages: Number of historical messages to include.
        """
        self._uow_factory = uow_factory
        self._retriever = retriever
        self._llm_provider = llm_provider
        self._max_context_length = max_context_length
        self._max_history_messages = max_history_messages

    async def chat(
        self,
        question: str,
        user_id: UUID,
        session_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
        top_k: int = 5,
        search_k: int = 20,
    ) -> ChatResponse:
        """Process a user question with RAG.

        Args:
            question: The user's question.
            user_id: The user's ID.
            session_id: Optional session ID for conversation continuity.
            document_ids: Optional list of document IDs to filter retrieval.
            top_k: Number of chunks to return after deduplication.
            search_k: Number of chunks to retrieve before deduplication.

        Returns:
            ChatResponse with answer and sources.

        Raises:
            ChatException: If chat processing fails.
        """
        str(uuid.uuid4())
        start_time = time.time()

        try:
            pass

            # Step 1: Retrieve relevant chunks
            retrieval_start = time.time()
            relevant_chunks = await self._retriever.retrieve(
                query=question,
                top_k=top_k,
                search_k=search_k,
                document_ids=document_ids,
            )
            time.time() - retrieval_start

            # Log retrieved chunks
            pass

            # Step 1.5: Validate retrieval results
            validation_result = self._validate_retrieval(relevant_chunks)

            if not validation_result["is_valid"]:
                # Return fallback response without invoking LLM
                pass

                # Still persist conversation with fallback response
                session_id = await self._persist_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    question=question,
                    answer=settings.RAG_FALLBACK_RESPONSE,
                    sources=[],
                    document_ids=document_ids,
                )

                time.time() - start_time

                pass

                return ChatResponse(
                    answer=settings.RAG_FALLBACK_RESPONSE,
                    sources=[],
                    citations=None,
                    session_id=session_id,
                )

            # Step 2: Build context from chunks (filter empty chunks)
            filtered_chunks = self._filter_empty_chunks(relevant_chunks)
            context_chunks = self._prepare_context_chunks(filtered_chunks)
            context = format_context(context_chunks)

            # Validate context length
            if len(context) > self._max_context_length:
                # Truncate context to fit
                context = self._truncate_context(context, self._max_context_length)
                pass

            # Step 3: Build prompts
            system_prompt, user_prompt = build_rag_prompts(context=context, question=question)

            # Log prompts (excluding API key)
            pass

            pass

            # Step 4: Get conversation history if session exists
            history = []
            if session_id:
                history = await self._load_conversation_history(session_id)
                pass

            # Step 5: Generate answer
            llm_start = time.time()
            if history:
                # Use history-aware generation
                messages = self._build_messages_with_history(system_prompt, user_prompt, history)
                pass
                answer = await self._llm_provider.generate_with_history(
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7,
                )
            else:
                # Simple generation without history
                pass
                answer = await self._llm_provider.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=1024,
                    temperature=0.7,
                )
            time.time() - llm_start

            # Step 6: Build sources and citations (use filtered chunks)
            sources = self._build_sources(filtered_chunks)
            citations = self._build_citations(filtered_chunks)

            # Step 7: Persist conversation
            session_id = await self._persist_conversation(
                user_id=user_id,
                session_id=session_id,
                question=question,
                answer=answer,
                sources=sources,
                document_ids=document_ids,
            )

            time.time() - start_time

            pass

            return ChatResponse(
                answer=answer,
                sources=sources,
                citations=citations,
                session_id=session_id,
            )

        except ContextLengthExceededException:
            raise
        except Exception as e:
            time.time() - start_time
            pass
            raise ChatException(f"Chat request failed: {e}")

    def _prepare_context_chunks(self, chunks: list[RelevantChunk]) -> list[dict]:
        """Prepare chunks for context formatting.

        Args:
            chunks: List of RelevantChunk objects.

        Returns:
            List of chunk dictionaries for formatting.
        """
        context_chunks = []
        for chunk in chunks:
            context_chunks.append(
                {
                    "text": chunk.text,
                    "page": chunk.start_page,
                }
            )
        return context_chunks

    def _filter_empty_chunks(self, chunks: list[RelevantChunk]) -> list[RelevantChunk]:
        """Filter out chunks with empty or whitespace-only text.

        Args:
            chunks: List of RelevantChunk objects.

        Returns:
            List of RelevantChunk objects with non-empty text.
        """
        return [chunk for chunk in chunks if chunk.text and chunk.text.strip()]

    def _validate_retrieval(self, chunks: list[RelevantChunk]) -> dict:
        """Validate retrieval results before LLM invocation.

        Args:
            chunks: List of RelevantChunk objects.

        Returns:
            Dictionary with:
            - is_valid: bool
            - reason: str (if invalid)
            - highest_similarity: float
        """
        # Detailed logging for validation debugging
        len(chunks)
        similarities = [c.similarity_score for c in chunks] if chunks else []
        highest_similarity = max(similarities) if similarities else 0.0
        sum(similarities) / len(similarities) if similarities else 0.0

        pass

        # Check if we have any valid chunks above threshold
        is_valid = False
        reason = None

        if not chunks:
            reason = "No relevant context found in documents."
        elif highest_similarity < settings.RAG_MIN_SIMILARITY_THRESHOLD:
            reason = f"Highest similarity score ({highest_similarity:.4f}) is below threshold ({settings.RAG_MIN_SIMILARITY_THRESHOLD})."
        else:
            is_valid = True

        return {
            "is_valid": is_valid,
            "reason": reason,
            "highest_similarity": highest_similarity,
        }

    def _truncate_context(self, context: str, max_length: int) -> str:
        """Truncate context to fit max length.

        Args:
            context: The context string.
            max_length: Maximum allowed length.

        Returns:
            Truncated context string.
        """
        if len(context) <= max_length:
            return context

        # Truncate at a reasonable point (end of a context block)
        truncated = context[:max_length]
        # Find the last context boundary
        last_context_idx = truncated.rfind("[Context")
        if last_context_idx > 0:
            truncated = truncated[:last_context_idx]

        return truncated

    async def _load_conversation_history(self, session_id: UUID) -> list[dict]:
        """Load conversation history for a session.

        Args:
            session_id: The session ID.

        Returns:
            List of message dicts with 'role' and 'content'.
        """
        history = []

        uow = self._uow_factory()
        try:
            async with uow:
                session = await uow.chat_session_repository.get_by_id(session_id)
                if session:
                    messages = await uow.chat_message_repository.list_by_session(
                        session_id,
                        limit=self._max_history_messages,
                    )
                    # Convert to message format
                    for msg in messages:
                        history.append(
                            {
                                "role": msg.role.value,
                                "content": msg.content,
                            }
                        )
        except Exception:
            pass

        return history

    def _build_messages_with_history(
        self, system_prompt: str, user_prompt: str, history: list[dict]
    ) -> list[dict]:
        """Build messages list with conversation history.

        Args:
            system_prompt: The system prompt.
            user_prompt: The user prompt.
            history: Conversation history.

        Returns:
            List of message dicts for LLM.
        """
        messages = [{"role": "system", "content": system_prompt}]

        # Add history
        for msg in history:
            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

        # Add current question
        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        return messages

    def _build_sources(self, chunks: list[RelevantChunk]) -> list[Source]:
        """Build source list from relevant chunks.

        Args:
            chunks: List of RelevantChunk objects.

        Returns:
            List of Source objects.
        """
        sources = []
        for chunk in chunks:
            source = Source(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                similarity_score=chunk.similarity_score,
            )
            sources.append(source)
        return sources

    def _build_citations(self, chunks: list[RelevantChunk]) -> list[Citation]:
        """Build citation list from relevant chunks with deduplication.

        Deduplicates citations that refer to the same document, page, and chunk.
        Preserves retrieval ranking (highest similarity first).

        Args:
            chunks: List of RelevantChunk objects.

        Returns:
            List of deduplicated Citation objects ordered by similarity score.
        """
        citations = []
        seen = set()

        for chunk in chunks:
            # Create deduplication key: (document_id, page_number, chunk_index)
            page_number = chunk.start_page
            dedupe_key = (chunk.document_id, page_number, chunk.chunk_index)

            if dedupe_key not in seen:
                seen.add(dedupe_key)
                citation = Citation(
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    chunk_index=chunk.chunk_index,
                    page_number=page_number,
                    similarity_score=chunk.similarity_score,
                )
                citations.append(citation)

        return citations

    async def _persist_conversation(
        self,
        user_id: UUID,
        session_id: UUID | None,
        question: str,
        answer: str,
        sources: list[Source],
        document_ids: list[UUID] | None = None,
    ) -> UUID:
        """Persist conversation to database.

        Args:
            user_id: The user's ID.
            session_id: Optional session ID.
            question: The user's question.
            answer: The generated answer.
            sources: List of sources.
            document_ids: List of document IDs for the session.

        Returns:
            The session ID.
        """
        uow = self._uow_factory()
        async with uow:
            # Get or create session
            if session_id:
                session = await uow.chat_session_repository.get_by_id(session_id)
            else:
                session = None

            if not session:
                # Create new session with a title from the question
                title = question[:50] + "..." if len(question) > 50 else question
                from app.models.chat_session import ChatSession

                session = ChatSession(
                    user_id=user_id,
                    title=title,
                    document_ids=[str(did) for did in document_ids] if document_ids else None,
                )
                session = await uow.chat_session_repository.create(session)
            elif document_ids:
                # Update existing session with new document IDs if provided
                new_doc_ids = [str(did) for did in document_ids]
                if session.document_ids != new_doc_ids:
                    session.document_ids = new_doc_ids

            # Save user message
            from datetime import datetime, timedelta

            from app.models.chat_message import ChatMessage
            from app.models.enums import ChatRole

            now = datetime.now(UTC)

            user_message = ChatMessage(
                session_id=session.id,
                role=ChatRole.USER,
                content=question,
                sources=None,
                created_at=now,
            )
            await uow.chat_message_repository.create(user_message)

            # Save assistant message with sources
            sources_dict = (
                [
                    {
                        "document_id": str(s.document_id),
                        "chunk_id": str(s.chunk_id),
                        "chunk_index": s.chunk_index,
                        "start_page": s.start_page,
                        "end_page": s.end_page,
                        "similarity_score": s.similarity_score,
                    }
                    for s in sources
                ]
                if sources
                else None
            )

            assistant_message = ChatMessage(
                session_id=session.id,
                role=ChatRole.ASSISTANT,
                content=answer,
                sources=sources_dict,
                created_at=now + timedelta(milliseconds=10),
            )
            await uow.chat_message_repository.create(assistant_message)

            await uow.commit()

            return session.id
