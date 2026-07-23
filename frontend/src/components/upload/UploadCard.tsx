import { memo } from "react";
import { X, RefreshCw, FileText, Music, Video } from "lucide-react";
import { UploadFile, UploadStatus } from "@services/uploadService";
import { UploadProgress } from "./UploadProgress";
import { UploadStatus as UploadStatusBadge } from "./UploadStatus";

interface UploadCardProps {
  upload: UploadFile;
  onCancel: () => void;
  onRetry: () => void;
}

export const UploadCard = memo(function UploadCard({
  upload,
  onCancel,
  onRetry,
}: UploadCardProps) {
  const getFileIcon = () => {
    const ext = upload.file.name.split(".").pop()?.toLowerCase() || "";
    switch (ext) {
      case "pdf":
        return <FileText className="h-5 w-5" />;
      case "mp3":
      case "wav":
        return <Music className="h-5 w-5" />;
      case "mp4":
        return <Video className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const canCancel =
    upload.status === UploadStatus.QUEUED ||
    upload.status === UploadStatus.UPLOADING;
  const canRetry = upload.status === UploadStatus.FAILED;

  return (
    <div className="rounded-xl bg-card border border-border p-4">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-muted text-muted-foreground">
          {getFileIcon()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <p className="text-sm font-medium text-foreground truncate">
              {upload.file.name}
            </p>
            <div className="flex items-center gap-2">
              {canRetry && (
                <button
                  onClick={onRetry}
                  className="touch-target p-2 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                  aria-label="Retry upload"
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
              )}
              {canCancel && (
                <button
                  onClick={onCancel}
                  className="touch-target p-2 rounded hover:bg-destructive/10 transition-colors text-muted-foreground hover:text-destructive"
                  aria-label="Cancel upload"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
            <span>{formatFileSize(upload.file.size)}</span>
            <UploadStatusBadge status={upload.status} />
          </div>

          {/* Show upload progress while uploading or processing */}
          {(upload.status === UploadStatus.UPLOADING ||
            upload.status === UploadStatus.PROCESSING) && (
            <UploadProgress progress={upload.progress} />
          )}

          {/* Show processing progress only while processing */}
          {upload.status === UploadStatus.PROCESSING &&
            upload.processingStage && (
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-muted-foreground text-truncate pr-2">
                    {upload.processingStage?.toLowerCase().includes("embed") ||
                    upload.processingStage?.toLowerCase().includes("index")
                      ? "Preparing for AI..."
                      : "Analyzing document..."}
                  </span>
                  {upload.processingProgress !== undefined && (
                    <span className="text-muted-foreground">
                      {upload.processingProgress}%
                    </span>
                  )}
                </div>
                <div
                  className="h-1.5 bg-muted rounded-full overflow-hidden"
                  role="progressbar"
                  aria-valuenow={upload.processingProgress || 0}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="h-full bg-primary transition-all duration-300"
                    style={{ width: `${upload.processingProgress || 0}%` }}
                  />
                </div>
              </div>
            )}

          {upload.error && (
            <p
              className="text-xs text-destructive mt-2 text-truncate"
              title={upload.error}
            >
              {upload.error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
});
