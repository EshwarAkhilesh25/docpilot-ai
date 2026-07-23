import { apiClient } from "@lib/api";

export interface DashboardStats {
  totalDocuments: number;
  processingDocuments: number;
  completedDocuments: number;
  failedDocuments: number;
  totalConversations: number;
  storageUsed: string;
}

export interface RecentDocument {
  id: string;
  original_filename: string;
  stored_filename: string;
  file_type: string;
  processing_status: string;
  created_at: string;
  updated_at: string;
  file_size: number;
  metadata?: {
    page_count?: number;
    ocr_used?: boolean;
  };
}

export interface RecentConversation {
  session_id: string;
  title: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

export interface ProcessingJob {
  document_id: string;
  status: string;
  progress: number;
  updated_at: string;
}

export interface DashboardData {
  stats: DashboardStats;
  recentDocuments: RecentDocument[];
  recentConversations: RecentConversation[];
  processingJobs: ProcessingJob[];
}

class DashboardService {
  /**
   * Load all dashboard data in a single call
   * Composes data from existing APIs
   */
  async loadDashboardData(): Promise<DashboardData> {
    const [documentsResponse, conversationsResponse] = await Promise.all([
      apiClient
        .get<{ items: RecentDocument[] }>("/documents?page=1&page_size=100")
        .catch(() => ({ data: { items: [] as RecentDocument[] } })),
      apiClient
        .get<RecentConversation[]>("/chat/conversations")
        .catch(() => ({ data: [] as RecentConversation[] })),
    ]);

    const documents: RecentDocument[] = documentsResponse.data?.items || [];
    const conversations: RecentConversation[] =
      conversationsResponse.data || [];

    // Compose stats from documents
    const stats: DashboardStats = {
      totalDocuments: documents.length,
      processingDocuments: documents.filter(
        (d) => d.processing_status?.toLowerCase() === "processing",
      ).length,
      completedDocuments: documents.filter(
        (d) => d.processing_status?.toLowerCase() === "completed",
      ).length,
      failedDocuments: documents.filter(
        (d) => d.processing_status?.toLowerCase() === "failed",
      ).length,
      totalConversations: conversations.length,
      storageUsed: this.calculateStorageUsed(documents),
    };

    // Get recent documents (first 5)
    const recentDocuments: RecentDocument[] = documents.slice(0, 5);

    // Get recent conversations (first 5)
    const recentConversations: RecentConversation[] = conversations.slice(0, 5);

    // Get processing jobs
    const processingJobs: ProcessingJob[] = documents
      .filter((d) => d.processing_status?.toLowerCase() === "processing")
      .slice(0, 5)
      .map((d) => ({
        document_id: d.id,
        status: d.processing_status,
        progress: 0, // Backend doesn't provide progress yet
        updated_at: d.updated_at,
      }));

    return {
      stats,
      recentDocuments,
      recentConversations,
      processingJobs,
    };
  }

  /**
   * Load only processing jobs for polling
   */
  async loadProcessingJobs(): Promise<ProcessingJob[]> {
    const response = await apiClient
      .get<{ items: RecentDocument[] }>(
        "/documents?status=processing&page_size=5",
      )
      .catch(() => ({ data: { items: [] as RecentDocument[] } }));
    const documents: RecentDocument[] = response.data?.items || [];

    return documents.map((d) => ({
      document_id: d.id,
      status: d.processing_status,
      progress: 0,
      updated_at: d.updated_at,
    }));
  }

  /**
   * Calculate storage used from documents
   * TODO: Replace with backend aggregation endpoint when available
   */
  private calculateStorageUsed(documents: RecentDocument[]): string {
    const totalBytes = documents.reduce(
      (sum: number, doc: RecentDocument) => sum + (doc.file_size || 0),
      0,
    );
    if (totalBytes === 0) return "0 MB";
    const mb = totalBytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  }
}

export const dashboardService = new DashboardService();
