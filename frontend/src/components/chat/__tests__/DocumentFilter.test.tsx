import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DocumentFilter } from "../DocumentFilter";

describe("DocumentFilter", () => {
  const mockDocuments = [
    { id: "1", original_filename: "doc1.pdf", file_type: "pdf" },
    { id: "2", original_filename: "doc2.pptx", file_type: "pptx" },
    { id: "3", original_filename: "doc3.xlsx", file_type: "xlsx" },
  ];

  it("should render document filter", () => {
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={[]}
        onSelectionChange={vi.fn()}
      />,
    );
    expect(screen.getByText("All Documents")).toBeInTheDocument();
  });

  it("should show selected count when documents are selected", () => {
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={["1", "2"]}
        onSelectionChange={vi.fn()}
      />,
    );
    expect(screen.getByText("2 documents selected")).toBeInTheDocument();
  });

  it("should open dropdown when clicked", () => {
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={[]}
        onSelectionChange={vi.fn()}
      />,
    );

    const filterButton = screen.getByText("All Documents");
    filterButton.click();

    expect(screen.getByText("Select documents")).toBeInTheDocument();
  });

  it("should render document options in dropdown", () => {
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={[]}
        onSelectionChange={vi.fn()}
      />,
    );

    const filterButton = screen.getByText("All Documents");
    filterButton.click();

    expect(screen.getByText("doc1.pdf")).toBeInTheDocument();
    expect(screen.getByText("doc2.pptx")).toBeInTheDocument();
    expect(screen.getByText("doc3.xlsx")).toBeInTheDocument();
  });

  it("should select document when clicked", () => {
    const handleSelection = vi.fn();
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={[]}
        onSelectionChange={handleSelection}
      />,
    );

    const filterButton = screen.getByText("All Documents");
    filterButton.click();

    const docButton = screen.getByText("doc1.pdf");
    docButton.click();

    expect(handleSelection).toHaveBeenCalledWith(["1"]);
  });

  it("should deselect document when clicked", () => {
    const handleSelection = vi.fn();
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={["1"]}
        onSelectionChange={handleSelection}
      />,
    );

    const filterButton = screen.getByText("1 document selected");
    filterButton.click();

    const docButton = screen.getByText("doc1.pdf");
    docButton.click();

    expect(handleSelection).toHaveBeenCalledWith([]);
  });

  it("should select all when All button is clicked", () => {
    const handleSelection = vi.fn();
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={[]}
        onSelectionChange={handleSelection}
      />,
    );

    const filterButton = screen.getByText("All Documents");
    filterButton.click();

    const allButton = screen.getByText("All");
    allButton.click();

    expect(handleSelection).toHaveBeenCalledWith(["1", "2", "3"]);
  });

  it("should clear selection when Clear button is clicked", () => {
    const handleSelection = vi.fn();
    render(
      <DocumentFilter
        documents={mockDocuments}
        selectedIds={["1", "2"]}
        onSelectionChange={handleSelection}
      />,
    );

    const filterButton = screen.getByText("2 documents selected");
    filterButton.click();

    const clearButton = screen.getByText("Clear");
    clearButton.click();

    expect(handleSelection).toHaveBeenCalledWith([]);
  });
});
