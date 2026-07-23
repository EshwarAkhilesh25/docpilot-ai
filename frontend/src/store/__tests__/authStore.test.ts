import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "../authStore";

describe("authStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.getState().clear();
  });

  describe("initial state", () => {
    it("should have initial state with no user and not authenticated", () => {
      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
    });
  });

  describe("login", () => {
    it("should set user, token, and authenticated to true", () => {
      const mockUser = {
        id: "1",
        name: "Test User",
        email: "test@example.com",
        createdAt: "2024-01-01",
      };
      const mockToken = "mock-token";

      useAuthStore.getState().login(mockUser, mockToken);

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.user).toEqual(mockUser);
      expect(state.token).toBe(mockToken);
    });
  });

  describe("logout", () => {
    it("should clear user, token, and set authenticated to false", () => {
      const mockUser = {
        id: "1",
        name: "Test User",
        email: "test@example.com",
        createdAt: "2024-01-01",
      };
      const mockToken = "mock-token";

      useAuthStore.getState().login(mockUser, mockToken);
      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
    });
  });

  describe("setUser", () => {
    it("should set user and update authenticated status", () => {
      const mockUser = {
        id: "1",
        name: "Test User",
        email: "test@example.com",
        createdAt: "2024-01-01",
      };

      useAuthStore.getState().setUser(mockUser);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
    });

    it("should clear user and set authenticated to false when null is passed", () => {
      const mockUser = {
        id: "1",
        name: "Test User",
        email: "test@example.com",
        createdAt: "2024-01-01",
      };
      useAuthStore.getState().setUser(mockUser);

      useAuthStore.getState().setUser(null);

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("setToken", () => {
    it("should set token and update authenticated status", () => {
      const mockToken = "mock-token";

      useAuthStore.getState().setToken(mockToken);

      const state = useAuthStore.getState();
      expect(state.token).toBe(mockToken);
      expect(state.isAuthenticated).toBe(true);
    });

    it("should clear token and set authenticated to false when null is passed", () => {
      const mockToken = "mock-token";
      useAuthStore.getState().setToken(mockToken);

      useAuthStore.getState().setToken(null);

      const state = useAuthStore.getState();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("clear", () => {
    it("should clear all state", () => {
      const mockUser = {
        id: "1",
        name: "Test User",
        email: "test@example.com",
        createdAt: "2024-01-01",
      };
      const mockToken = "mock-token";

      useAuthStore.getState().login(mockUser, mockToken);
      useAuthStore.getState().clear();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
    });
  });
});
