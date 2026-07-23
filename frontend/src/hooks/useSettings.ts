import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  settingsService,
  User,
  UpdateProfileInput,
  ChangePasswordInput,
} from "@services/settingsService";
import { authService } from "@services/authService";
import { useAuthStore } from "@store/authStore";

// Query keys
export const settingsKeys = {
  all: ["settings"] as const,
  user: () => [...settingsKeys.all, "user"] as const,
};

/**
 * Hook for fetching current user information
 */
export function useCurrentUser(
  options?: Omit<UseQueryOptions<User, Error>, "queryKey" | "queryFn">,
) {
  return useQuery<User, Error>({
    queryKey: settingsKeys.user(),
    queryFn: () => authService.getCurrentUser(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    refetchOnWindowFocus: false,
    ...options,
  });
}

/**
 * Hook for updating user profile with optimistic updates
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (data: UpdateProfileInput) => {
      return await settingsService.updateProfile(data);
    },
    onMutate: async (newData: UpdateProfileInput) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: settingsKeys.user() });

      // Snapshot the previous value
      const previousUser = queryClient.getQueryData<User>(settingsKeys.user());

      // Optimistically update to the new value
      queryClient.setQueryData<User>(
        settingsKeys.user(),
        (old: User | undefined) => ({
          ...old!,
          full_name: newData.full_name,
        }),
      );

      // Return context with the previous data for rollback
      return { previousUser };
    },
    onError: (
      _error: unknown,
      _variables: UpdateProfileInput,
      context: { previousUser: User | undefined } | undefined,
    ) => {
      // Rollback to the previous state
      if (context?.previousUser) {
        queryClient.setQueryData(settingsKeys.user(), context.previousUser);
      }
    },
    onSuccess: (updatedUser: User) => {
      // Update auth store with fresh user data
      setUser(updatedUser);

      // Invalidate the user query to get fresh data
      queryClient.invalidateQueries({ queryKey: settingsKeys.user() });
    },
  });
}

/**
 * Hook for changing password
 */
export function useChangePassword() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ChangePasswordInput) => {
      await settingsService.changePassword(data);
    },
    onSuccess: () => {
      // Invalidate the user query to get fresh data
      queryClient.invalidateQueries({ queryKey: settingsKeys.user() });
    },
  });
}
