import { apiClient } from "@lib/api";

// Message roles
export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
}

// Message status for optimistic updates
export enum MessageStatus {
  SENDING = "sending",
  SENT = "sent",
  FAILED = "failed",
}

// Conversation message interface
export interface ConversationMessage {
  id: string; // Backend message ID (required)
  role: string;
  content: string;
  created_at: string;
  status?: MessageStatus; // For optimistic messages
}

// Conversation list item interface
export interface ConversationListItem {
  session_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string;
}

// Conversation detail interface
export interface ConversationDetail {
  session_id: string;
  title?: string;
  document_ids?: string[];
  created_at: string;
  updated_at: string;
  messages: ConversationMessage[];
}

// Chat request interface
export interface ChatRequest {
  question: string;
  session_id?: string;
  document_ids?: string[];
  intent?: string;
  workflow_params?: Record<string, unknown>;
  top_k?: number;
  search_k?: number;
}

// Citation interface
export interface Citation {
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  page_number?: number;
  similarity_score: number;
}

// Chat response interface
export interface ChatResponse {
  answer: string;
  sources: Array<{
    document_id: string;
    chunk_id: string;
    chunk_index: number;
    start_page?: number;
    end_page?: number;
    similarity_score: number;
  }>;
  citations?: Citation[];
  session_id: string;
}

class ChatService {
  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>("/chat/", request);
    return response.data;
  }

  /**
   * List all conversations for the current user
   */
  async listConversations(): Promise<ConversationListItem[]> {
    const response = await apiClient.get<ConversationListItem[]>(
      "/chat/conversations",
    );
    return response.data;
  }

  /**
   * Get a specific conversation with message history
   */
  async getConversation(sessionId: string): Promise<ConversationDetail> {
    const response = await apiClient.get<ConversationDetail>(
      `/chat/conversations/${sessionId}`,
    );
    return response.data;
  }

  /**
   * Update a conversation's details
   */
  async updateConversation(
    sessionId: string,
    data: { title?: string; document_ids?: string[] },
  ): Promise<ConversationDetail> {
    const response = await apiClient.patch<ConversationDetail>(
      `/chat/conversations/${sessionId}`,
      data,
    );
    return response.data;
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(sessionId: string): Promise<void> {
    await apiClient.delete<void>(`/chat/conversations/${sessionId}`);
  }
}

export const chatService = new ChatService();
