import { useState, memo } from "react";
import { motion } from "framer-motion";
import { Copy, FileText, Check } from "lucide-react";
import { cn } from "@lib/utils";

interface ResponseToolbarProps {
  onCopy?: () => void;
  onShowSources?: () => void;
  hasSources?: boolean;
  className?: string;
}

export const ResponseToolbar = memo(
  ({
    onCopy,
    onShowSources,
    hasSources = false,
    className,
  }: ResponseToolbarProps) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
      if (onCopy) {
        await onCopy();
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    };

    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("flex items-center gap-2", className)}
      >
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1.5 text-xs rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
          aria-label={copied ? "Copied!" : "Copy response"}
          aria-live="polite"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-green-500" />
              <span className="text-green-500">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>

        {hasSources && onShowSources && (
          <button
            onClick={onShowSources}
            className="flex items-center gap-1.5 px-2 py-1.5 text-xs rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
            aria-label="Show sources"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Sources</span>
          </button>
        )}
      </motion.div>
    );
  },
);

ResponseToolbar.displayName = "ResponseToolbar";
