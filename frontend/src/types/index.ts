// Common types
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}

export interface Document {
  id: string;
  userId: string;
  filename: string;
  fileType: "PDF" | "AUDIO" | "VIDEO";
  processingStatus: "UPLOADED" | "PROCESSING" | "COMPLETED" | "FAILED";
  storagePath: string;
  fileSize: number;
  mimeType: string;
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: string;
  sessionId: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export interface ChatSession {
  id: string;
  userId: string;
  title: string;
  documentIds: string[];
  createdAt: string;
  updatedAt: string;
}

export interface ProcessingJob {
  id: string;
  documentId: string;
  status: "UPLOADED" | "PROCESSING" | "COMPLETED" | "FAILED";
  currentStage: string;
  progress: number;
  retryCount: number;
  error?: string;
  createdAt: string;
  updatedAt: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}
