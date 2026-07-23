import { motion } from "framer-motion";
import { cardVariants, staggerContainer } from "@lib/animations";
import { MessageSquare, MessageCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import {
  dashboardService,
  RecentConversation,
} from "@services/dashboardService";
import { ConversationListSkeleton } from "./DashboardSkeleton";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@lib/constants";
import { formatRelativeTime } from "@lib/helpers/format";

export function RecentConversations() {
  const navigate = useNavigate();
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", "data"],
    queryFn: () => dashboardService.loadDashboardData(),
    staleTime: 2 * 60 * 1000,
    gcTime: 5 * 60 * 1000,
    retry: 2,
    refetchOnWindowFocus: false,
  });

  const conversations = data?.recentConversations || [];

  if (isLoading) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">AI Conversations</h2>
          </div>
          <ConversationListSkeleton />
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">AI Conversations</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            Failed to load conversations
          </p>
        </div>
      </motion.div>
    );
  }

  if (conversations.length === 0) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 id="conversations-heading" className="text-lg font-semibold">
              AI Conversations
            </h2>
          </div>
          <div className="text-center py-8">
            <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground mb-2">
              No conversations yet
            </p>
            <button
              onClick={() => navigate(ROUTES.CHAT)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors text-sm mt-4"
            >
              <MessageCircle className="h-4 w-4" />
              Start Chat
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div variants={cardVariants} initial="initial" animate="animate">
      <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 id="conversations-heading" className="text-lg font-semibold">
            AI Conversations
          </h2>
          <button
            onClick={() => navigate(ROUTES.CHAT)}
            className="text-sm text-primary hover:underline focus:outline-none"
          >
            View all
          </button>
        </div>
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-2"
          role="list"
          aria-labelledby="conversations-heading"
        >
          {conversations.slice(0, 5).map((conv: RecentConversation) => (
            <motion.div
              key={conv.session_id}
              variants={cardVariants}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 border border-transparent hover:border-border transition-all cursor-pointer group focus:outline-none focus:ring-2 focus:ring-primary"
              role="listitem"
              tabIndex={0}
              onClick={() =>
                navigate(`${ROUTES.CHAT}?session=${conv.session_id}`)
              }
              onKeyDown={(e: React.KeyboardEvent) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  navigate(`${ROUTES.CHAT}?session=${conv.session_id}`);
                }
              }}
            >
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
                  <MessageSquare className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate text-foreground/90 group-hover:text-foreground transition-colors">
                    {conv.title || "Untitled Conversation"}
                  </p>
                  <p className="text-xs text-muted-foreground truncate mt-0.5 max-w-[200px] sm:max-w-md">
                    {conv.last_message || "Continue this conversation..."}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 ml-4 shrink-0">
                <div className="text-xs text-muted-foreground w-20 text-right">
                  {formatRelativeTime(conv.updated_at)}
                </div>
                <div className="hidden sm:flex items-center justify-center min-w-[1.5rem] h-6 px-1.5 bg-blue-500/10 text-blue-500 text-[10px] font-bold rounded-full">
                  {conv.message_count}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  );
}
