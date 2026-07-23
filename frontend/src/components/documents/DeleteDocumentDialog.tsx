import { useState } from "react";
import { AlertTriangle, Loader2 } from "lucide-react";
import { ResponsiveDialog } from "../common/ResponsiveDialog";

interface DeleteDocumentDialogProps {
  isOpen: boolean;
  documentName: string;
  onConfirm: () => Promise<void>;
  onCancel: () => void;
}

export function DeleteDocumentDialog({
  isOpen,
  documentName,
  onConfirm,
  onCancel,
}: DeleteDocumentDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async () => {
    setIsDeleting(true);
    try {
      await onConfirm();
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <ResponsiveDialog
      isOpen={isOpen}
      onOpenChange={(open) => {
        if (!open) onCancel();
      }}
      title="Delete Document"
      description={`Are you sure you want to delete "${documentName}"? This action cannot be undone.`}
      footer={
        <div className="flex justify-end gap-3 w-full">
          <button
            onClick={onCancel}
            disabled={isDeleting}
            className="touch-target px-4 py-2 rounded-lg border border-border text-sm font-medium text-foreground hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-1 md:flex-none"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={isDeleting}
            className="touch-target px-4 py-2 rounded-lg bg-destructive text-destructive-foreground text-sm font-medium hover:bg-destructive/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 flex-1 md:flex-none"
          >
            {isDeleting && <Loader2 className="h-4 w-4 animate-spin" />}
            <span>Delete</span>
          </button>
        </div>
      }
    >
      <div className="flex items-center space-x-3 mb-2 md:hidden">
        <div className="p-2 rounded-lg bg-destructive/10 text-destructive mx-auto">
          <AlertTriangle className="h-6 w-6" />
        </div>
      </div>
    </ResponsiveDialog>
  );
}
