import { describe, it, expect, vi, beforeEach } from "vitest";
import { chatService } from "../chatService";

// Mock the apiClient
vi.mock("@lib/api", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

import { apiClient } from "@lib/api";

describe("ChatService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("sendMessage", () => {
    it("should send a chat message", async () => {
      const mockResponse = {
        data: {
          answer: "Test answer",
          sources: [],
          citations: [],
          session_id: "session-123",
        },
      };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const request = {
        question: "Test question",
        session_id: "session-123",
      };

      const result = await chatService.sendMessage(request);

      expect(apiClient.post).toHaveBeenCalledWith("/chat", request);
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle send message error", async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error("Network error"));

      await expect(
        chatService.sendMessage({ question: "Test" }),
      ).rejects.toThrow("Network error");
    });
  });

  describe("listConversations", () => {
    it("should list all conversations", async () => {
      const mockResponse = {
        data: [
          {
            session_id: "session-1",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T01:00:00Z",
            message_count: 5,
            last_message_preview: "Test message...",
          },
        ],
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await chatService.listConversations();

      expect(apiClient.get).toHaveBeenCalledWith("/chat/conversations");
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("getConversation", () => {
    it("should get a specific conversation", async () => {
      const mockResponse = {
        data: {
          session_id: "session-1",
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T01:00:00Z",
          messages: [
            {
              role: "user",
              content: "Test message",
              created_at: "2024-01-01T00:30:00Z",
            },
          ],
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await chatService.getConversation("session-1");

      expect(apiClient.get).toHaveBeenCalledWith(
        "/chat/conversations/session-1",
      );
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("deleteConversation", () => {
    it("should delete a conversation", async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({});

      await chatService.deleteConversation("session-1");

      expect(apiClient.delete).toHaveBeenCalledWith(
        "/chat/conversations/session-1",
      );
    });
  });

  describe("formatTimestamp", () => {
    it('should format timestamp as "Just now" for very recent', () => {
      const now = new Date();
      const timestamp = new Date(now.getTime() - 30000).toISOString(); // 30 seconds ago
      expect(chatService.formatTimestamp(timestamp)).toBe("Just now");
    });

    it("should format timestamp as minutes ago", () => {
      const now = new Date();
      const timestamp = new Date(now.getTime() - 5 * 60000).toISOString(); // 5 minutes ago
      expect(chatService.formatTimestamp(timestamp)).toBe("5m ago");
    });

    it("should format timestamp as hours ago", () => {
      const now = new Date();
      const timestamp = new Date(now.getTime() - 3 * 3600000).toISOString(); // 3 hours ago
      expect(chatService.formatTimestamp(timestamp)).toBe("3h ago");
    });

    it("should format timestamp as days ago", () => {
      const now = new Date();
      const timestamp = new Date(now.getTime() - 2 * 86400000).toISOString(); // 2 days ago
      expect(chatService.formatTimestamp(timestamp)).toBe("2d ago");
    });

    it("should format timestamp as date for older messages", () => {
      const timestamp = "2024-01-01T00:00:00Z";
      expect(chatService.formatTimestamp(timestamp)).toMatch(/Jan \d{1,2}/);
    });
  });

  describe("truncatePreview", () => {
    it("should return original text if shorter than max length", () => {
      const text = "Short text";
      expect(chatService.truncatePreview(text, 50)).toBe("Short text");
    });

    it("should truncate text longer than max length", () => {
      const text = "This is a very long text that should be truncated";
      expect(chatService.truncatePreview(text, 20)).toBe(
        "This is a very lo...",
      );
    });

    it("should use default max length of 50", () => {
      const text = "x".repeat(60);
      const result = chatService.truncatePreview(text);
      expect(result.length).toBe(53); // 50 + '...'
    });
  });
});
