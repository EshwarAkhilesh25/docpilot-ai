import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  QueryKey,
} from "@tanstack/react-query";
import {
  documentService,
  DocumentListParams,
  ProcessingStatus,
  ProcessingStage,
  DocumentListResponse,
  DocumentDetails,
  ProcessingStatusResponse,
} from "@services/documentService";

// Query keys
export const documentKeys = {
  all: ["documents"] as const,
  lists: () => [...documentKeys.all, "list"] as const,
  list: (params: DocumentListParams) =>
    [...documentKeys.lists(), params] as const,
  details: () => [...documentKeys.all, "detail"] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
  processingStatus: (id: string) =>
    [...documentKeys.all, "processing-status", id] as const,
};

/**
 * Hook for fetching documents list with pagination, search, and filtering
 */
export function useDocuments(
  params: DocumentListParams = {},
  options?: Omit<
    UseQueryOptions<DocumentListResponse, Error>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery<DocumentListResponse, Error>({
    queryKey: documentKeys.list(params),
    queryFn: () => documentService.listDocuments(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    refetchOnWindowFocus: false,
    ...options,
  });
}

/**
 * Hook for fetching document details
 */
export function useDocument(
  id: string,
  options?: Omit<
    UseQueryOptions<DocumentDetails, Error>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery<DocumentDetails, Error>({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentService.getDocument(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    enabled: !!id,
    ...options,
  });
}

interface DeleteMutationContext {
  previousQueries: [QueryKey, DocumentListResponse | undefined][];
  deletedId: string;
}

/**
 * Hook for deleting a document with optimistic updates and rollback
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation<string, Error, string, DeleteMutationContext>({
    mutationFn: async (documentId: string) => {
      await documentService.deleteDocument(documentId);
      return documentId;
    },
    onMutate: async (deletedId: string): Promise<DeleteMutationContext> => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: documentKeys.lists() });

      // Snapshot the previous value
      const previousQueries = queryClient.getQueriesData<DocumentListResponse>({
        queryKey: documentKeys.lists(),
      });

      // Optimistically remove the document from all list queries
      queryClient.setQueriesData<DocumentListResponse>(
        { queryKey: documentKeys.lists() },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.filter((item) => item.id !== deletedId),
            total: Math.max(0, old.total - 1),
          };
        },
      );

      // Return context with the previous data for rollback
      return { previousQueries, deletedId };
    },
    onError: (
      _error: Error,
      _deletedId: string,
      context: DeleteMutationContext | undefined,
    ) => {
      // Rollback to the previous state
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, queryData]) => {
          queryClient.setQueryData(queryKey, queryData);
        });
      }
    },
    onSuccess: (deletedId: string) => {
      // Invalidate the documents list query to get fresh data
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });

      // Remove the deleted document from cache
      queryClient.removeQueries({ queryKey: documentKeys.detail(deletedId) });
      queryClient.removeQueries({
        queryKey: documentKeys.processingStatus(deletedId),
      });
    },
  });
}

/**
 * Hook for document processing status with conditional polling
 */
export function useProcessingStatus(
  id: string,
  options?: Omit<
    UseQueryOptions<ProcessingStatusResponse, Error>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery<ProcessingStatusResponse, Error>({
    queryKey: documentKeys.processingStatus(id),
    queryFn: () => documentService.getProcessingStatus(id),
    staleTime: 0, // Always fetch fresh data
    gcTime: 1 * 60 * 1000, // 1 minute
    retry: 3,
    enabled: !!id,
    ...options,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Only poll if the document is in an active processing state
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
  });
}
