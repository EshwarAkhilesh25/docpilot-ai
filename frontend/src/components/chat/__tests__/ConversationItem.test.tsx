import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConversationItem } from "../ConversationItem";

describe("ConversationItem", () => {
  const mockOnClick = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render conversation item", () => {
    render(
      <ConversationItem
        sessionId="session-1"
        preview="Test conversation"
        messageCount={5}
        updatedAt="2024-01-01T00:00:00Z"
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("Test conversation")).toBeInTheDocument();
    expect(screen.getByText("5 messages")).toBeInTheDocument();
  });

  it("should show active state when isActive is true", () => {
    render(
      <ConversationItem
        sessionId="session-1"
        preview="Test conversation"
        messageCount={5}
        updatedAt="2024-01-01T00:00:00Z"
        isActive
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />,
    );

    const button = screen.getByRole("button", {
      name: /conversation: test conversation/i,
    });
    expect(button).toHaveClass("bg-primary/10");
  });

  it("should call onClick when clicked", () => {
    render(
      <ConversationItem
        sessionId="session-1"
        preview="Test conversation"
        messageCount={5}
        updatedAt="2024-01-01T00:00:00Z"
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />,
    );

    const button = screen.getByRole("button", {
      name: /conversation: test conversation/i,
    });
    fireEvent.click(button);

    expect(mockOnClick).toHaveBeenCalled();
  });

  it("should call onDelete when delete button is clicked", () => {
    render(
      <ConversationItem
        sessionId="session-1"
        preview="Test conversation"
        messageCount={5}
        updatedAt="2024-01-01T00:00:00Z"
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />,
    );

    const deleteButton = screen.getByRole("button", {
      name: /delete conversation/i,
    });
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledWith("session-1");
    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it("should show singular message count", () => {
    render(
      <ConversationItem
        sessionId="session-1"
        preview="Test conversation"
        messageCount={1}
        updatedAt="2024-01-01T00:00:00Z"
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("1 message")).toBeInTheDocument();
  });
});
