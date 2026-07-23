import { memo } from "react";
import { motion } from "framer-motion";
import { FileText, ExternalLink } from "lucide-react";
import { cn } from "@lib/utils";

export interface CitationSource {
  document_id: string;
  document_name?: string;
  chunk_index?: number;
  page_number?: number;
  relevance_score?: number;
  text?: string;
}

interface CitationCardProps {
  source: CitationSource;
  isHighlighted?: boolean;
  onClick?: () => void;
  id?: string;
}

export const CitationCard = memo(
  ({ source, isHighlighted = false, onClick, id }: CitationCardProps) => {
    return (
      <motion.button
        id={id}
        onClick={onClick}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          "w-full text-left p-3 rounded-lg border transition-all duration-200",
          "hover:shadow-md",
          isHighlighted
            ? "bg-primary/10 border-primary/50 ring-2 ring-primary/20"
            : "bg-muted/50 border-border hover:bg-muted",
        )}
        aria-label={`Citation from ${source.document_name || "Document"}${source.page_number ? `, page ${source.page_number}` : ""}`}
      >
        <div className="flex items-start gap-2">
          <FileText className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium truncate">
                {source.document_name || "Unknown Document"}
              </p>
              {source.relevance_score !== undefined && (
                <span className="text-xs text-muted-foreground flex-shrink-0">
                  {Math.round(source.relevance_score * 100)}%
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1">
              {source.page_number && (
                <span className="text-xs text-muted-foreground">
                  Page {source.page_number}
                </span>
              )}
              {source.chunk_index !== undefined && (
                <span className="text-xs text-muted-foreground">
                  Chunk {source.chunk_index}
                </span>
              )}
            </div>
            {source.text && (
              <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                {source.text}
              </p>
            )}
          </div>
          {onClick && (
            <ExternalLink className="w-4 h-4 text-muted-foreground flex-shrink-0" />
          )}
        </div>
      </motion.button>
    );
  },
);

CitationCard.displayName = "CitationCard";
