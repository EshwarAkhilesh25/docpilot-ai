import { useState, useRef, useEffect, useCallback, forwardRef } from "react";
import { Send } from "lucide-react";
import { cn } from "@lib/utils";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const MessageInput = forwardRef<HTMLTextAreaElement, MessageInputProps>(
  ({ onSend, disabled = false, placeholder = "Type your message..." }, ref) => {
    const [message, setMessage] = useState("");
    const internalRef = useRef<HTMLTextAreaElement>(null);
    const textareaRef =
      (ref as React.RefObject<HTMLTextAreaElement>) || internalRef;

    const autoResize = useCallback(() => {
      const textarea = textareaRef.current;
      if (textarea) {
        textarea.style.height = "auto";
        const newHeight = Math.min(textarea.scrollHeight, 200); // Max height of 200px
        textarea.style.height = `${newHeight}px`;
      }
    }, [textareaRef]);

    useEffect(() => {
      autoResize();
    }, [message, autoResize, textareaRef]);

    const handleSubmit = () => {
      const trimmed = message.trim();
      if (trimmed && !disabled) {
        onSend(trimmed);
        setMessage("");
        // Reset height
        if (textareaRef.current) {
          textareaRef.current.style.height = "auto";
        }
      }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    };

    return (
      <div className="flex items-end gap-3 px-4 pt-4 pb-[calc(1rem+env(safe-area-inset-bottom))] border-t bg-card shrink-0">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            "flex-1 resize-none rounded-xl border border-input bg-background px-4 py-3 text-sm",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "min-h-[48px] max-h-[200px]",
          )}
          style={{ height: "auto" }}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className={cn(
            "flex-shrink-0 w-12 h-12 rounded-xl bg-primary text-primary-foreground",
            "flex items-center justify-center transition-colors",
            "hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
          )}
          aria-label="Send message"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    );
  },
);

MessageInput.displayName = "MessageInput";
