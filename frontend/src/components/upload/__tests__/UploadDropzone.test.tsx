import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { UploadDropzone } from "../UploadDropzone";

describe("UploadDropzone", () => {
  const mockOnFilesSelected = vi.fn();
  const mockOnValidationError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render dropzone", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
      />,
    );

    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
    expect(screen.getByText(/browse files/i)).toBeInTheDocument();
  });

  it("should be disabled when disabled prop is true", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
        disabled
      />,
    );

    const input = screen.getByRole("button").querySelector("input");
    expect(input).toBeDisabled();
  });

  it("should call onFilesSelected when valid files are selected", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
      />,
    );

    const input = screen
      .getByRole("button")
      .querySelector("input") as HTMLInputElement;
    const file = new File(["test"], "test.pdf", { type: "application/pdf" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(mockOnFilesSelected).toHaveBeenCalledWith([file]);
  });

  it("should call onValidationError when invalid files are selected", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
      />,
    );

    const input = screen
      .getByRole("button")
      .querySelector("input") as HTMLInputElement;
    const file = new File(["test"], "test.docx", { type: "application/docx" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(mockOnValidationError).toHaveBeenCalledWith([
      expect.objectContaining({
        file,
        error: expect.stringContaining("Unsupported file type"),
      }),
    ]);
  });

  it("should handle drag events", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
      />,
    );

    const dropzone = screen.getByRole("button");

    fireEvent.dragOver(dropzone);
    expect(dropzone).toHaveClass("border-primary");

    fireEvent.dragLeave(dropzone);
    expect(dropzone).not.toHaveClass("border-primary");
  });

  it("should handle drop event with valid files", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
      />,
    );

    const dropzone = screen.getByRole("button");
    const file = new File(["test"], "test.pdf", { type: "application/pdf" });

    const dataTransfer = {
      files: [file],
    } as unknown as DataTransfer;

    fireEvent.drop(dropzone, { dataTransfer });

    expect(mockOnFilesSelected).toHaveBeenCalledWith([file]);
  });

  it("should handle keyboard interaction", () => {
    render(
      <UploadDropzone
        onFilesSelected={mockOnFilesSelected}
        onValidationError={mockOnValidationError}
      />,
    );

    const dropzone = screen.getByRole("button");
    const input = dropzone.querySelector("input") as HTMLInputElement;
    const clickSpy = vi.spyOn(input, "click");

    fireEvent.keyDown(dropzone, { key: "Enter" });
    expect(clickSpy).toHaveBeenCalled();

    fireEvent.keyDown(dropzone, { key: " " });
    expect(clickSpy).toHaveBeenCalledTimes(2);
  });
});
