import { memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, FileIcon, X } from "lucide-react";
import { cn } from "@lib/utils";
import { formatTimestamp } from "@lib/formatters";

export interface DocumentSource {
  id: string;
  original_filename: string;
  file_type: string;
  uploaded_at: string;
}

interface SourcesPanelProps {
  sources: DocumentSource[];
  selectedSourceId: string | null;
  onSourceSelect: (sourceId: string | null) => void;
  onSourceClick?: (sourceId: string) => void;
  onClose?: () => void;
  isOpen: boolean;
}

export const SourcesPanel = memo(
  ({
    sources,
    selectedSourceId,
    onSourceSelect,
    onSourceClick,
    onClose,
    isOpen,
  }: SourcesPanelProps) => {
    const handleSourceClick = (sourceId: string) => {
      onSourceSelect(sourceId);
      if (onSourceClick) {
        onSourceClick(sourceId);
      }
    };
    return (
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="w-80 border-l bg-card flex flex-col h-full"
          >
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-sm">Sources</h3>
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-1 hover:bg-muted rounded-md transition-colors"
                  aria-label="Close sources panel"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              <button
                onClick={() => onSourceSelect(null)}
                className={cn(
                  "w-full text-left p-3 rounded-lg border transition-all duration-200",
                  "hover:shadow-md",
                  selectedSourceId === null
                    ? "bg-primary/10 border-primary/50 ring-2 ring-primary/20"
                    : "bg-muted/50 border-border hover:bg-muted",
                )}
              >
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium">All Documents</span>
                </div>
              </button>

              {sources.map((source) => (
                <motion.button
                  key={source.id}
                  onClick={() => handleSourceClick(source.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={cn(
                    "w-full text-left p-3 rounded-lg border transition-all duration-200",
                    "hover:shadow-md",
                    selectedSourceId === source.id
                      ? "bg-primary/10 border-primary/50 ring-2 ring-primary/20"
                      : "bg-muted/50 border-border hover:bg-muted",
                  )}
                  aria-label={`Select ${source.original_filename}`}
                >
                  <div className="flex items-start gap-2">
                    <FileIcon className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {source.original_filename}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted-foreground capitalize">
                          {source.file_type}
                        </span>
                        <span className="text-xs text-muted-foreground">•</span>
                        <span className="text-xs text-muted-foreground">
                          {formatTimestamp(source.uploaded_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    );
  },
);

SourcesPanel.displayName = "SourcesPanel";
