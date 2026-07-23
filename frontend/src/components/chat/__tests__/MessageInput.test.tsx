import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MessageInput } from "../MessageInput";

describe("MessageInput", () => {
  const mockOnSend = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render input with placeholder", () => {
    render(
      <MessageInput onSend={mockOnSend} placeholder="Type a message..." />,
    );

    const textarea = screen.getByPlaceholderText("Type a message...");
    expect(textarea).toBeInTheDocument();
  });

  it("should send message on Enter key", () => {
    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(textarea, { target: { value: "Test message" } });
    fireEvent.keyDown(textarea, { key: "Enter" });

    expect(mockOnSend).toHaveBeenCalledWith("Test message");
  });

  it("should not send on Shift+Enter", () => {
    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(textarea, { target: { value: "Test message" } });
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: true });

    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it("should send on button click", () => {
    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByRole("button", { name: /send message/i });

    fireEvent.change(textarea, { target: { value: "Test message" } });
    fireEvent.click(button);

    expect(mockOnSend).toHaveBeenCalledWith("Test message");
  });

  it("should be disabled when disabled prop is true", () => {
    render(<MessageInput onSend={mockOnSend} disabled />);

    const textarea = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByRole("button", { name: /send message/i });

    expect(textarea).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it("should not send empty messages", () => {
    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByRole("button", { name: /send message/i });

    fireEvent.change(textarea, { target: { value: "   " } });
    fireEvent.click(button);

    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it("should auto-resize textarea", () => {
    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(
      /type your message/i,
    ) as HTMLTextAreaElement;

    fireEvent.change(textarea, { target: { value: "A".repeat(200) } });

    // Height should increase from auto
    expect(textarea.style.height).not.toBe("auto");
  });
});
