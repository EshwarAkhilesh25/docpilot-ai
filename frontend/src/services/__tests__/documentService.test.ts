import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  documentService,
  ProcessingStatus,
  FileType,
} from "../documentService";

// Mock the apiClient
vi.mock("@lib/api", () => ({
  apiClient: {
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

import { apiClient } from "@lib/api";

describe("DocumentService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("listDocuments", () => {
    it("should fetch documents with default parameters", async () => {
      const mockResponse = {
        data: {
          items: [
            {
              id: "1",
              original_filename: "test.pdf",
              file_type: FileType.PDF,
              processing_status: ProcessingStatus.COMPLETED,
              uploaded_at: "2024-01-01T00:00:00Z",
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await documentService.listDocuments();

      expect(apiClient.get).toHaveBeenCalledWith(
        "/documents?page=1&page_size=20",
      );
      expect(result).toEqual(mockResponse.data);
    });

    it("should fetch documents with search and filter parameters", async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0,
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await documentService.listDocuments({
        page: 2,
        page_size: 10,
        search: "test",
        status: ProcessingStatus.PROCESSING,
      });

      expect(apiClient.get).toHaveBeenCalledWith(
        "/documents?page=2&page_size=10&search=test&status=processing",
      );
    });
  });

  describe("getDocument", () => {
    it("should fetch a single document", async () => {
      const mockResponse = {
        data: {
          id: "1",
          original_filename: "test.pdf",
          file_type: FileType.PDF,
          file_size: 1000,
          processing_status: ProcessingStatus.COMPLETED,
          processing_stage: null,
          uploaded_at: "2024-01-01T00:00:00Z",
          processed_at: "2024-01-01T00:05:00Z",
          page_count: 10,
          character_count: 5000,
          chunk_count: 25,
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await documentService.getDocument("1");

      expect(apiClient.get).toHaveBeenCalledWith("/documents/1");
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("deleteDocument", () => {
    it("should delete a document", async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({});

      await documentService.deleteDocument("1");

      expect(apiClient.delete).toHaveBeenCalledWith("/documents/1");
    });
  });

  describe("downloadDocument", () => {
    it("should download a document", async () => {
      const mockBlob = new Blob(["test content"]);
      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockBlob,
        headers: { "content-disposition": 'attachment; filename="test.pdf"' },
      });

      // Mock browser APIs
      const mockCreateObjectURL = vi
        .spyOn(window.URL, "createObjectURL")
        .mockReturnValue("blob:url");
      const mockRevokeObjectURL = vi.spyOn(window.URL, "revokeObjectURL");
      const mockCreateElement = vi
        .spyOn(document, "createElement")
        .mockReturnValue({
          href: "",
          download: "",
          click: vi.fn(),
        } as unknown as HTMLAnchorElement);
      const mockAppendChild = vi.spyOn(document.body, "appendChild");
      const mockRemoveChild = vi.spyOn(document.body, "removeChild");

      await documentService.downloadDocument("1");

      expect(apiClient.get).toHaveBeenCalledWith("/documents/1/download", {
        responseType: "blob",
      });
      expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(mockRevokeObjectURL).toHaveBeenCalledWith("blob:url");

      mockCreateObjectURL.mockRestore();
      mockRevokeObjectURL.mockRestore();
      mockCreateElement.mockRestore();
      mockAppendChild.mockRestore();
      mockRemoveChild.mockRestore();
    });
  });

  describe("getDocumentSummary", () => {
    it("should fetch document summary", async () => {
      const mockResponse = {
        data: {
          summary: "This is a test summary",
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await documentService.getDocumentSummary("1");

      expect(apiClient.get).toHaveBeenCalledWith("/documents/1/summary");
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("getProcessingStatus", () => {
    it("should fetch processing status", async () => {
      const mockResponse = {
        data: {
          status: ProcessingStatus.PROCESSING,
          stage: "chunking",
          progress: 50,
          error: null,
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await documentService.getProcessingStatus("1");

      expect(apiClient.get).toHaveBeenCalledWith(
        "/documents/1/processing-status",
      );
      expect(result).toEqual(mockResponse.data);
    });
  });
});
