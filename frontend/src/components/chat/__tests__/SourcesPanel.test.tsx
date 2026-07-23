import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SourcesPanel, DocumentSource } from "../SourcesPanel";

describe("SourcesPanel", () => {
  const mockSources: DocumentSource[] = [
    {
      id: "1",
      original_filename: "doc1.pdf",
      file_type: "pdf",
      uploaded_at: "2024-01-01T00:00:00Z",
    },
    {
      id: "2",
      original_filename: "doc2.pptx",
      file_type: "pptx",
      uploaded_at: "2024-01-02T00:00:00Z",
    },
  ];

  it("should render sources panel when open", () => {
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId={null}
        onSourceSelect={vi.fn()}
        isOpen={true}
      />,
    );
    expect(screen.getByText("Sources")).toBeInTheDocument();
  });

  it("should not render when closed", () => {
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId={null}
        onSourceSelect={vi.fn()}
        isOpen={false}
      />,
    );
    expect(screen.queryByText("Sources")).not.toBeInTheDocument();
  });

  it("should render all documents option", () => {
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId={null}
        onSourceSelect={vi.fn()}
        isOpen={true}
      />,
    );
    expect(screen.getByText("All Documents")).toBeInTheDocument();
  });

  it("should render document sources", () => {
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId={null}
        onSourceSelect={vi.fn()}
        isOpen={true}
      />,
    );
    expect(screen.getByText("doc1.pdf")).toBeInTheDocument();
    expect(screen.getByText("doc2.pptx")).toBeInTheDocument();
  });

  it("should call onSourceSelect when source is clicked", () => {
    const handleSelect = vi.fn();
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId={null}
        onSourceSelect={handleSelect}
        isOpen={true}
      />,
    );

    const docButton = screen.getByText("doc1.pdf");
    docButton.click();

    expect(handleSelect).toHaveBeenCalledWith("1");
  });

  it("should call onSourceSelect with null when All Documents is clicked", () => {
    const handleSelect = vi.fn();
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId="1"
        onSourceSelect={handleSelect}
        isOpen={true}
      />,
    );

    const allButton = screen.getByText("All Documents");
    allButton.click();

    expect(handleSelect).toHaveBeenCalledWith(null);
  });

  it("should highlight selected source", () => {
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId="1"
        onSourceSelect={vi.fn()}
        isOpen={true}
      />,
    );
    const docButton = screen.getByText("doc1.pdf");
    expect(docButton).toHaveClass("bg-primary/10");
  });

  it("should call onClose when close button is clicked", () => {
    const handleClose = vi.fn();
    render(
      <SourcesPanel
        sources={mockSources}
        selectedSourceId={null}
        onSourceSelect={vi.fn()}
        isOpen={true}
        onClose={handleClose}
      />,
    );

    const closeButton = screen.getByLabelText("Close sources panel");
    closeButton.click();

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
