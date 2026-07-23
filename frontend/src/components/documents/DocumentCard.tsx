import { memo } from "react";
import { useState } from "react";
import { motion } from "framer-motion";
import { cardVariants, microInteractions } from "@lib/animations";
import {
  FileText,
  Download,
  Trash2,
  Eye,
  FileVideo,
  Music,
  MessageSquare,
  MoreVertical,
  CheckCircle2,
  Circle,
} from "lucide-react";
import { BottomSheet } from "../common/BottomSheet";
import { DocumentSummary, FileType } from "@services/documentService";
import { DocumentStatusBadge } from "./DocumentStatusBadge";
import { formatTime } from "@lib/helpers/format";
import { cn } from "@lib/utils";

interface DocumentCardProps {
  document: DocumentSummary;
  onDelete: (id: string) => void;
  onDownload: (id: string) => void;
  onViewDetails?: (id: string) => void;
  onChat?: (id: string) => void;
  selectable?: boolean;
  selected?: boolean;
  onToggleSelection?: (id: string) => void;
}

const getFileIcon = (fileType: FileType) => {
  switch (fileType) {
    case FileType.PDF:
      return FileText;
    case FileType.VIDEO:
      return FileVideo;
    case FileType.AUDIO:
      return Music;
    default:
      return FileText;
  }
};

