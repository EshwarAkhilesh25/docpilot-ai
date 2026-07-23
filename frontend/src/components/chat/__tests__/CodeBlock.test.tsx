import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { CodeBlock } from "../CodeBlock";

describe("CodeBlock", () => {
  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it("should render code block with language", () => {
    render(<CodeBlock language="javascript" code="const x = 1;" />);
    expect(screen.getByText("javascript")).toBeInTheDocument();
    expect(screen.getByText("const x = 1;")).toBeInTheDocument();
  });

  it("should render copy button", () => {
    render(<CodeBlock language="python" code="print('hello')" />);
    expect(screen.getByText("Copy")).toBeInTheDocument();
  });

  it("should copy code to clipboard", async () => {
    render(<CodeBlock language="javascript" code="const x = 1;" />);

    const copyButton = screen.getByText("Copy");
    copyButton.click();

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("const x = 1;");
  });

  it("should show copied state after copying", async () => {
    render(<CodeBlock language="javascript" code="const x = 1;" />);

    const copyButton = screen.getByText("Copy");
    copyButton.click();

    expect(screen.getByText("Copied")).toBeInTheDocument();
  });
});
