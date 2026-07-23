import { memo, lazy, Suspense } from "react";
import { motion } from "framer-motion";
import { MessageRole, MessageStatus } from "@services/chatService";
import { MessageAvatar } from "./MessageAvatar";
import { ResponseToolbar } from "./ResponseToolbar";
import { CitationCard, CitationSource } from "./CitationCard";
import { cn } from "@lib/utils";
import { RefreshCw } from "lucide-react";
import { listItemVariants } from "@lib/animations";

const MarkdownRenderer = lazy(() => import("./MarkdownRenderer"));

interface MessageBubbleProps {
  role: string;
  content: string;
  timestamp?: string;
  status?: MessageStatus;
  onRetry?: () => void;
  sources?: CitationSource[];
  onCopy?: () => void;
  onShowSources?: () => void;
}

export const MessageBubble = memo(
  ({
    role,
    content,
    timestamp,
    status,
    onRetry,
    sources,
    onCopy,
    onShowSources,
  }: MessageBubbleProps) => {
    const isUser = role === MessageRole.USER;
    const isFailed = status === MessageStatus.FAILED;
    const isSending = status === MessageStatus.SENDING;
    const hasSources = sources && sources.length > 0;

    return (
      <motion.div
        variants={listItemVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className={cn(
          "flex gap-3 mb-4",
          isUser ? "flex-row-reverse" : "flex-row",
        )}
      >
        <MessageAvatar role={role} />

        <div
          className={cn(
            "max-w-[90%] md:max-w-[80%] lg:max-w-[70%] rounded-2xl px-4 py-4",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-muted text-foreground rounded-tl-sm",
            isFailed && "border border-destructive",
          )}
        >
          {!isUser ? (
            <>
              {/* Assistant Response */}
              <div className="mb-3">
                <Suspense
                  fallback={
                    <div className="text-body whitespace-pre-wrap break-words leading-relaxed">
                      {content}
                    </div>
                  }
                >
                  <MarkdownRenderer content={content} />
                </Suspense>
              </div>

              {/* Sources Section */}
              {hasSources && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.3 }}
                  className="mb-3 pt-3 border-t border-border/50"
                >
                  <p className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wider">
                    Sources
                  </p>
                  <div className="space-y-2">
                    {sources.map((source, index) => (
                      <CitationCard
                        key={`${source.document_id}-${index}`}
                        source={source}
                      />
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Toolbar */}
              <div className="flex items-center justify-end">
                <ResponseToolbar
                  onCopy={onCopy}
                  onShowSources={hasSources ? onShowSources : undefined}
                  hasSources={hasSources}
                />
              </div>
            </>
          ) : (
            <p className="text-body whitespace-pre-wrap break-words leading-relaxed">
              {content}
            </p>
          )}

          {isSending && <p className="text-xs mt-1 opacity-70">Sending...</p>}
          {isFailed && (
            <div className="flex items-center gap-2 mt-2">
              <p className="text-xs text-destructive">Failed to send</p>
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="text-xs flex items-center gap-1 text-destructive hover:underline"
                  aria-label="Retry message"
                >
                  <RefreshCw className="w-3 h-3" />
                  Retry
                </button>
              )}
            </div>
          )}
          {timestamp && !isSending && (
            <p
              className={cn(
                "text-xs mt-1 opacity-70",
                isUser ? "text-primary-foreground/70" : "text-muted-foreground",
              )}
            >
              {new Date(timestamp).toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          )}
        </div>
      </motion.div>
    );
  },
);

MessageBubble.displayName = "MessageBubble";
