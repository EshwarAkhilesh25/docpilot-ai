import { useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ConversationMessage, MessageStatus } from "@services/chatService";

interface MessageListProps {
  messages: ConversationMessage[];
  isTyping?: boolean;
  onRetry?: (message: ConversationMessage) => void;
  className?: string;
}

export function MessageList({
  messages,
  isTyping = false,
  onRetry,
  className = "",
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  return (
    <div
      className={`flex-1 flex flex-col overflow-y-auto px-4 sm:px-6 py-6 space-y-6 ${className}`}
    >
      {messages.length === 0 && !isTyping && (
        <div className="flex items-center justify-center flex-1 text-muted-foreground">
          <p>No messages yet. Start a conversation!</p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role}
          content={message.content}
          timestamp={message.created_at}
          status={message.status}
          onRetry={
            message.status === MessageStatus.FAILED
              ? () => onRetry?.(message)
              : undefined
          }
        />
      ))}

      {isTyping && <TypingIndicator />}

      {/* Invisible element to scroll to */}
      <div ref={scrollRef} className="h-4" />
    </div>
  );
}
