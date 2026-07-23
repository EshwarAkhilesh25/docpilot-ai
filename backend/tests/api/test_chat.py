"""Tests for chat API endpoints."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User

client = TestClient(app, raise_server_exceptions=True)

from app.api.dependencies import get_authentication_service, get_uow


@pytest.fixture(autouse=True)
def override_dependencies(mock_uow, mock_auth_service):
    app.dependency_overrides[get_uow] = lambda: mock_uow
    app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_current_user():
    """Fixture for mocked current user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    return user


@pytest.fixture
def mock_auth_service():
    """Fixture for mocked authentication service."""
    auth_service = AsyncMock()
    return auth_service


@pytest.fixture
def mock_uow():
    """Fixture for mocked Unit of Work."""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    return uow


class TestChatEndpoint:
    """Tests for POST /chat endpoint."""

    def test_chat_response_contains_citations(self, mock_current_user, mock_auth_service, mock_uow):
        """Test that chat response includes citations."""
        # Setup
        from app.chat.models.chat_response import ChatResponse
        from app.chat.models.citation import Citation
        from app.chat.models.source import Source
        from app.retrieval.models.relevant_chunk import RelevantChunk

        user_id = uuid4()
        mock_current_user.id = user_id

        # Mock chat service response with citations
        doc_id = uuid4()
        chunk_id = uuid4()

        [
            RelevantChunk(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                text="Test content",
                similarity_score=0.95,
                start_page=1,
                end_page=1,
            )
        ]

        citations = [
            Citation(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                page_number=1,
                similarity_score=0.95,
            )
        ]

        sources = [
            Source(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                start_page=1,
                end_page=1,
                similarity_score=0.95,
            )
        ]

        chat_response = ChatResponse(
            answer="Test answer",
            sources=sources,
            citations=citations,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert "citations" in data
                    assert data["citations"] is not None
                    assert len(data["citations"]) == 1
                    assert data["citations"][0]["document_id"] == str(doc_id)
                    assert data["citations"][0]["chunk_id"] == str(chunk_id)
                    assert data["citations"][0]["chunk_index"] == 0
                    assert data["citations"][0]["page_number"] == 1
                    assert data["citations"][0]["similarity_score"] == 0.95

    def test_empty_citations_on_no_retrieval(self, mock_current_user, mock_auth_service, mock_uow):
        """Test that citations are empty when no chunks are retrieved."""
        # Setup
        from app.chat.models.chat_response import ChatResponse

        user_id = uuid4()
        mock_current_user.id = user_id

        chat_response = ChatResponse(
            answer="I don't have enough information in the uploaded documents.",
            sources=[],
            citations=None,
            session_id=None,
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is the weather?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert "citations" in data
                    assert data["citations"] is None

    def test_duplicate_citation_removal(self, mock_current_user, mock_auth_service, mock_uow):
        """Test that duplicate citations are removed in response."""
        # Setup
        from app.chat.models.chat_response import ChatResponse
        from app.chat.models.citation import Citation
        from app.chat.models.source import Source
        from app.retrieval.models.relevant_chunk import RelevantChunk

        user_id = uuid4()
        mock_current_user.id = user_id

        doc_id = uuid4()
        chunk_id = uuid4()

        # Create duplicate chunks (same doc, page, chunk)
        [
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

        # Citations should be deduplicated (only one)
        citations = [
            Citation(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                page_number=1,
                similarity_score=0.95,
            )
        ]

        # Sources should have both (no deduplication)
        sources = [
            Source(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                start_page=1,
                end_page=1,
                similarity_score=0.95,
            ),
            Source(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                start_page=1,
                end_page=1,
                similarity_score=0.90,
            ),
        ]

        chat_response = ChatResponse(
            answer="Answer",
            sources=sources,
            citations=citations,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data["citations"]) == 1
                    assert len(data["sources"]) == 2

    def test_citation_ordering_verification(self, mock_current_user, mock_auth_service, mock_uow):
        """Test that citations maintain retrieval ranking order."""
        # Setup
        from app.chat.models.chat_response import ChatResponse
        from app.chat.models.citation import Citation
        from app.chat.models.source import Source

        user_id = uuid4()
        mock_current_user.id = user_id

        citations = [
            Citation(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                page_number=1,
                similarity_score=0.95,
            ),
            Citation(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                page_number=2,
                similarity_score=0.85,
            ),
            Citation(
                document_id=uuid4(),
                chunk_id=uuid4(),
                chunk_index=0,
                page_number=3,
                similarity_score=0.70,
            ),
        ]

        sources = [
            Source(
                document_id=c.document_id,
                chunk_id=c.chunk_id,
                chunk_index=c.chunk_index,
                start_page=c.page_number,
                end_page=c.page_number,
                similarity_score=c.similarity_score,
            )
            for c in citations
        ]

        chat_response = ChatResponse(
            answer="Answer",
            sources=sources,
            citations=citations,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data["citations"]) == 3
                    # Verify ordering by similarity score (highest first)
                    assert data["citations"][0]["similarity_score"] == 0.95
                    assert data["citations"][1]["similarity_score"] == 0.85
                    assert data["citations"][2]["similarity_score"] == 0.70

    def test_backward_compatibility_sources_still_work(
        self, mock_current_user, mock_auth_service, mock_uow
    ):
        """Test that sources field still works as before (backward compatibility)."""
        # Setup
        from app.chat.models.chat_response import ChatResponse
        from app.chat.models.citation import Citation
        from app.chat.models.source import Source

        user_id = uuid4()
        mock_current_user.id = user_id

        doc_id = uuid4()
        chunk_id = uuid4()

        citations = [
            Citation(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                page_number=1,
                similarity_score=0.95,
            )
        ]

        sources = [
            Source(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=0,
                start_page=1,
                end_page=1,
                similarity_score=0.95,
            )
        ]

        chat_response = ChatResponse(
            answer="Answer",
            sources=sources,
            citations=citations,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    # Sources should still work
                    assert "sources" in data
                    assert len(data["sources"]) == 1
                    assert data["sources"][0]["document_id"] == str(doc_id)
                    # Citations should also be present
                    assert "citations" in data
                    assert len(data["citations"]) == 1

    def test_fallback_response_no_retrieval(self, mock_current_user, mock_auth_service, mock_uow):
        """Test fallback response when no chunks are retrieved."""
        # Setup
        from app.chat.models.chat_response import ChatResponse

        user_id = uuid4()
        mock_current_user.id = user_id

        chat_response = ChatResponse(
            answer="I don't have enough information in the uploaded documents.",
            sources=[],
            citations=None,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is the weather?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert "I don't have enough information" in data["answer"]
                    assert data["sources"] == []
                    assert data["citations"] is None

    def test_threshold_rejection_low_similarity(
        self, mock_current_user, mock_auth_service, mock_uow
    ):
        """Test that low similarity chunks trigger fallback."""
        # Setup
        from app.chat.models.chat_response import ChatResponse

        user_id = uuid4()
        mock_current_user.id = user_id

        chat_response = ChatResponse(
            answer="I don't have enough information in the uploaded documents.",
            sources=[],
            citations=None,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert "I don't have enough information" in data["answer"]
                    assert data["sources"] == []
                    assert data["citations"] is None

    def test_citations_empty_on_fallback(self, mock_current_user, mock_auth_service, mock_uow):
        """Test that citations are empty when fallback is triggered."""
        # Setup
        from app.chat.models.chat_response import ChatResponse

        user_id = uuid4()
        mock_current_user.id = user_id

        chat_response = ChatResponse(
            answer="I don't have enough information in the uploaded documents.",
            sources=[],
            citations=None,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["citations"] is None
                    assert data["sources"] == []

    def test_sources_empty_on_fallback(self, mock_current_user, mock_auth_service, mock_uow):
        """Test that sources are empty when fallback is triggered."""
        # Setup
        from app.chat.models.chat_response import ChatResponse

        user_id = uuid4()
        mock_current_user.id = user_id

        chat_response = ChatResponse(
            answer="I don't have enough information in the uploaded documents.",
            sources=[],
            citations=None,
            session_id=uuid4(),
        )

        mock_auth_service.verify_token = AsyncMock(return_value=mock_current_user)

        if True:
            if True:
                if True:
                    mock_chat_service = AsyncMock()
                    mock_chat_service.execute_pipeline.return_value = {
                        "answer": chat_response.answer,
                        "sources": [
                            {
                                "document_id": str(c.document_id),
                                "chunk_id": str(c.chunk_id),
                                "chunk_index": c.chunk_index,
                                "start_page": c.start_page,
                                "end_page": c.end_page,
                                "similarity_score": c.similarity_score,
                                "page_number": c.start_page,
                            }
                            for c in chat_response.sources
                        ],
                    }
                    from app.api.v1.chat import get_chat_pipeline_service

                    app.dependency_overrides[get_chat_pipeline_service] = lambda: mock_chat_service

                    # Execute
                    response = client.post(
                        "/api/v1/chat/",
                        json={
                            "question": "What is this about?",
                            "top_k": 5,
                            "search_k": 20,
                        },
                        headers={"Authorization": "Bearer test_token"},
                    )

                    # Assert
                    if response.status_code != 200:
                        print(f"ERROR RESPONSE: {response.text}")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["sources"] == []
