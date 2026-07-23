import { describe, it, expect, vi, beforeEach } from "vitest";
import { dashboardService } from "../dashboardService";

// Mock the API service
vi.mock("@services/apiService", () => ({
  apiService: {
    get: vi.fn(),
  },
}));

describe("DashboardService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("loadDashboardData", () => {
    it("should load and aggregate dashboard data", async () => {
      const mockDocuments = [
        {
          id: "1",
          stored_filename: "doc1.pdf",
          file_size: 1024,
          status: "completed",
          created_at: "2024-01-01",
        },
        {
          id: "2",
          stored_filename: "doc2.pdf",
          file_size: 2048,
          status: "processing",
          created_at: "2024-01-02",
        },
      ];

      const mockConversations = [
        {
          id: "1",
          title: "Chat 1",
          message_count: 5,
          updated_at: "2024-01-01",
        },
      ];

      const { apiService } = await import("@services/apiService");
      vi.mocked(apiService.get)
        .mockResolvedValueOnce({ data: { items: mockDocuments, total: 2 } })
        .mockResolvedValueOnce(mockConversations);

      const data = await dashboardService.loadDashboardData();

      expect(data).toBeDefined();
      expect(data.recentDocuments).toHaveLength(2);
      expect(data.recentConversations).toHaveLength(1);
      expect(data.stats).toBeDefined();
      expect(data.stats.totalDocuments).toBe(2);
      expect(data.stats.processingDocuments).toBe(1);
      expect(data.stats.completedDocuments).toBe(1);
    });

    it("should handle API errors gracefully", async () => {
      const { apiService } = await import("@services/apiService");
      vi.mocked(apiService.get).mockRejectedValue(new Error("API Error"));

      await expect(dashboardService.loadDashboardData()).rejects.toThrow();
    });
  });

  describe("loadProcessingJobs", () => {
    it("should load processing jobs", async () => {
      const mockJobs = [
        { id: "1", document_id: "doc1", status: "processing", progress: 50 },
      ];

      const { apiService } = await import("@services/apiService");
      vi.mocked(apiService.get).mockResolvedValue({ data: mockJobs });

      const jobs = await dashboardService.loadProcessingJobs();

      expect(jobs).toHaveLength(1);
      expect(jobs[0].status).toBe("processing");
    });

    it("should return empty array when no jobs", async () => {
      const { apiService } = await import("@services/apiService");
      vi.mocked(apiService.get).mockResolvedValue({ data: [] });

      const jobs = await dashboardService.loadProcessingJobs();

      expect(jobs).toHaveLength(0);
    });
  });
});
