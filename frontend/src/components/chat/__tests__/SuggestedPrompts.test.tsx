import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SuggestedPrompts } from "../SuggestedPrompts";

describe("SuggestedPrompts", () => {
  const mockPrompts = ["Prompt 1", "Prompt 2", "Prompt 3"];
  const handleSelect = vi.fn();

  it("should render default prompts when none provided", () => {
    render(<SuggestedPrompts onSelectPrompt={handleSelect} />);
    expect(screen.getByText("Summarize this document.")).toBeInTheDocument();
  });

  it("should render custom prompts", () => {
    render(
      <SuggestedPrompts prompts={mockPrompts} onSelectPrompt={handleSelect} />,
    );
    expect(screen.getByText("Prompt 1")).toBeInTheDocument();
    expect(screen.getByText("Prompt 2")).toBeInTheDocument();
    expect(screen.getByText("Prompt 3")).toBeInTheDocument();
  });

  it("should call onSelectPrompt when prompt is clicked", () => {
    render(
      <SuggestedPrompts prompts={mockPrompts} onSelectPrompt={handleSelect} />,
    );

    const promptButton = screen.getByText("Prompt 1");
    promptButton.click();

    expect(handleSelect).toHaveBeenCalledWith("Prompt 1");
  });

  it("should render suggested questions label", () => {
    render(<SuggestedPrompts onSelectPrompt={handleSelect} />);
    expect(screen.getByText("Suggested questions")).toBeInTheDocument();
  });
});