export const DocumentCard = memo(function DocumentCard({
  document,
  onDelete,
  onDownload,
  onViewDetails,
  onChat,
  selectable = false,
  selected = false,
  onToggleSelection,
}: DocumentCardProps) {
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const FileIcon = getFileIcon(document.file_type);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(document.id);
  };

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDownload(document.id);
  };

  const handleViewDetails = (e: React.MouseEvent) => {
    e.stopPropagation();
    onViewDetails?.(document.id);
  };

  const handleChat = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChat?.(document.id);
  };

  const handleClick = (e: React.MouseEvent) => {
    if (selectable && onToggleSelection) {
      e.preventDefault();
      e.stopPropagation();
      onToggleSelection(document.id);
    } else {
      handleViewDetails(e);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (selectable && onToggleSelection) {
        onToggleSelection(document.id);
      } else {
        handleViewDetails(e as unknown as React.MouseEvent);
      }
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      whileHover={!selectable ? microInteractions.card.hover : undefined}
      transition={microInteractions.card.transition}
      className={cn(
        "group relative rounded-xl bg-card border p-4 sm:p-6 transition-all cursor-pointer w-full h-auto",
        selected
          ? "border-primary ring-1 ring-primary shadow-md bg-primary/5"
          : "border-border hover:border-primary/50 hover:shadow-xl",
      )}
      role="article"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onClick={handleClick}
    >
      {/* Header Layout */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-2 sm:mb-4">
        {/* Left Side: Icon & Title */}
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          {selectable && (
            <div className="flex-shrink-0 mr-1 transition-colors">
              {selected ? (
                <CheckCircle2
                  className="w-5 h-5 text-primary"
                  fill="currentColor"
                />
              ) : (
                <Circle className="w-5 h-5 text-muted-foreground opacity-50" />
              )}
            </div>
          )}
          <motion.div
            className="p-3 rounded-lg bg-primary/10 text-primary flex-shrink-0"
            whileHover={{ scale: 1.05, rotate: 5 }}
            transition={{ duration: 0.2 }}
          >
            <FileIcon className="h-5 w-5" />
          </motion.div>

          <div className="flex-1 min-w-0">
            <h3
              className="text-sm font-semibold text-foreground text-truncate"
              title={document.original_filename}
            >
              {document.original_filename}
            </h3>
            {/* Hide secondary meta on mobile */}
            <p className="hidden sm:block text-xs text-muted-foreground mt-0.5">
              {formatTime(document.uploaded_at)}
            </p>
          </div>
        </div>

        {/* Right Side: Status (and desktop actions) */}
        <div className="flex items-center justify-between sm:justify-end gap-3 w-full sm:w-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <DocumentStatusBadge
              status={document.processing_status}
              size="sm"
            />
          </motion.div>

          {/* Mobile 3-dot Menu triggering Bottom Sheet */}
          <div className="sm:hidden" onClick={(e) => e.stopPropagation()}>
            <BottomSheet
              isOpen={isSheetOpen}
              onOpenChange={setIsSheetOpen}
              title={document.original_filename}
              description="Select an action"
              trigger={
                <button
                  className="touch-target p-2 -mr-2 rounded-lg text-muted-foreground hover:bg-muted"
                  aria-label="Document Options"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>
              }
            >
              <div className="flex flex-col gap-2 mt-4 pb-4">
                <button
                  onClick={(e) => {
                    setIsSheetOpen(false);
                    handleViewDetails(e);
                  }}
                  className="touch-target flex items-center gap-3 p-4 hover:bg-muted rounded-xl transition-colors text-left"
                >
                  <div className="p-2 bg-background border border-border rounded-lg">
                    <Eye className="w-4 h-4" />
                  </div>
                  <span className="font-medium text-foreground text-sm">
                    View details
                  </span>
                </button>
                {onChat && (
                  <button
                    onClick={(e) => {
                      setIsSheetOpen(false);
                      handleChat(e);
                    }}
                    className="touch-target flex items-center gap-3 p-4 hover:bg-muted rounded-xl transition-colors text-left"
                  >
                    <div className="p-2 bg-primary/10 text-primary rounded-lg">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                    <span className="font-medium text-foreground text-sm">
                      Chat
                    </span>
                  </button>
                )}
                <button
                  onClick={(e) => {
                    setIsSheetOpen(false);
                    handleDownload(e);
                  }}
                  className="touch-target flex items-center gap-3 p-4 hover:bg-muted rounded-xl transition-colors text-left"
                >
                  <div className="p-2 bg-background border border-border rounded-lg">
                    <Download className="w-4 h-4" />
                  </div>
                  <span className="font-medium text-foreground text-sm">
                    Download
                  </span>
                </button>
                <button
                  onClick={(e) => {
                    setIsSheetOpen(false);
                    handleDelete(e);
                  }}
                  className="touch-target flex items-center gap-3 p-4 hover:bg-destructive/10 rounded-xl transition-colors text-left text-destructive"
                >
                  <div className="p-2 bg-destructive/10 rounded-lg">
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </div>
                  <span className="font-medium text-sm">Delete</span>
                </button>
              </div>
            </BottomSheet>
          </div>
        </div>
      </div>

      {/* Desktop Quick Actions - Visible on Hover (Hidden in selectable mode) */}
      {!selectable && (
        <motion.div
          className="hidden sm:flex absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity items-center space-x-1"
          initial={false}
          animate={false}
        >
          {[
            { icon: Eye, label: "View details", handler: handleViewDetails },
            ...(onChat
              ? [{ icon: MessageSquare, label: "Chat", handler: handleChat }]
              : []),
            { icon: Download, label: "Download", handler: handleDownload },
            {
              icon: Trash2,
              label: "Delete",
              handler: handleDelete,
              destructive: true,
            },
          ].map((action, index) => (
            <motion.button
              key={action.label}
              initial={{ opacity: 0, x: 10 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={action.handler}
              className={cn(
                "p-2 rounded-lg transition-colors text-muted-foreground hover:text-foreground",
                action.destructive
                  ? "hover:bg-destructive/10 hover:text-destructive"
                  : "hover:bg-muted",
              )}
              aria-label={action.label}
              title={action.label}
            >
              <action.icon className="h-4 w-4" />
            </motion.button>
          ))}
        </motion.div>
      )}

      {/* File Type Badge */}
      <motion.div
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-md bg-muted text-xs text-muted-foreground mb-3"
      >
        {document.file_type.toUpperCase()}
      </motion.div>
    </motion.div>
  );
});
