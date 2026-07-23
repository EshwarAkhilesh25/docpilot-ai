import { memo } from "react";
import { motion } from "framer-motion";
import { Trash2, MessageSquare } from "lucide-react";
import { formatTimestamp } from "@lib/formatters";
import { cn } from "@lib/utils";

interface ConversationItemProps {
  sessionId: string;
  preview: string;
  messageCount: number;
  updatedAt: string;
  isActive?: boolean;
  onClick: () => void;
  onDelete: (sessionId: string) => void;
}

export const ConversationItem = memo(
  ({
    sessionId,
    preview,
    messageCount,
    updatedAt,
    isActive = false,
    onClick,
    onDelete,
  }: ConversationItemProps) => {
    const handleDelete = (e: React.MouseEvent) => {
      e.stopPropagation();
      onDelete(sessionId);
    };

    return (
      <motion.div
        onClick={onClick}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onClick();
          }
        }}
        tabIndex={0}
        whileHover={{ x: 4 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.2 }}
        className={cn(
          "w-full text-left p-3 rounded-lg transition-all group relative cursor-pointer",
          "hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
          isActive
            ? "bg-primary/15 border border-primary/20"
            : "bg-transparent border border-transparent",
        )}
        role="button"
        aria-label={`Conversation: ${preview}`}
        aria-current={isActive ? "page" : undefined}
      >
        {/* Active indicator */}
        {isActive && (
          <motion.div
            layoutId="activeIndicator"
            className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-l-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          />
        )}

        <div className="flex items-start gap-3 pl-1">
          <motion.div
            className={cn(
              "flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors",
              isActive
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground",
            )}
            whileHover={{ scale: 1.05, rotate: 5 }}
            transition={{ duration: 0.2 }}
          >
            <MessageSquare className="w-4 h-4" />
          </motion.div>

          <div className="flex-1 min-w-0">
            <p
              className={cn(
                "text-sm font-medium truncate transition-colors",
                isActive ? "text-foreground" : "text-foreground/90",
              )}
            >
              {preview}
            </p>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-muted-foreground">
                {messageCount} message{messageCount !== 1 ? "s" : ""}
              </span>
              <span className="text-xs text-muted-foreground/50">•</span>
              <span className="text-xs text-muted-foreground">
                {formatTimestamp(updatedAt)}
              </span>
            </div>
          </div>

          <motion.button
            onClick={handleDelete}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className={cn(
              "flex-shrink-0 p-1.5 rounded-md transition-all",
              "opacity-0 group-hover:opacity-100 focus:opacity-100",
              "hover:bg-destructive/10 hover:text-destructive",
              "focus:outline-none focus:ring-2 focus:ring-destructive",
            )}
            aria-label="Delete conversation"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </motion.button>
        </div>
      </motion.div>
    );
  },
);

ConversationItem.displayName = "ConversationItem";
