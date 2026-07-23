import { apiClient } from "@lib/api";
import { LoginInput, RegisterInput } from "@lib/validations/auth";

export interface User {
  id: string;
  full_name: string;
  email: string;
  created_at: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterResponse {
  id: string;
  full_name: string;
  email: string;
  created_at: string;
  message: string;
}

class AuthService {
  private readonly endpoints = {
    login: "/auth/login",
    register: "/auth/register",
    logout: "/auth/logout",
    refresh: "/auth/refresh",
    currentUser: "/auth/me",
  };

  async login(data: LoginInput): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>(
      this.endpoints.login,
      data,
    );
    return response.data;
  }

  async register(data: RegisterInput): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>(
      this.endpoints.register,
      data,
    );
    return response.data;
  }

  async logout(): Promise<void> {
    await apiClient.post(this.endpoints.logout);
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>(
      this.endpoints.refresh,
      { refresh_token: refreshToken },
    );
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>(this.endpoints.currentUser);
    return response.data;
  }
}

export const authService = new AuthService();
