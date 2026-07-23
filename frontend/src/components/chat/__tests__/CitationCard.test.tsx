import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { CitationCard, CitationSource } from "../CitationCard";

describe("CitationCard", () => {
  const mockSource: CitationSource = {
    document_id: "doc-1",
    document_name: "Test Document.pdf",
    chunk_index: 1,
    page_number: 5,
    relevance_score: 0.95,
    text: "Sample citation text",
  };

  it("should render citation card", () => {
    render(<CitationCard source={mockSource} />);
    expect(screen.getByText("Test Document.pdf")).toBeInTheDocument();
    expect(screen.getByText("Page 5")).toBeInTheDocument();
    expect(screen.getByText("95%")).toBeInTheDocument();
  });

  it("should render without page number", () => {
    const sourceWithoutPage = { ...mockSource, page_number: undefined };
    render(<CitationCard source={sourceWithoutPage} />);
    expect(screen.queryByText("Page 5")).not.toBeInTheDocument();
  });

  it("should render without relevance score", () => {
    const sourceWithoutScore = { ...mockSource, relevance_score: undefined };
    render(<CitationCard source={sourceWithoutScore} />);
    expect(screen.queryByText("95%")).not.toBeInTheDocument();
  });

  it("should call onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<CitationCard source={mockSource} onClick={handleClick} />);

    const button = screen.getByRole("button");
    button.click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("should render highlighted state", () => {
    render(<CitationCard source={mockSource} isHighlighted={true} />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("bg-primary/10");
  });

  it("should render chunk index", () => {
    render(<CitationCard source={mockSource} />);
    expect(screen.getByText("Chunk 1")).toBeInTheDocument();
  });

  it("should render citation text", () => {
    render(<CitationCard source={mockSource} />);
    expect(screen.getByText("Sample citation text")).toBeInTheDocument();
  });
});
