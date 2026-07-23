import { describe, it, expect, vi, beforeEach } from "vitest";
import { authService } from "../authService";
import { apiClient } from "@lib/api";

vi.mock("@lib/api", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe("AuthService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("login", () => {
    it("should call apiClient.post with correct endpoint and data", async () => {
      const mockResponse = {
        data: {
          user: {
            id: "1",
            name: "Test User",
            email: "test@example.com",
            createdAt: "2024-01-01",
          },
          accessToken: "mock-token",
        },
      };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const loginData = { email: "test@example.com", password: "password123" };
      const result = await authService.login(loginData);

      expect(apiClient.post).toHaveBeenCalledWith("/auth/login", loginData);
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle login errors", async () => {
      const mockError = new Error("Login failed");
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      const loginData = { email: "test@example.com", password: "password123" };

      await expect(authService.login(loginData)).rejects.toThrow(
        "Login failed",
      );
    });
  });

  describe("register", () => {
    it("should call apiClient.post with correct endpoint and data", async () => {
      const mockResponse = {
        data: {
          user: {
            id: "1",
            name: "Test User",
            email: "test@example.com",
            createdAt: "2024-01-01",
          },
          accessToken: "mock-token",
        },
      };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const registerData = {
        name: "Test User",
        email: "test@example.com",
        password: "Password123",
        confirmPassword: "Password123",
      };
      const result = await authService.register(registerData);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/auth/register",
        registerData,
      );
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle registration errors", async () => {
      const mockError = new Error("Registration failed");
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      const registerData = {
        name: "Test User",
        email: "test@example.com",
        password: "Password123",
        confirmPassword: "Password123",
      };

      await expect(authService.register(registerData)).rejects.toThrow(
        "Registration failed",
      );
    });
  });

  describe("logout", () => {
    it("should call apiClient.post with correct endpoint", async () => {
      vi.mocked(apiClient.post).mockResolvedValue({});

      await authService.logout();

      expect(apiClient.post).toHaveBeenCalledWith("/auth/logout");
    });

    it("should handle logout errors", async () => {
      const mockError = new Error("Logout failed");
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      await expect(authService.logout()).rejects.toThrow("Logout failed");
    });
  });

  describe("refreshToken", () => {
    it("should call apiClient.post with correct endpoint and data", async () => {
      const mockResponse = {
        data: {
          user: {
            id: "1",
            name: "Test User",
            email: "test@example.com",
            createdAt: "2024-01-01",
          },
          accessToken: "new-token",
        },
      };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const refreshToken = "refresh-token";
      const result = await authService.refreshToken(refreshToken);

      expect(apiClient.post).toHaveBeenCalledWith("/auth/refresh", {
        refreshToken,
      });
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle refresh token errors", async () => {
      const mockError = new Error("Refresh failed");
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      await expect(authService.refreshToken("refresh-token")).rejects.toThrow(
        "Refresh failed",
      );
    });
  });

  describe("getCurrentUser", () => {
    it("should call apiClient.get with correct endpoint", async () => {
      const mockResponse = {
        data: {
          id: "1",
          name: "Test User",
          email: "test@example.com",
          createdAt: "2024-01-01",
        },
      };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await authService.getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith("/auth/me");
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle get current user errors", async () => {
      const mockError = new Error("Get user failed");
      vi.mocked(apiClient.get).mockRejectedValue(mockError);

      await expect(authService.getCurrentUser()).rejects.toThrow(
        "Get user failed",
      );
    });
  });
});
