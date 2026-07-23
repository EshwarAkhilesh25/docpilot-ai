import { memo } from "react";
import { motion } from "framer-motion";
import { FileText, Check, FileVideo, Music } from "lucide-react";
import { cn } from "@lib/utils";
import { DocumentSummary, FileType } from "@services/documentService";
import { ResponsiveDialog } from "../common/ResponsiveDialog";

interface DocumentLibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  documents: DocumentSummary[];
  selectedIds: string[];
  onSelectDocument: (documentId: string) => void;
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

export const DocumentLibraryModal = memo(
  ({
    isOpen,
    onClose,
    documents,
    selectedIds,
    onSelectDocument,
  }: DocumentLibraryModalProps) => {
    return (
      <ResponsiveDialog
        isOpen={isOpen}
        onOpenChange={(open) => {
          if (!open) onClose();
        }}
        title="Select Documents"
        description="Choose documents to attach to your conversation"
        footer={
          <div className="flex w-full items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {selectedIds.length} document{selectedIds.length !== 1 ? "s" : ""}{" "}
              selected
            </p>
            <button
              onClick={onClose}
              className="touch-target px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium shrink-0"
            >
              Done
            </button>
          </div>
        }
      >
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No documents available</p>
          </div>
        ) : (
          <div className="space-y-2 pb-4">
            {documents.map((document) => {
              const isSelected = selectedIds.includes(document.id);
              const FileIcon = getFileIcon(document.file_type);

              return (
                <motion.button
                  key={document.id}
                  onClick={() => onSelectDocument(document.id)}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  className={cn(
                    "w-full flex items-center gap-4 p-4 rounded-lg border transition-all",
                    "hover:bg-muted/50",
                    isSelected && "bg-primary/10 border-primary/30",
                  )}
                >
                  <div
                    className={cn(
                      "p-3 rounded-lg",
                      isSelected
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground",
                    )}
                  >
                    <FileIcon className="w-5 h-5" />
                  </div>

                  <div className="flex-1 text-left min-w-0">
                    <p className="font-medium text-foreground truncate">
                      {document.original_filename}
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5 truncate">
                      {document.file_type.toUpperCase()} •{" "}
                      {new Date(document.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>

                  {isSelected && (
                    <div className="p-2 rounded-full bg-primary text-primary-foreground shrink-0">
                      <Check className="w-4 h-4" />
                    </div>
                  )}
                </motion.button>
              );
            })}
          </div>
        )}
      </ResponsiveDialog>
    );
  },
);

DocumentLibraryModal.displayName = "DocumentLibraryModal";
