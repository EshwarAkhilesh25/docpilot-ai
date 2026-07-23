import { memo } from "react";
import { motion } from "framer-motion";
import { MessageSquare } from "lucide-react";
import { cn } from "@lib/utils";

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
  className?: string;
  hasDocuments?: boolean;
  summarizePrompt?: string;
}

const SUGGESTIONS = [
  "Summarize this document",
  "Explain the key findings",
  "What are the important dates?",
  "Extract action items",
  "Compare two documents",
];

export const EmptyState = memo(
  ({ onSelectPrompt, className, summarizePrompt }: EmptyStateProps) => {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center h-full px-8",
          className,
        )}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl w-full"
        >
          <div className="inline-flex p-5 rounded-full bg-primary/10 text-primary mb-6">
            <MessageSquare className="h-10 w-10" />
          </div>

          <h2 className="text-2xl sm:text-3xl font-semibold text-foreground mb-3 tracking-tight">
            Welcome to AI Copilot
          </h2>

          <p className="text-muted-foreground mb-8 max-w-[280px] sm:max-w-md mx-auto text-sm sm:text-base">
            Start a new conversation to ask questions, extract insights, and
            summarize your documents instantly.
          </p>

          {/* Suggestions Grid */}
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 max-w-2xl mx-auto">
            {SUGGESTIONS.map((suggestion, index) => {
              const isFirst = index === 0;
              const promptText =
                isFirst && summarizePrompt ? summarizePrompt : suggestion;

              return (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onSelectPrompt(promptText)}
                  className={cn(
                    "touch-target flex items-center justify-center px-4 py-2 sm:px-5 sm:py-2.5 font-medium rounded-xl transition-colors text-sm sm:text-base",
                    isFirst
                      ? "bg-primary text-primary-foreground shadow-sm hover:bg-primary/90"
                      : "bg-muted text-foreground hover:bg-muted/80 border border-transparent",
                  )}
                >
                  {promptText}
                </motion.button>
              );
            })}
          </div>
        </motion.div>
      </div>
    );
  },
);

EmptyState.displayName = "EmptyState";
