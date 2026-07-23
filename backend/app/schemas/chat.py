from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ChatRole


class ChatRequest(BaseModel):
    """Request schema for sending a chat message."""

    session_id: UUID | None = Field(
        default=None,
        description="ID of the chat session. Null for new sessions.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    question: str = Field(
        min_length=1,
        max_length=10000,
        description="User's message or question",
        examples=["What is the main topic of this document?"],
    )
    document_ids: list[UUID] | None = Field(
        default=None,
        description="List of document IDs to use as context for the query",
        examples=[["550e8400-e29b-41d4-a716-446655440000"]],
    )


class ChatMessageResponse(BaseModel):
    """Response schema for a single chat message."""

    id: UUID = Field(
        description="Unique identifier of the message",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    role: ChatRole = Field(
        description="Role of the message sender",
        examples=[ChatRole.USER],
    )
    content: str = Field(
        description="Message content",
        examples=["What is the main topic?"],
    )
    sources: list[dict[str, Any]] | None = Field(
        default=None,
        description="Source documents/chunks used to generate the response",
        examples=[[{"document_id": "...", "chunk_index": 1, "text": "..."}]],
    )
    created_at: datetime = Field(
        description="Timestamp when the message was created",
        examples=["2024-01-01T00:00:00Z"],
    )


class ChatResponse(BaseModel):
    """Response schema for chat completion."""

    session_id: UUID = Field(
        description="ID of the chat session",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    message: ChatMessageResponse = Field(
        description="The assistant's response message",
    )
    is_new_session: bool = Field(
        description="Whether this is a new chat session",
        examples=[False],
    )


class StreamingChatResponse(BaseModel):
    """Response schema for streaming chat completion (SSE)."""

    session_id: UUID = Field(
        description="ID of the chat session",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    content: str = Field(
        description="Chunk of the response content",
        examples=["Hello! I can help you with..."],
    )
    done: bool = Field(
        default=False,
        description="Whether the stream is complete",
        examples=[False],
    )
    sources: list[dict[str, Any]] | None = Field(
        default=None,
        description="Source documents/chunks (sent with final chunk)",
    )


class ConversationMessage(BaseModel):
    """Schema for a message in conversation history."""

    id: UUID = Field(
        description="Unique identifier of the message",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    role: str = Field(
        description="Role of the message sender (user or assistant)",
        examples=["user"],
    )
    content: str = Field(
        description="Message content",
        examples=["What is the main topic?"],
    )
    created_at: datetime = Field(
        description="Timestamp when the message was created",
        examples=["2024-01-01T00:00:00Z"],
    )


class ConversationListItem(BaseModel):
    """Schema for a conversation in the list view."""

    session_id: UUID = Field(
        description="ID of the chat session",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    created_at: datetime = Field(
        description="Timestamp when the session was created",
        examples=["2024-01-01T00:00:00Z"],
    )
    updated_at: datetime = Field(
        description="Timestamp when the session was last updated",
        examples=["2024-01-01T01:00:00Z"],
    )
    message_count: int = Field(
        description="Number of messages in the conversation",
        examples=[5],
    )
    last_message_preview: str = Field(
        description="Preview of the last message (truncated to 100 chars)",
        examples=["What is the main topic of this document..."],
    )


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation's details."""

    title: str | None = Field(
        default=None,
        description="Updated title for the conversation",
    )
    document_ids: list[str] | None = Field(
        default=None,
        description="Updated list of document IDs attached to this conversation",
    )


class ConversationDetail(BaseModel):
    """Schema for conversation details with full message history."""

    session_id: UUID = Field(
        description="ID of the chat session",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    title: str | None = Field(
        default=None,
        description="Title of the conversation",
    )
    document_ids: list[str] | None = Field(
        default=None,
        description="List of document IDs attached to this conversation",
    )
    created_at: datetime = Field(
        description="Timestamp when the session was created",
        examples=["2024-01-01T00:00:00Z"],
    )
    updated_at: datetime = Field(
        description="Timestamp when the session was last updated",
        examples=["2024-01-01T01:00:00Z"],
    )
    messages: list[ConversationMessage] = Field(
        description="List of messages in chronological order",
    )
