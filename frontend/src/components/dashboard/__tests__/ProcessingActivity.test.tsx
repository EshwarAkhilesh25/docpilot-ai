import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ProcessingActivity } from "../ProcessingActivity";

describe("ProcessingActivity", () => {
  it("should render skeleton when loading", () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { enabled: false },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ProcessingActivity />
      </QueryClientProvider>,
    );

    expect(screen.getAllByRole("status")).toHaveLength(2);
  });

  it("should render empty state when no jobs", async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ProcessingActivity />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText(/No processing activity/)).toBeInTheDocument();
    });
  });

  it("should render processing jobs when available", async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ProcessingActivity />
      </QueryClientProvider>,
    );

    // Test would need mocked data to verify job rendering
    // This is a placeholder for the actual test implementation
  });
});
