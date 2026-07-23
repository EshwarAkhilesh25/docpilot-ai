import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MessageBubble } from "../MessageBubble";
import { MessageRole, MessageStatus } from "@services/chatService";

describe("MessageBubble", () => {
  it("should render user message", () => {
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test message"
        timestamp="2024-01-01T00:00:00Z"
      />,
    );

    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("should render assistant message", () => {
    render(
      <MessageBubble
        role={MessageRole.ASSISTANT}
        content="Assistant response"
      />,
    );

    expect(screen.getByText("Assistant response")).toBeInTheDocument();
  });

  it("should render timestamp when provided", () => {
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test"
        timestamp="2024-01-01T00:00:00Z"
      />,
    );

    expect(screen.getByText(/12:00/)).toBeInTheDocument();
  });

  it("should handle long messages with wrapping", () => {
    const longMessage = "A".repeat(200);
    render(<MessageBubble role={MessageRole.USER} content={longMessage} />);

    expect(screen.getByText(longMessage)).toBeInTheDocument();
  });

  it("should render sending status", () => {
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test message"
        status={MessageStatus.SENDING}
      />,
    );

    expect(screen.getByText("Sending...")).toBeInTheDocument();
  });

  it("should render failed status", () => {
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test message"
        status={MessageStatus.FAILED}
      />,
    );

    expect(screen.getByText("Failed to send")).toBeInTheDocument();
  });

  it("should render retry button when failed and onRetry provided", () => {
    const onRetry = vi.fn();
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test message"
        status={MessageStatus.FAILED}
        onRetry={onRetry}
      />,
    );

    const retryButton = screen.getByText("Retry");
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalled();
  });

  it("should not render retry button when not failed", () => {
    const onRetry = vi.fn();
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test message"
        status={MessageStatus.SENT}
        onRetry={onRetry}
      />,
    );

    expect(screen.queryByText("Retry")).not.toBeInTheDocument();
  });

  it("should not render timestamp when sending", () => {
    render(
      <MessageBubble
        role={MessageRole.USER}
        content="Test message"
        timestamp="2024-01-01T00:00:00Z"
        status={MessageStatus.SENDING}
      />,
    );

    expect(screen.queryByText(/12:00/)).not.toBeInTheDocument();
    expect(screen.getByText("Sending...")).toBeInTheDocument();
  });
});
