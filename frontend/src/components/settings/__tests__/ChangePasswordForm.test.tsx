import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ChangePasswordForm } from "../ChangePasswordForm";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock the useSettings hook
vi.mock("@hooks/useSettings", () => ({
  useChangePassword: () => ({
    mutateAsync: vi.fn(),
    error: null,
  }),
}));

describe("ChangePasswordForm", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    });
  });

  const renderWithQueryClient = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>,
    );
  };

  it("should render form with all fields", () => {
    renderWithQueryClient(<ChangePasswordForm />);

    expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /change password/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("should disable submit button when form is empty", () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });
    expect(submitButton).toBeDisabled();
  });

  it("should show validation error for empty current password", async () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/current password is required/i),
      ).toBeInTheDocument();
    });
  });

  it("should show validation error for empty new password", async () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });
    const currentPasswordInput = screen.getByLabelText(/current password/i);

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/new password is required/i)).toBeInTheDocument();
    });
  });

  it("should show validation error for password mismatch", async () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });
    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "DifferentPass123" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it("should show validation error for weak password", async () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });
    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "weak" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "weak" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/password must be at least 8 characters/i),
      ).toBeInTheDocument();
    });
  });

  it("should show validation error when new password equals current password", async () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });
    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

    fireEvent.change(currentPasswordInput, {
      target: { value: "SamePass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "SamePass123" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "SamePass123" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(
          /new password must be different from current password/i,
        ),
      ).toBeInTheDocument();
    });
  });

  it("should clear form after successful submission", async () => {
    import { useChangePassword } from "@hooks/useSettings";
    const mockMutateAsync = vi.fn().mockResolvedValue(undefined);
    useChangePassword.mockReturnValue({
      mutateAsync: mockMutateAsync,
      error: null,
    });

    renderWithQueryClient(<ChangePasswordForm />);

    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(currentPasswordInput).toHaveValue("");
      expect(newPasswordInput).toHaveValue("");
      expect(confirmPasswordInput).toHaveValue("");
    });
  });

  it("should show success message after successful change", async () => {
    import { useChangePassword } from "@hooks/useSettings";
    const mockMutateAsync = vi.fn().mockResolvedValue(undefined);
    useChangePassword.mockReturnValue({
      mutateAsync: mockMutateAsync,
      error: null,
    });

    renderWithQueryClient(<ChangePasswordForm />);

    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/password changed successfully/i),
      ).toBeInTheDocument();
    });
  });

  it("should show error message on API failure", async () => {
    import { useChangePassword } from "@hooks/useSettings";
    const mockMutateAsync = vi
      .fn()
      .mockRejectedValue(new Error("Invalid current password"));
    useChangePassword.mockReturnValue({
      mutateAsync: mockMutateAsync,
      error: new Error("Invalid current password"),
    });

    renderWithQueryClient(<ChangePasswordForm />);

    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/failed to change password/i),
      ).toBeInTheDocument();
    });
  });

  it("should cancel form and clear fields on cancel button click", () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
    const cancelButton = screen.getByRole("button", { name: /cancel/i });

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.click(cancelButton);

    expect(currentPasswordInput).toHaveValue("");
    expect(newPasswordInput).toHaveValue("");
    expect(confirmPasswordInput).toHaveValue("");
  });

  it("should handle escape key to cancel form", () => {
    renderWithQueryClient(<ChangePasswordForm />);

    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.keyDown(document, { key: "Escape" });

    expect(currentPasswordInput).toHaveValue("");
    expect(newPasswordInput).toHaveValue("");
    expect(confirmPasswordInput).toHaveValue("");
  });

  it("should disable submit button while loading", async () => {
    import { useChangePassword } from "@hooks/useSettings";
    const mockMutateAsync = vi.fn(() => new Promise(() => {}));
    useChangePassword.mockReturnValue({
      mutateAsync: mockMutateAsync,
      error: null,
    });

    renderWithQueryClient(<ChangePasswordForm />);

    const currentPasswordInput = screen.getByLabelText(/current password/i);
    const newPasswordInput = screen.getByLabelText(/new password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
    const submitButton = screen.getByRole("button", {
      name: /change password/i,
    });

    fireEvent.change(currentPasswordInput, {
      target: { value: "CurrentPass123" },
    });
    fireEvent.change(newPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "NewPass123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/changing\.\.\./i)).toBeInTheDocument();
    });
  });
});
