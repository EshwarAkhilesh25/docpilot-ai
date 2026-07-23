import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DocumentCard } from "../DocumentCard";
import {
  DocumentSummary,
  FileType,
  ProcessingStatus,
} from "@services/documentService";

const mockDocument: DocumentSummary = {
  id: "1",
  original_filename: "test.pdf",
  file_type: FileType.PDF,
  processing_status: ProcessingStatus.COMPLETED,
  uploaded_at: "2024-01-01T00:00:00Z",
};

describe("DocumentCard", () => {
  it("should render document information", () => {
    render(
      <DocumentCard
        document={mockDocument}
        onDelete={vi.fn()}
        onDownload={vi.fn()}
      />,
    );

    expect(screen.getByText("test.pdf")).toBeInTheDocument();
  });

  it("should call onDelete when delete button is clicked", () => {
    const onDelete = vi.fn();
    render(
      <DocumentCard
        document={mockDocument}
        onDelete={onDelete}
        onDownload={vi.fn()}
      />,
    );

    const deleteButton = screen.getByLabelText("Delete");
    deleteButton.click();

    expect(onDelete).toHaveBeenCalledWith("1");
  });

  it("should call onDownload when download button is clicked", () => {
    const onDownload = vi.fn();
    render(
      <DocumentCard
        document={mockDocument}
        onDelete={vi.fn()}
        onDownload={onDownload}
      />,
    );

    const downloadButton = screen.getByLabelText("Download");
    downloadButton.click();

    expect(onDownload).toHaveBeenCalledWith("1");
  });
});
