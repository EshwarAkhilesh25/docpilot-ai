import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MarkdownRenderer } from "../MarkdownRenderer";

describe("MarkdownRenderer", () => {
  it("should render plain text", () => {
    render(<MarkdownRenderer content="Hello world" />);
    expect(screen.getByText("Hello world")).toBeInTheDocument();
  });

  it("should render bold text", () => {
    render(<MarkdownRenderer content="**bold text**" />);
    expect(screen.getByText("bold text")).toBeInTheDocument();
  });

  it("should render italic text", () => {
    render(<MarkdownRenderer content="*italic text*" />);
    expect(screen.getByText("italic text")).toBeInTheDocument();
  });

  it("should render headings", () => {
    render(<MarkdownRenderer content="# Heading 1" />);
    expect(screen.getByText("Heading 1")).toBeInTheDocument();
  });

  it("should render code blocks", () => {
    render(<MarkdownRenderer content="```javascript\nconst x = 1;\n```" />);
    expect(screen.getByText("const x = 1;")).toBeInTheDocument();
  });

  it("should render inline code", () => {
    render(<MarkdownRenderer content="`inline code`" />);
    expect(screen.getByText("inline code")).toBeInTheDocument();
  });

  it("should render lists", () => {
    render(<MarkdownRenderer content="- Item 1\n- Item 2" />);
    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
  });

  it("should render links", () => {
    render(<MarkdownRenderer content="[link](https://example.com)" />);
    const link = screen.getByText("link");
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "https://example.com");
    expect(link).toHaveAttribute("target", "_blank");
  });

  it("should render blockquotes", () => {
    render(<MarkdownRenderer content="> Quote text" />);
    expect(screen.getByText("Quote text")).toBeInTheDocument();
  });

  it("should render tables", () => {
    render(<MarkdownRenderer content="| Header |\n| --- |\n| Cell |" />);
    expect(screen.getByText("Header")).toBeInTheDocument();
    expect(screen.getByText("Cell")).toBeInTheDocument();
  });
});
