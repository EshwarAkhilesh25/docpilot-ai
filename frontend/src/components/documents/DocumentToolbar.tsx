import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@lib/constants";

interface DocumentToolbarProps {
  totalDocuments: number;
  onUploadClick?: () => void;
}

export function DocumentToolbar({
  totalDocuments,
  onUploadClick,
}: DocumentToolbarProps) {
  const navigate = useNavigate();

  const handleUpload = () => {
    if (onUploadClick) {
      onUploadClick();
    } else {
      navigate(ROUTES.UPLOAD);
    }
  };

  return (
    <div className="block md:flex md:items-center md:justify-between mb-6">
      <div className="mb-4 md:mb-0">
        <h1 className="text-3xl font-bold text-foreground mb-1">Documents</h1>
        <p className="text-sm text-muted-foreground">
          {totalDocuments === 0
            ? "No documents yet"
            : `${totalDocuments} document${totalDocuments !== 1 ? "s" : ""} in your library`}
        </p>
      </div>
      <button
        onClick={handleUpload}
        className="inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium w-full md:w-auto flex-shrink-0"
        aria-label="Upload new document"
      >
        <Plus className="h-5 w-5 shrink-0" />
        <span className="whitespace-nowrap">Upload Document</span>
      </button>
    </div>
  );
}
