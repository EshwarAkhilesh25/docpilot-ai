import { Plus, Sparkles, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ConversationItem } from "./ConversationItem";
import { ConversationListSkeleton } from "./ConversationSkeleton";
import { ConversationListItem } from "@services/chatService";
import { listItemVariants } from "@lib/animations";

interface ConversationSidebarProps {
  conversations: ConversationListItem[];
  activeSessionId: string | null;
  isLoading: boolean;
  error: string | null;
  onSelectConversation: (sessionId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (sessionId: string) => void;
  onCloseSidebar?: () => void;
}

export function ConversationSidebar({
  conversations,
  activeSessionId,
  isLoading,
  error,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onCloseSidebar,
}: ConversationSidebarProps) {
  return (
    <aside className="w-72 border-r bg-card flex flex-col h-full relative z-50">
      {/* Mobile Sidebar Header with Close Button */}
      <div className="lg:hidden flex items-center justify-between p-4 border-b border-border">
        <h2 className="font-semibold text-foreground">Conversations</h2>
        {onCloseSidebar && (
          <button
            onClick={onCloseSidebar}
            className="p-2 -mr-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Header */}
      <div
        className={`p-4 border-b ${!activeSessionId ? "hidden lg:block" : ""}`}
      >
        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          aria-label="Start new conversation"
        >
          <Plus className="w-4 h-4" />
          <span className="text-sm font-medium">New Conversation</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
        {isLoading ? (
          <ConversationListSkeleton />
        ) : error ? (
          <div className="p-4 text-center text-sm text-destructive">
            {error}
          </div>
        ) : conversations.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full text-center p-4"
          >
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6 text-muted-foreground" />
            </div>
            <h3 className="text-sm font-medium text-foreground mb-1">
              No conversations yet
            </h3>
            <p className="text-xs text-muted-foreground">
              Start a new conversation to begin
            </p>
          </motion.div>
        ) : (
          <AnimatePresence mode="popLayout">
            <div className="space-y-1">
              {conversations.map((conversation, index) => (
                <motion.div
                  key={conversation.session_id}
                  variants={listItemVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ delay: index * 0.05 }}
                >
                  <ConversationItem
                    sessionId={conversation.session_id}
                    preview={conversation.last_message_preview}
                    messageCount={conversation.message_count}
                    updatedAt={conversation.updated_at}
                    isActive={conversation.session_id === activeSessionId}
                    onClick={() =>
                      onSelectConversation(conversation.session_id)
                    }
                    onDelete={onDeleteConversation}
                  />
                </motion.div>
              ))}
            </div>
          </AnimatePresence>
        )}
      </div>
    </aside>
  );
}
