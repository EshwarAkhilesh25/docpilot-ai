import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { ResponseToolbar } from "../ResponseToolbar";

describe("ResponseToolbar", () => {
  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it("should render copy button", () => {
    render(<ResponseToolbar />);
    expect(screen.getByText("Copy")).toBeInTheDocument();
  });

  it("should not render sources button when hasSources is false", () => {
    render(<ResponseToolbar hasSources={false} />);
    expect(screen.queryByText("Sources")).not.toBeInTheDocument();
  });

  it("should render sources button when hasSources is true", () => {
    render(<ResponseToolbar hasSources={true} onShowSources={vi.fn()} />);
    expect(screen.getByText("Sources")).toBeInTheDocument();
  });

  it("should call onCopy when copy button is clicked", async () => {
    const handleCopy = vi.fn();
    render(<ResponseToolbar onCopy={handleCopy} />);

    const copyButton = screen.getByText("Copy");
    copyButton.click();

    expect(handleCopy).toHaveBeenCalledTimes(1);
  });

  it("should show copied state after copy", async () => {
    render(<ResponseToolbar onCopy={vi.fn()} />);

    const copyButton = screen.getByText("Copy");
    copyButton.click();

    expect(screen.getByText("Copied")).toBeInTheDocument();
  });

  it("should call onShowSources when sources button is clicked", () => {
    const handleShowSources = vi.fn();
    render(
      <ResponseToolbar hasSources={true} onShowSources={handleShowSources} />,
    );

    const sourcesButton = screen.getByText("Sources");
    sourcesButton.click();

    expect(handleShowSources).toHaveBeenCalledTimes(1);
  });

  it("should have proper aria-label for copy button", () => {
    render(<ResponseToolbar />);
    const copyButton = screen.getByText("Copy");
    expect(copyButton).toHaveAttribute("aria-label", "Copy response");
  });

  it("should have aria-live for copy button", () => {
    render(<ResponseToolbar />);
    const copyButton = screen.getByText("Copy");
    expect(copyButton).toHaveAttribute("aria-live", "polite");
  });
});
