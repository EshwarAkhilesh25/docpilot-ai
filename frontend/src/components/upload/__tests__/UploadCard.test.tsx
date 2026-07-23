import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { UploadCard } from "../UploadCard";
import { UploadFile, UploadStatus } from "@services/uploadService";

describe("UploadCard", () => {
  const mockOnCancel = vi.fn();
  const mockOnRetry = vi.fn();

  const baseUpload: UploadFile = {
    id: "upload-1",
    file: new File(["test"], "test.pdf", { type: "application/pdf" }),
    status: UploadStatus.QUEUED,
    progress: { loaded: 0, total: 1024, percentage: 0 },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render upload card with file info", () => {
    render(
      <UploadCard
        upload={baseUpload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    expect(screen.getByText("test.pdf")).toBeInTheDocument();
  });

  it("should show cancel button for queued status", () => {
    render(
      <UploadCard
        upload={baseUpload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    expect(cancelButton).toBeInTheDocument();
  });

  it("should show cancel button for uploading status", () => {
    const upload = { ...baseUpload, status: UploadStatus.UPLOADING };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    expect(cancelButton).toBeInTheDocument();
  });

  it("should show retry button for failed status", () => {
    const upload = {
      ...baseUpload,
      status: UploadStatus.FAILED,
      error: "Upload failed",
    };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    const retryButton = screen.getByRole("button", { name: /retry/i });
    expect(retryButton).toBeInTheDocument();
  });

  it("should not show cancel button for completed status", () => {
    const upload = { ...baseUpload, status: UploadStatus.COMPLETED };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    const cancelButton = screen.queryByRole("button", { name: /cancel/i });
    expect(cancelButton).not.toBeInTheDocument();
  });

  it("should show upload progress when uploading", () => {
    const upload = {
      ...baseUpload,
      status: UploadStatus.UPLOADING,
      progress: { loaded: 512, total: 1024, percentage: 50 },
    };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("should show processing progress when processing", () => {
    const upload = {
      ...baseUpload,
      status: UploadStatus.PROCESSING,
      processingStage: "chunking",
      processingProgress: 75,
    };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    expect(screen.getByText("chunking")).toBeInTheDocument();
    expect(screen.getByText("75%")).toBeInTheDocument();
  });

  it("should show error message when failed", () => {
    const upload = {
      ...baseUpload,
      status: UploadStatus.FAILED,
      error: "Network error",
    };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    expect(screen.getByText("Network error")).toBeInTheDocument();
  });

  it("should call onCancel when cancel button clicked", () => {
    render(
      <UploadCard
        upload={baseUpload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledWith("upload-1");
  });

  it("should call onRetry when retry button clicked", () => {
    const upload = {
      ...baseUpload,
      status: UploadStatus.FAILED,
      error: "Upload failed",
    };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    const retryButton = screen.getByRole("button", { name: /retry/i });
    fireEvent.click(retryButton);

    expect(mockOnRetry).toHaveBeenCalledWith("upload-1");
  });

  it("should format file size correctly", () => {
    const upload = {
      ...baseUpload,
      file: new File(["x".repeat(1024 * 1024)], "large.pdf", {
        type: "application/pdf",
      }),
    };
    render(
      <UploadCard
        upload={upload}
        onCancel={mockOnCancel}
        onRetry={mockOnRetry}
      />,
    );

    expect(screen.getByText(/1 MB/i)).toBeInTheDocument();
  });
});
