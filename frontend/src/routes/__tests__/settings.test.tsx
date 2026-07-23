import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import Settings from "../settings";

// Mock the hooks
vi.mock("@hooks/useSettings", () => ({
  useCurrentUser: () => ({
    data: {
      id: "1",
      full_name: "Test User",
      email: "test@example.com",
      created_at: "2024-01-01T00:00:00Z",
      is_active: true,
    },
    isLoading: false,
    error: null,
  }),
}));

vi.mock("@store/authStore", () => ({
  useAuthStore: () => ({
    logout: vi.fn(),
  }),
}));

vi.mock("@store/uiStore", () => ({
  useUIStore: () => ({
    sidebarOpen: true,
  }),
}));

describe("Settings Page", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{component}</BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("should render settings page with all sections", () => {
    renderWithProviders(<Settings />);

    expect(screen.getByText(/settings/i)).toBeInTheDocument();
    expect(screen.getByText(/profile/i)).toBeInTheDocument();
    expect(screen.getByText(/appearance/i)).toBeInTheDocument();
    expect(screen.getByText(/change password/i)).toBeInTheDocument();
    expect(screen.getByText(/account/i)).toBeInTheDocument();
  });

  it("should display user profile information", () => {
    renderWithProviders(<Settings />);

    expect(screen.getByText(/test user/i)).toBeInTheDocument();
    expect(screen.getByText(/test@example.com/i)).toBeInTheDocument();
  });

  it("should show edit profile button initially", () => {
    renderWithProviders(<Settings />);

    expect(
      screen.getByRole("button", { name: /edit profile/i }),
    ).toBeInTheDocument();
  });

  it("should switch to edit profile form when edit button is clicked", () => {
    renderWithProviders(<Settings />);

    const editButton = screen.getByRole("button", { name: /edit profile/i });
    fireEvent.click(editButton);

    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /save changes/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("should render change password form", () => {
    renderWithProviders(<Settings />);

    expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
  });

  it("should render appearance settings with theme options", () => {
    renderWithProviders(<Settings />);

    expect(
      screen.getByRole("button", { name: /switch to light theme/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /switch to dark theme/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /switch to system theme/i }),
    ).toBeInTheDocument();
  });

  it("should render account actions with logout button", () => {
    renderWithProviders(<Settings />);

    expect(screen.getByRole("button", { name: /logout/i })).toBeInTheDocument();
  });

  it("should show loading skeleton while loading", () => {
    import { useCurrentUser } from "@hooks/useSettings";
    useCurrentUser.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    renderWithProviders(<Settings />);

    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("should show error message on load failure", () => {
    import { useCurrentUser } from "@hooks/useSettings";
    useCurrentUser.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error("Failed to load"),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByText(/failed to load settings/i)).toBeInTheDocument();
  });

  it("should have proper ARIA labels for accessibility", () => {
    renderWithProviders(<Settings />);

    expect(screen.getByRole("main", { name: /settings/i })).toBeInTheDocument();
    expect(
      screen.getByRole("region", { name: /profile information/i }),
    ).toBeInTheDocument();
  });

  it("should have proper heading structure", () => {
    renderWithProviders(<Settings />);

    const mainHeading = screen.getByRole("heading", { level: 1 });
    expect(mainHeading).toHaveTextContent(/settings/i);
  });

  it("should be keyboard navigable", () => {
    renderWithProviders(<Settings />);

    const editButton = screen.getByRole("button", { name: /edit profile/i });
    editButton.focus();
    expect(document.activeElement).toBe(editButton);
  });
});
