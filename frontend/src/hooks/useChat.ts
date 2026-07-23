import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  chatService,
  ChatRequest,
  ConversationListItem,
} from "@services/chatService";

// Query keys
export const chatKeys = {
  all: ["chat"] as const,
  conversations: () => [...chatKeys.all, "conversations"] as const,
  conversation: (id: string) => [...chatKeys.all, "conversations", id] as const,
};

/**
 * Hook for sending a chat message
 */
export function useChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: ChatRequest) => {
      return await chatService.sendMessage(request);
    },
    onSuccess: (data) => {
      // Invalidate conversations list to show updated preview
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() });
      // Invalidate the active conversation details so it refetches
      if (data?.session_id) {
        queryClient.invalidateQueries({
          queryKey: chatKeys.conversation(data.session_id),
        });
      }
    },
  });
}

/**
 * Hook for listing all conversations
 */
export function useConversations() {
  return useQuery({
    queryKey: chatKeys.conversations(),
    queryFn: () => chatService.listConversations(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook for getting a specific conversation
 */
export function useConversation(sessionId: string, enabled = true) {
  return useQuery({
    queryKey: chatKeys.conversation(sessionId),
    queryFn: () => chatService.getConversation(sessionId),
    enabled: !!sessionId && enabled,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook for deleting a conversation with optimistic update
 */
export function useDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (sessionId: string) => {
      await chatService.deleteConversation(sessionId);
    },
    onMutate: async (sessionId: string) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: chatKeys.conversations() });

      // Snapshot previous value
      const previousConversations = queryClient.getQueryData<
        ConversationListItem[]
      >(chatKeys.conversations());

      // Optimistically remove conversation
      queryClient.setQueryData<ConversationListItem[]>(
        chatKeys.conversations(),
        (old: ConversationListItem[] | undefined) =>
          old?.filter(
            (conv: ConversationListItem) => conv.session_id !== sessionId,
          ) ?? [],
      );

      // Return context for rollback
      return { previousConversations };
    },
    onError: (
      _err: unknown,
      _sessionId: string,
      context: { previousConversations?: ConversationListItem[] } | undefined,
    ) => {
      // Rollback on error
      if (context?.previousConversations) {
        queryClient.setQueryData(
          chatKeys.conversations(),
          context.previousConversations,
        );
      }
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() });
    },
  });
}

/**
 * Hook for updating a conversation's details
 */
export function useUpdateConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sessionId,
      data,
    }: {
      sessionId: string;
      data: { title?: string; document_ids?: string[] };
    }) => {
      return await chatService.updateConversation(sessionId, data);
    },
    onSuccess: (data) => {
      // Invalidate both lists and the specific conversation
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() });
      if (data?.session_id) {
        queryClient.invalidateQueries({
          queryKey: chatKeys.conversation(data.session_id),
        });
      }
    },
  });
}
