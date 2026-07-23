import { apiClient } from "@lib/api";
import type { AxiosProgressEvent } from "axios";

import { ProcessingStage } from "@services/documentService";

import { UPLOAD_CONFIG } from "@lib/constants";

// Use centralized configuration

export const ALLOWED_EXTENSIONS = UPLOAD_CONFIG.ALLOWED_EXTENSIONS;

export const MAX_FILE_SIZE = UPLOAD_CONFIG.MAX_FILE_SIZE;

export type AllowedExtension = (typeof ALLOWED_EXTENSIONS)[number];

export enum UploadStatus {
  QUEUED = "queued",

  UPLOADING = "uploading",

  UPLOADED = "uploaded",

  PROCESSING = "processing",

  COMPLETED = "completed",

  FAILED = "failed",

  CANCELLED = "cancelled",
}

export interface UploadProgress {
  loaded: number;

  total: number;

  percentage: number;

  speed?: number; // bytes per second
}

export interface UploadFile {
  id: string;

  file: File;

  status: UploadStatus;

  progress: UploadProgress;

  error?: string;

  documentId?: string;

  processingJobId?: string | null;

  processingStage?: ProcessingStage | null;

  processingProgress?: number;

  ingestionReport?: unknown;
}

export interface UploadResponse {
  document_id: string;

  processing_job_id: string;

  status: string;
}

export interface ValidationError {
  file: File;

  error: string;
}

class UploadService {
  private abortControllers: Map<string, AbortController> = new Map();

  /**

   * Validate file before upload

   */

  validateFile(file: File): ValidationError | null {
    // Check file extension

    const ext = "." + file.name.split(".").pop()?.toLowerCase() || "";

    if (!ALLOWED_EXTENSIONS.includes(ext as AllowedExtension)) {
      return {
        file,

        error: `Unsupported file type. Allowed types: ${ALLOWED_EXTENSIONS.join(", ")}`,
      };
    }

    // Check file size

    if (file.size > MAX_FILE_SIZE) {
      return {
        file,

        error: `File too large. Maximum size: ${MAX_FILE_SIZE / (1024 * 1024)} MB`,
      };
    }

    return null;
  }

  /**

   * Validate multiple files

   */

  validateFiles(files: File[]): ValidationError[] {
    const errors: ValidationError[] = [];

    for (const file of files) {
      const error = this.validateFile(file);

      if (error) {
        errors.push(error);
      }
    }

    return errors;
  }

  /**

   * Upload a file with progress tracking

   */

  async uploadFile(
    file: File,

    onProgress?: (progress: UploadProgress) => void,

    uploadId?: string,
  ): Promise<UploadResponse> {
    // Always create a new AbortController for each upload attempt

    const controller = new AbortController();

    if (uploadId) {
      this.abortControllers.set(uploadId, controller);
    }

    const formData = new FormData();

    formData.append("file", file);

    let startTime = Date.now();

    let lastLoaded = 0;

    try {
      const response = await apiClient.post<UploadResponse>(
        "/documents/upload",
        formData,
        {
          signal: controller.signal,

          headers: {},

          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            if (progressEvent.total) {
              const loaded = progressEvent.loaded;

              const total = progressEvent.total;

              const percentage = Math.round((loaded / total) * 100);

              // Calculate speed (bytes per second)

              const elapsed = (Date.now() - startTime) / 1000;

              const speed =
                elapsed > 0
                  ? Math.round((loaded - lastLoaded) / elapsed)
                  : undefined;

              lastLoaded = loaded;

              startTime = Date.now();

              onProgress?.({
                loaded,

                total,

                percentage,

                speed,
              });
            }
          },
        },
      );

      return response.data;
    } catch (error: unknown) {
      void 0;

      throw error;
    } finally {
      if (uploadId) {
        this.abortControllers.delete(uploadId);
      }
    }
  }

  /**

   * Cancel an in-progress upload

   */

  cancelUpload(uploadId: string): void {
    const controller = this.abortControllers.get(uploadId);

    if (controller) {
      controller.abort();

      this.abortControllers.delete(uploadId);
    }
  }

  /**

   * Get file type icon based on extension

   */

  getFileTypeIcon(filename: string): string {
    const ext = "." + filename.split(".").pop()?.toLowerCase() || "";

    switch (ext) {
      case ".pdf":
        return "📄";
      case ".docx":
        return "📄";
      case ".mp3":
        return "🎵";
      case ".wav":
        return "🎵";
      case ".mp4":
        return "🎬";

      default:
        return "đź“";
    }
  }

  /**

   * Format file size for display

   */

  formatFileSize(bytes: number): string {
    if (bytes === 0) return "0 Bytes";

    const k = 1024;

    const sizes = ["Bytes", "KB", "MB", "GB"];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  }
}

export const uploadService = new UploadService();
