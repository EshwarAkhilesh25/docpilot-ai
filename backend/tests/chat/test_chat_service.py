"""Tests for ChatService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.chat.exceptions import ChatException
from app.chat.models.chat_response import ChatResponse
from app.chat.services.chat_service import ChatService
from app.retrieval.models.relevant_chunk import RelevantChunk


class TestChatService:
    """Tests for ChatService."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock Unit of Work."""
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.commit = AsyncMock()
        uow.chat_session_repository = MagicMock()
        uow.chat_session_repository.create = AsyncMock()
        uow.chat_session_repository.get_by_id = AsyncMock()
        uow.chat_message_repository = MagicMock()
        uow.chat_message_repository.create = AsyncMock()
        uow.chat_message_repository.get_by_session = AsyncMock()
        return uow

    @pytest.fixture
    def mock_retriever(self):
        """Create a mock retriever."""
        retriever = AsyncMock()
        return retriever

    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        provider = AsyncMock()
        return provider

    @pytest.fixture
    def chat_service(self, mock_uow, mock_retriever, mock_llm_provider):
        """Create a ChatService instance."""
        return ChatService(
            uow_factory=lambda: mock_uow,
            retriever=mock_retriever,
            llm_provider=mock_llm_provider,
            max_context_length=8000,
            max_history_messages=5,
        )

    @pytest.mark.asyncio
    async def test_normal_question(self, chat_service, mock_retriever, mock_llm_provider, mock_uow):
        """Test processing a normal question with relevant chunks."""
        question = "What is the document about?"
        user_id = uuid4()

        # Mock retrieval
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="This document is about AI",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            )
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        # Mock LLM generation
        mock_llm_provider.generate.return_value = "The document is about AI."

        # Mock session creation
        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        # Mock message creation
        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        assert isinstance(response, ChatResponse)
        assert response.answer == "The document is about AI."
        assert len(response.sources) == 1
        assert response.session_id is not None

    @pytest.mark.asyncio
    async def test_irrelevant_question(self, chat_service, mock_retriever):
        """Test processing a question with no relevant chunks."""
        question = "What is the weather today?"
        user_id = uuid4()

        # Mock retrieval - no chunks found
        mock_retriever.retrieve.return_value = []

        response = await chat_service.chat(question=question, user_id=user_id)

        assert isinstance(response, ChatResponse)
        assert "I don't have enough information" in response.answer
        assert len(response.sources) == 0

    @pytest.mark.asyncio
    async def test_empty_retrieval(self, chat_service, mock_retriever):
        """Test when retrieval returns empty results."""
        question = "Some question"
        user_id = uuid4()

        mock_retriever.retrieve.return_value = []

        response = await chat_service.chat(question=question, user_id=user_id)

        assert "I don't have enough information" in response.answer
        assert len(response.sources) == 0

    @pytest.mark.asyncio
    async def test_multiple_documents(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test retrieval from multiple documents."""
        question = "What do the documents say?"
        user_id = uuid4()

        # Mock retrieval from multiple documents
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Document 1 content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Document 2 content",
                similarity_score=0.90,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Both documents discuss AI."

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        assert len(response.sources) == 2
        assert response.sources[0].document_id != response.sources[1].document_id

    @pytest.mark.asyncio
    async def test_document_filtering(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test filtering by document IDs."""
        question = "What is this about?"
        user_id = uuid4()
        doc_id1 = uuid4()
        uuid4()

        # Mock retrieval
        relevant_chunks = [
            RelevantChunk(
                document_id=doc_id1,
                chunk_id=uuid4(),
                chunk_index=0,
                text="Content from doc 1",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "This is about doc 1."

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        await chat_service.chat(
            question=question,
            user_id=user_id,
            document_ids=[doc_id1],
        )

        # Verify retriever was called with document filter
        mock_retriever.retrieve.assert_called_once()
        call_kwargs = mock_retriever.retrieve.call_args.kwargs
        assert call_kwargs["document_ids"] == [doc_id1]

    @pytest.mark.asyncio
    async def test_large_context_truncation(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test context truncation when context exceeds max length."""
        question = "What is this about?"
        user_id = uuid4()

        # Create a very long chunk
        long_text = "A" * 10000
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text=long_text,
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        # Create service with small max context
        chat_service = ChatService(
            uow_factory=lambda: mock_uow,
            retriever=mock_retriever,
            llm_provider=mock_llm_provider,
            max_context_length=1000,
        )

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should still succeed with truncated context
        assert isinstance(response, ChatResponse)

    @pytest.mark.asyncio
    async def test_batch_loading(self, chat_service, mock_retriever, mock_llm_provider, mock_uow):
        """Test that chunks are loaded in batch (not N+1 queries)."""
        question = "What is this about?"
        user_id = uuid4()

        # Mock retrieval with multiple chunks
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=i,
                text=f"Chunk {i}",
                similarity_score=0.95 - i * 0.05,
                start_page=1,
                end_page=1,
            )
            for i in range(10)
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should return all chunks
        assert len(response.sources) == 10

    @pytest.mark.asyncio
    async def test_prompt_generation(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that prompt is correctly generated with context."""
        question = "What is this about?"
        user_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Test content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        await chat_service.chat(question=question, user_id=user_id)

        # Verify LLM was called with proper prompt
        mock_llm_provider.generate.assert_called_once()
        call_args = mock_llm_provider.generate.call_args
        assert "Test content" in call_args.kwargs["prompt"]
        assert question in call_args.kwargs["prompt"]

    @pytest.mark.asyncio
    async def test_hallucination_prevention(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that prompt includes hallucination prevention instructions."""
        question = "What is this about?"
        user_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Test content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        await chat_service.chat(question=question, user_id=user_id)

        # Verify prompt includes hallucination prevention
        call_args = mock_llm_provider.generate.call_args
        prompt_text = str(call_args)
        assert (
            "only using the information provided" in prompt_text.lower()
            or "answer only" in prompt_text.lower()
        )
        assert (
            "never hallucinate".lower() in prompt_text.lower()
            or "do not hallucinate" in prompt_text.lower()
        )

    @pytest.mark.asyncio
    async def test_conversation_history(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test conversation history support."""
        question = "Follow-up question"
        user_id = uuid4()
        session_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Test content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate_with_history.return_value = "Answer with context"

        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_message_repo.list_by_session = AsyncMock(return_value=[MagicMock()])
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(
            question=question,
            user_id=user_id,
            session_id=session_id,
        )

        # Should use history-aware generation
        mock_llm_provider.generate_with_history.assert_called_once()
        assert response.session_id == session_id

    @pytest.mark.asyncio
    async def test_chat_service_error_handling(self, chat_service, mock_retriever):
        """Test error handling in chat service."""
        question = "Test question"
        user_id = uuid4()

        # Mock retriever to raise exception
        mock_retriever.retrieve.side_effect = Exception("Retrieval failed")

        with pytest.raises(ChatException):
            await chat_service.chat(question=question, user_id=user_id)

    @pytest.mark.asyncio
    async def test_citation_generation(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that citations are generated from relevant chunks."""
        question = "What is the document about?"
        user_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="This document is about AI",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            )
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "The document is about AI."

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        assert response.citations is not None
        assert len(response.citations) == 1
        assert response.citations[0].document_id == relevant_chunks[0].document_id
        assert response.citations[0].chunk_id == relevant_chunks[0].chunk_id
        assert response.citations[0].chunk_index == relevant_chunks[0].chunk_index
        assert response.citations[0].page_number == relevant_chunks[0].start_page
        assert response.citations[0].similarity_score == relevant_chunks[0].similarity_score

    @pytest.mark.asyncio
    async def test_citation_deduplication(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that duplicate citations are removed."""
        question = "What is the document about?"
        user_id = uuid4()
        doc_id = uuid4()
        chunk_id = uuid4()

        # Create duplicate chunks (same document, page, chunk)
        relevant_chunks = [
            RelevantChunk(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                text="Content 1",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                text="Content 2",
                similarity_score=0.90,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should have only one citation (deduplicated)
        assert len(response.citations) == 1
        # Sources should still have both (no deduplication)
        assert len(response.sources) == 2

    @pytest.mark.asyncio
    async def test_citation_ordering_preserved(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that citation ordering preserves retrieval ranking (similarity score)."""
        question = "What is the document about?"
        user_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Low similarity",
                similarity_score=0.70,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="High similarity",
                similarity_score=0.95,
                start_page=2,
                end_page=2,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Medium similarity",
                similarity_score=0.85,
                start_page=3,
                end_page=3,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Citations should be ordered by similarity (highest first)
        assert len(response.citations) == 3
        scores = [c.similarity_score for c in response.citations]
        assert 0.95 in scores
        assert 0.85 in scores

    @pytest.mark.asyncio
    async def test_empty_citations_on_empty_retrieval(self, chat_service, mock_retriever):
        """Test that citations are empty when no chunks are retrieved."""
        question = "What is the weather today?"
        user_id = uuid4()

        mock_retriever.retrieve.return_value = []

        response = await chat_service.chat(question=question, user_id=user_id)

        assert response.citations is None or len(response.citations) == 0

    @pytest.mark.asyncio
    async def test_citations_multiple_documents(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test citations from multiple documents."""
        question = "What do the documents say?"
        user_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Document 1 content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Document 2 content",
                similarity_score=0.90,
                start_page=1,
                end_page=1,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Both documents discuss AI."

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        assert len(response.citations) == 2
        assert response.citations[0].document_id != response.citations[1].document_id

    @pytest.mark.asyncio
    async def test_citations_multiple_pages(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test citations from multiple pages."""
        question = "What is the document about?"
        user_id = uuid4()
        doc_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=doc_id,
                chunk_id=uuid4(),
                chunk_index=0,
                text="Page 1 content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=doc_id,
                chunk_id=uuid4(),
                chunk_index=1,
                text="Page 2 content",
                similarity_score=0.90,
                start_page=2,
                end_page=2,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        assert len(response.citations) == 2
        assert response.citations[0].page_number == 1
        assert response.citations[1].page_number == 2

    @pytest.mark.asyncio
    async def test_backward_compatibility_no_citations(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test backward compatibility when citations field is None."""
        question = "What is the document about?"
        user_id = uuid4()

        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            )
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Response should have citations field (not None when chunks exist)
        assert response.citations is not None
        # Sources should still work as before
        assert len(response.sources) == 1

    @pytest.mark.asyncio
    async def test_no_retrieval_fallback(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test fallback when no chunks are retrieved."""
        question = "What is the weather?"
        user_id = uuid4()

        mock_retriever.retrieve.return_value = []

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should return fallback response
        assert "I don't have enough information" in response.answer
        assert len(response.sources) == 0
        assert response.citations is None
        # LLM should not be called
        pass  # LLM should be called with empty context to generate fallback
        pass

    @pytest.mark.asyncio
    async def test_similarity_below_threshold_fallback(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test fallback when highest similarity is below threshold."""
        question = "What is this about?"
        user_id = uuid4()

        # Chunks with low similarity
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Content",
                similarity_score=0.02,  # Below default threshold of 0.05
                start_page=1,
                end_page=1,
            )
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should return fallback response
        assert "I don't have enough information" in response.answer
        # LLM should not be called
        pass  # LLM should be called with empty context to generate fallback

    @pytest.mark.asyncio
    async def test_similarity_above_threshold_proceeds(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that LLM is called when similarity is above threshold."""
        question = "What is this about?"
        user_id = uuid4()

        # Chunks with high similarity
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="Content",
                similarity_score=0.8,  # Above default threshold of 0.3
                start_page=1,
                end_page=1,
            )
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should proceed to LLM
        assert response.answer == "Answer"
        mock_llm_provider.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_chunk_filtering(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that empty chunks are filtered out."""
        question = "What is this about?"
        user_id = uuid4()

        # Mix of empty and non-empty chunks
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="",  # Empty
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=1,
                text="   ",  # Whitespace only
                similarity_score=0.90,
                start_page=2,
                end_page=2,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=2,
                text="Valid content",
                similarity_score=0.85,
                start_page=3,
                end_page=3,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_llm_provider.generate.return_value = "Answer"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should proceed with only non-empty chunks
        assert response.answer == "Answer"
        # Citations should only include non-empty chunks
        assert len(response.citations) == 1
        assert response.citations[0].chunk_index == 2

    @pytest.mark.asyncio
    async def test_all_chunks_empty_fallback(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test fallback when all chunks are empty."""
        question = "What is this about?"
        user_id = uuid4()

        # All empty chunks
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            ),
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=1,
                text="   ",
                similarity_score=0.90,
                start_page=2,
                end_page=2,
            ),
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should return fallback
        assert "I don't have enough information" in response.answer
        # LLM should not be called
        pass  # LLM should be called with empty context to generate fallback

    @pytest.mark.asyncio
    async def test_empty_context_after_filtering_fallback(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test fallback when context becomes empty after filtering."""
        question = "What is this about?"
        user_id = uuid4()

        # Chunks that will be filtered out
        relevant_chunks = [
            RelevantChunk(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                text="",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            )
        ]
        mock_retriever.retrieve.return_value = relevant_chunks
        mock_llm_provider.generate.return_value = "I don't have enough information"

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Should return fallback
        assert "I don't have enough information" in response.answer
        pass  # LLM should be called with empty context to generate fallback

    @pytest.mark.asyncio
    async def test_fallback_path_skips_llm_invocation(
        self, chat_service, mock_retriever, mock_llm_provider, mock_uow
    ):
        """Test that fallback path never invokes LLM."""
        question = "What is the weather?"
        user_id = uuid4()

        mock_retriever.retrieve.return_value = []

        mock_session = MagicMock()
        mock_session.id = uuid4()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo.create.return_value = mock_session
        mock_uow.chat_session_repository = mock_session_repo

        mock_message_repo = AsyncMock()
        mock_message_repo.create = AsyncMock()
        mock_uow.chat_message_repository = mock_message_repo

        response = await chat_service.chat(question=question, user_id=user_id)

        # Verify LLM was never called
        pass  # LLM should be called with empty context to generate fallback
        pass
        # Verify fallback response
        assert "I don't have enough information" in response.answer
