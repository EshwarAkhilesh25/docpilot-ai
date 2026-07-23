"""Tests for conversation API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User

client = TestClient(app)

from app.api.dependencies import get_authentication_service, get_current_user
from app.api.v1.chat import get_conversation_service


@pytest.fixture
def mock_current_user():
    user = MagicMock(spec=User)
    user.id = uuid4()
    return user


@pytest.fixture
def mock_auth_service():
    return AsyncMock()


@pytest.fixture
def mock_conversation_service():
    return AsyncMock()


@pytest.fixture(autouse=True)
def override_dependencies(mock_current_user, mock_auth_service, mock_conversation_service):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_authentication_service] = lambda: mock_auth_service
    app.dependency_overrides[get_conversation_service] = lambda: mock_conversation_service
    yield
    app.dependency_overrides.clear()


class TestListConversations:
    def test_list_conversations_success(self, mock_current_user, mock_conversation_service):
        session1 = {
            "session_id": uuid4(),
            "title": "Session 1",
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "updated_at": datetime(2024, 1, 1, 11, 0, 0),
            "message_count": 0,
            "last_message_preview": "Some message preview",
        }
        mock_conversation_service.list_conversations.return_value = [session1]

        response = client.get("/api/v1/chat/conversations")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "session_id" in data[0]

    def test_list_conversations_unauthorized(self, mock_auth_service):
        mock_auth_service.verify_token.side_effect = Exception("Unauthorized")

        # To test unauthorized, we override get_current_user to fail
        async def mock_fail():
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_current_user] = mock_fail

        response = client.get("/api/v1/chat/conversations")
        assert response.status_code == 401


class TestGetConversation:
    def test_get_conversation_success(self, mock_current_user, mock_conversation_service):
        session_id = uuid4()
        session_data = {
            "session_id": session_id,
            "title": "Test Session",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": [],
            "document_ids": [],
        }
        mock_conversation_service.get_conversation.return_value = session_data

        response = client.get(f"/api/v1/chat/conversations/{session_id}")
        assert response.status_code == 200

    def test_get_conversation_not_found(self, mock_conversation_service):
        session_id = uuid4()
        mock_conversation_service.get_conversation.side_effect = Exception("Conversation not found")

        response = client.get(f"/api/v1/chat/conversations/{session_id}")
        assert response.status_code == 404

    def test_get_conversation_unauthorized(self, mock_auth_service):
        async def mock_fail():
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_current_user] = mock_fail

        response = client.get(f"/api/v1/chat/conversations/{uuid4()}")
        assert response.status_code == 401


class TestDeleteConversation:
    def test_delete_conversation_success(self, mock_conversation_service):
        session_id = uuid4()
        mock_conversation_service.delete_conversation.return_value = None

        response = client.delete(f"/api/v1/chat/conversations/{session_id}")
        assert response.status_code == 204

    def test_delete_conversation_not_found(self, mock_conversation_service):
        session_id = uuid4()
        mock_conversation_service.delete_conversation.side_effect = Exception("not found")

        response = client.delete(f"/api/v1/chat/conversations/{session_id}")
        assert response.status_code == 404

    def test_delete_conversation_unauthorized(self, mock_auth_service):
        async def mock_fail():
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_current_user] = mock_fail

        response = client.delete(f"/api/v1/chat/conversations/{uuid4()}")
        assert response.status_code == 401
