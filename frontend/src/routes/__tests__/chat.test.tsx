import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import Chat from "../chat";

// Mock dependencies
vi.mock("@components/layout/DashboardLayout", () => ({
  DashboardLayout: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

vi.mock("@components/chat/ConversationSidebar", () => ({
  ConversationSidebar: ({
    onNewConversation,
    onSelectConversation,
    onDeleteConversation,
  }: unknown) => (
    <div>
      <button onClick={onNewConversation}>New Conversation</button>
      <button onClick={() => onSelectConversation("session-1")}>
        Select Conversation
      </button>
      <button onClick={() => onDeleteConversation("session-1")}>
        Delete Conversation
      </button>
    </div>
  ),
}));

vi.mock("@components/chat/MessageList", () => ({
  MessageList: ({ messages, isTyping }: unknown) => (
    <div>
      <div data-testid="message-count">{messages.length}</div>
      {isTyping && <div data-testid="typing">Typing...</div>}
    </div>
  ),
}));

vi.mock("@components/chat/MessageInput", () => ({
  MessageInput: ({ onSend, disabled }: unknown) => (
    <button onClick={() => onSend("test")} disabled={disabled}>
      Send
    </button>
  ),
}));

vi.mock("@components/common/ErrorBoundary", () => ({
  ErrorBoundary: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

vi.mock("@hooks/useChat", () => ({
  useChat: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      answer: "Test response",
      session_id: "session-123",
    }),
    isPending: false,
  }),
  useConversations: () => ({
    data: [],
    isLoading: false,
    error: null,
  }),
  useConversation: () => ({
    data: null,
    isLoading: false,
  }),
  useDeleteConversation: () => ({
    mutate: vi.fn(),
  }),
}));

vi.mock("@lib/animations", () => ({
  pageTransition: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  },
}));

describe("Chat Page", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const renderChat = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Chat />
        </BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("should render chat page with header", () => {
    renderChat();

    expect(screen.getByText("AI Workspace")).toBeInTheDocument();
  });

  it("should show empty state when no messages", () => {
    renderChat();

    expect(
      screen.getByText("Start your first conversation"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Ask questions about your uploaded documents/),
    ).toBeInTheDocument();
  });

  it("should render conversation sidebar", () => {
    renderChat();

    expect(screen.getByText("New Conversation")).toBeInTheDocument();
  });

  it("should render message input", () => {
    renderChat();

    expect(screen.getByText("Send")).toBeInTheDocument();
  });
});
