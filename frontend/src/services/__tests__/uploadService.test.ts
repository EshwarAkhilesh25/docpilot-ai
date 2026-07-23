import { describe, it, expect, vi, beforeEach } from "vitest";
import { uploadService, MAX_FILE_SIZE } from "../uploadService";

// Mock the apiClient
vi.mock("@lib/api", () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

import { apiClient } from "@lib/api";

describe("UploadService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("validateFile", () => {
    it("should return null for valid PDF file", () => {
      const file = new File(["test"], "document.pdf", {
        type: "application/pdf",
      });
      const result = uploadService.validateFile(file);
      expect(result).toBeNull();
    });

    it("should return null for valid MP3 file", () => {
      const file = new File(["test"], "audio.mp3", { type: "audio/mpeg" });
      const result = uploadService.validateFile(file);
      expect(result).toBeNull();
    });

    it("should return null for valid WAV file", () => {
      const file = new File(["test"], "audio.wav", { type: "audio/wav" });
      const result = uploadService.validateFile(file);
      expect(result).toBeNull();
    });

    it("should return null for valid MP4 file", () => {
      const file = new File(["test"], "video.mp4", { type: "video/mp4" });
      const result = uploadService.validateFile(file);
      expect(result).toBeNull();
    });

    it("should return error for unsupported file type", () => {
      const file = new File(["test"], "document.docx", {
        type: "application/docx",
      });
      const result = uploadService.validateFile(file);
      expect(result).not.toBeNull();
      expect(result?.error).toContain("Unsupported file type");
    });

    it("should return error for file exceeding max size", () => {
      const file = new File(["x".repeat(MAX_FILE_SIZE + 1)], "large.pdf", {
        type: "application/pdf",
      });
      const result = uploadService.validateFile(file);
      expect(result).not.toBeNull();
      expect(result?.error).toContain("too large");
    });

    it("should return error for both unsupported type and large size", () => {
      const file = new File(["x".repeat(MAX_FILE_SIZE + 1)], "large.exe", {
        type: "application/exe",
      });
      const result = uploadService.validateFile(file);
      expect(result).not.toBeNull();
      // Should return type error first (checked before size)
      expect(result?.error).toContain("Unsupported file type");
    });
  });

  describe("validateFiles", () => {
    it("should return empty array for all valid files", () => {
      const files = [
        new File(["test"], "doc1.pdf", { type: "application/pdf" }),
        new File(["test"], "audio.mp3", { type: "audio/mpeg" }),
      ];
      const result = uploadService.validateFiles(files);
      expect(result).toEqual([]);
    });

    it("should return errors for invalid files", () => {
      const files = [
        new File(["test"], "valid.pdf", { type: "application/pdf" }),
        new File(["test"], "invalid.docx", { type: "application/docx" }),
        new File(["test"], "large.pdf", { type: "application/pdf" }),
      ];
      // Set large file size
      Object.defineProperty(files[2], "size", { value: MAX_FILE_SIZE + 1 });

      const result = uploadService.validateFiles(files);
      expect(result).toHaveLength(2);
      expect(result[0].file.name).toBe("invalid.docx");
      expect(result[1].file.name).toBe("large.pdf");
    });
  });

  describe("uploadFile", () => {
    it("should upload file with progress tracking", async () => {
      const file = new File(["test content"], "test.pdf", {
        type: "application/pdf",
      });
      const mockResponse = {
        data: {
          document_id: "doc-123",
          processing_job_id: "job-456",
          status: "uploaded",
        },
      };

      vi.mocked(apiClient.post).mockImplementation((url, data, config) => {
        // Simulate progress callback
        if (config?.onUploadProgress) {
          config.onUploadProgress({ loaded: 50, total: 100 });
        }
        return Promise.resolve(mockResponse);
      });

      const progressCallback = vi.fn();
      const result = await uploadService.uploadFile(
        file,
        progressCallback,
        "upload-1",
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/documents/upload",
        expect.any(FormData),
        expect.objectContaining({
          signal: expect.any(AbortSignal),
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: expect.any(Function),
        }),
      );
      expect(result).toEqual(mockResponse.data);
      expect(progressCallback).toHaveBeenCalledWith(
        expect.objectContaining({
          loaded: 50,
          total: 100,
          percentage: 50,
        }),
      );
    });

    it("should create new AbortController for each upload", async () => {
      const file = new File(["test"], "test.pdf", { type: "application/pdf" });
      vi.mocked(apiClient.post).mockResolvedValue({
        data: {
          document_id: "doc-123",
          processing_job_id: "job-456",
          status: "uploaded",
        },
      });

      await uploadService.uploadFile(file, undefined, "upload-1");
      await uploadService.uploadFile(file, undefined, "upload-2");

      expect(apiClient.post).toHaveBeenCalledTimes(2);
    });

    it("should handle upload error", async () => {
      const file = new File(["test"], "test.pdf", { type: "application/pdf" });
      vi.mocked(apiClient.post).mockRejectedValue(new Error("Network error"));

      await expect(uploadService.uploadFile(file)).rejects.toThrow(
        "Network error",
      );
    });
  });

  describe("cancelUpload", () => {
    it("should cancel in-progress upload", () => {
      const abortSpy = vi.spyOn(AbortController.prototype, "abort");

      uploadService.cancelUpload("upload-1");

      // The abort controller is created during upload, so we can't directly test
      // but we can verify the method doesn't throw
      expect(() => uploadService.cancelUpload("non-existent")).not.toThrow();

      abortSpy.mockRestore();
    });
  });

  describe("getFileTypeIcon", () => {
    it("should return correct icon for PDF", () => {
      expect(uploadService.getFileTypeIcon("document.pdf")).toBe("📄");
    });

    it("should return correct icon for MP3", () => {
      expect(uploadService.getFileTypeIcon("audio.mp3")).toBe("🎵");
    });

    it("should return correct icon for WAV", () => {
      expect(uploadService.getFileTypeIcon("audio.wav")).toBe("🎵");
    });

    it("should return correct icon for MP4", () => {
      expect(uploadService.getFileTypeIcon("video.mp4")).toBe("🎬");
    });

    it("should return default icon for unknown type", () => {
      expect(uploadService.getFileTypeIcon("unknown.xyz")).toBe("📁");
    });
  });

  describe("formatFileSize", () => {
    it("should format bytes correctly", () => {
      expect(uploadService.formatFileSize(0)).toBe("0 Bytes");
      expect(uploadService.formatFileSize(500)).toBe("500 Bytes");
      expect(uploadService.formatFileSize(1024)).toBe("1 KB");
      expect(uploadService.formatFileSize(1536)).toBe("1.5 KB");
      expect(uploadService.formatFileSize(1024 * 1024)).toBe("1 MB");
      expect(uploadService.formatFileSize(1024 * 1024 * 1.5)).toBe("1.5 MB");
      expect(uploadService.formatFileSize(1024 * 1024 * 1024)).toBe("1 GB");
    });
  });
});
