import { UploadStatus as UploadStatusEnum } from "@services/uploadService";
import {
  Clock,
  Loader2,
  CheckCircle2,
  XCircle,
  UploadCloud,
} from "lucide-react";

interface UploadStatusBadgeProps {
  status: UploadStatusEnum;
}

export function UploadStatus({ status }: UploadStatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case UploadStatusEnum.QUEUED:
        return {
          icon: <Clock className="h-3 w-3" />,
          label: "Queued",
          className: "bg-muted text-muted-foreground",
        };
      case UploadStatusEnum.UPLOADING:
        return {
          icon: <Loader2 className="h-3 w-3 animate-spin" />,
          label: "Uploading",
          className: "bg-blue-500/10 text-blue-500",
        };
      case UploadStatusEnum.UPLOADED:
        return {
          icon: <CheckCircle2 className="h-3 w-3" />,
          label: "Uploaded",
          className: "bg-green-500/10 text-green-500",
        };
      case UploadStatusEnum.PROCESSING:
        return {
          icon: <Loader2 className="h-3 w-3 animate-spin" />,
          label: "Analyzing",
          className: "bg-purple-500/10 text-purple-500",
        };
      case UploadStatusEnum.COMPLETED:
        return {
          icon: <CheckCircle2 className="h-3 w-3" />,
          label: "Ready",
          className: "bg-green-500/10 text-green-500",
        };
      case UploadStatusEnum.FAILED:
        return {
          icon: <XCircle className="h-3 w-3" />,
          label: "Failed",
          className: "bg-destructive/10 text-destructive",
        };
      case UploadStatusEnum.CANCELLED:
        return {
          icon: <XCircle className="h-3 w-3" />,
          label: "Cancelled",
          className: "bg-muted text-muted-foreground",
        };
      default:
        return {
          icon: <UploadCloud className="h-3 w-3" />,
          label: "Unknown",
          className: "bg-muted text-muted-foreground",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${config.className}`}
    >
      {config.icon}
      {config.label}
    </span>
  );
}
