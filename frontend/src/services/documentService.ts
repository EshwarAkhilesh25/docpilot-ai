import { apiClient } from "@lib/api";

export enum ProcessingStatus {
  UPLOADED = "uploaded",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export enum ProcessingStage {
  QUEUED = "queued",
  EXTRACTING = "extracting",
  CHUNKING = "chunking",
  EMBEDDING = "embedding",
  INDEXING = "indexing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export enum FileType {
  PDF = "pdf",
  AUDIO = "audio",
  VIDEO = "video",
}

export interface DocumentSummary {
  id: string;
  original_filename: string;
  stored_filename: string;
  file_type: FileType;
  file_size: number;
  processing_status: ProcessingStatus;
  processing_job_id: string | null;
  uploaded_at: string;
  updated_at: string;
}

export interface DocumentDetails {
  id: string;
  original_filename: string;
  file_type: FileType;
  file_size: number;
  processing_status: ProcessingStatus;
  processing_stage: ProcessingStage | null;
  uploaded_at: string;
  processed_at: string | null;
  page_count: number | null;
  character_count: number | null;
  chunk_count: number | null;
}

export interface DocumentListResponse {
  items: DocumentSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DocumentListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: ProcessingStatus;
}

export interface ProcessingStatusResponse {
  status: ProcessingStatus;
  stage: ProcessingStage | null;
  progress: number;
  error?: string | null;
  ingestion_report?: unknown;
}

class DocumentService {
  /**
   * List documents with pagination, search, and filtering
   */
  async listDocuments(
    params: DocumentListParams = {},
  ): Promise<DocumentListResponse> {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.page_size)
      queryParams.append("page_size", params.page_size.toString());
    if (params.search) queryParams.append("search", params.search);
    if (params.status) queryParams.append("status", params.status);

    const response = await apiClient.get<DocumentListResponse>(
      `/documents?${queryParams.toString()}`,
    );
    return response.data;
  }

  /**
   * Get document details
   */
  async getDocument(documentId: string): Promise<DocumentDetails> {
    const response = await apiClient.get<DocumentDetails>(
      `/documents/${documentId}`,
    );
    return response.data;
  }

  /**
   * Delete document
   */
  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`);
  }

  /**
   * Download document
   * Handles Blob creation and Object URL cleanup
   */
  async downloadDocument(documentId: string): Promise<void> {
    const response = await apiClient.get(`/documents/${documentId}/download`, {
      responseType: "blob",
    });

    const blob = response.data as Blob;
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download =
      response.headers?.["content-disposition"]?.match(
        /filename="(.+)"/,
      )?.[1] || `document-${documentId}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * View document in browser
   * Opens the document in a new tab instead of downloading
   * For PDFs: opens in browser PDF viewer
   * For videos/audio: opens in browser for playback
   */
  async viewDocument(documentId: string): Promise<void> {
    const response = await apiClient.get(`/documents/${documentId}/download`, {
      responseType: "blob",
    });

    const blob = response.data as Blob;
    const url = window.URL.createObjectURL(blob);

    // Open in browser for all file types
    window.open(url, "_blank");

    // Don't revoke the URL immediately - let the browser handle it when the tab is closed
    // This prevents ERR_FILE_NOT_FOUND errors for videos/audio
  }

  /**
   * Get document summary
   */
  async getDocumentSummary(
    documentId: string,
  ): Promise<{ summary: string | null }> {
    const response = await apiClient.get<{ summary: string | null }>(
      `/documents/${documentId}/summary`,
    );
    return response.data;
  }

  /**
   * Get document processing status
   */
  async getProcessingStatus(
    documentId: string,
  ): Promise<ProcessingStatusResponse> {
    const response = await apiClient.get<ProcessingStatusResponse>(
      `/documents/${documentId}/processing-status`,
    );
    return response.data;
  }
}

export const documentService = new DocumentService();
