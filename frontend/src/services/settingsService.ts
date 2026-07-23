import { apiClient } from "@lib/api";
import type { User } from "@services/authService";

export interface UpdateProfileInput {
  full_name: string;
}

export interface ChangePasswordInput {
  current_password: string;
  new_password: string;
}

class SettingsService {
  private readonly endpoints = {
    updateProfile: "/auth/me",
    changePassword: "/auth/change-password",
  };

  async updateProfile(data: UpdateProfileInput): Promise<User> {
    const response = await apiClient.put<User>(
      this.endpoints.updateProfile,
      data,
    );
    return response.data;
  }

  async changePassword(data: ChangePasswordInput): Promise<void> {
    await apiClient.post(this.endpoints.changePassword, data);
  }
}

export const settingsService = new SettingsService();

// Re-export User type from authService for convenience
export type { User };
