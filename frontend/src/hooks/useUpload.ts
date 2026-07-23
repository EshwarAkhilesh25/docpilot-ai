import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { uploadService, UploadProgress } from "@services/uploadService";
import {
  documentService,
  ProcessingStatus,
  ProcessingStage,
  ProcessingStatusResponse,
} from "@services/documentService";

// Query keys
export const uploadKeys = {
  all: ["uploads"] as const,
  processingStatus: (documentId: string) =>
    [...uploadKeys.all, "processing-status", documentId] as const,
};

/**
 * Hook for uploading a file with progress tracking
 */
export function useUploadFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      file,
      uploadId,
      onProgress,
    }: {
      file: File;
      uploadId: string;
      onProgress?: (progress: UploadProgress) => void;
    }) => {
      return await uploadService.uploadFile(file, onProgress, uploadId);
    },
    onSuccess: () => {
      // Invalidate only necessary queries
      queryClient.invalidateQueries({ queryKey: ["documents", "list"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "data"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "processing"] });
    },
  });
}

/**
 * Hook for processing status polling after upload
 */
export function useUploadProcessingStatus(
  documentId: string,
  shouldPoll = false,
) {
  return useQuery<ProcessingStatusResponse, Error>({
    queryKey: uploadKeys.processingStatus(documentId),
    queryFn: () => documentService.getProcessingStatus(documentId),
    enabled: !!documentId && shouldPoll,
    refetchInterval: (query) => {
      // Only poll if the document is in an active processing state
      if (!shouldPoll) return false;
      const data = query.state.data;
      if (!data) return false;

      // Active statuses: UPLOADED, PROCESSING
      const isActiveStatus =
        data.status === ProcessingStatus.UPLOADED ||
        data.status === ProcessingStatus.PROCESSING;

      // Active stages: QUEUED, EXTRACTING, CHUNKING, EMBEDDING, INDEXING
      const isActiveStage =
        data.stage &&
        [
          ProcessingStage.QUEUED,
          ProcessingStage.EXTRACTING,
          ProcessingStage.CHUNKING,
          ProcessingStage.EMBEDDING,
          ProcessingStage.INDEXING,
        ].includes(data.stage);

      return isActiveStatus || isActiveStage ? 3000 : false; // Poll every 3 seconds while actively processing
    },
    staleTime: 0,
    gcTime: 2 * 60 * 1000,
  });
}

/**
 * Hook for cancelling an upload
 */
export function useCancelUpload() {
  return {
    cancel: (uploadId: string) => {
      uploadService.cancelUpload(uploadId);
    },
  };
}
