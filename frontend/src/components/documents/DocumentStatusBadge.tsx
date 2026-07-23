import { ProcessingStatus, ProcessingStage } from "@services/documentService";
import {
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  FileText,
  Layers,
  Database,
  Search,
} from "lucide-react";

interface DocumentStatusBadgeProps {
  status: ProcessingStatus;
  stage?: ProcessingStage | null;
  size?: "sm" | "md";
}

export function DocumentStatusBadge({
  status,
  stage,
  size = "md",
}: DocumentStatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case ProcessingStatus.UPLOADED:
        return {
          label: "Uploaded",
          icon: Clock,
          color: "text-blue-600 dark:text-blue-400",
          bgColor: "bg-blue-100 dark:bg-blue-900/30",
        };
      case ProcessingStatus.PROCESSING:
        return {
          label: stage ? getStageLabel(stage) : "Processing",
          icon: stage ? getStageIcon(stage) : Loader2,
          color: "text-yellow-600 dark:text-yellow-400",
          bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
          animate: !stage || stage === ProcessingStage.QUEUED,
        };
      case ProcessingStatus.COMPLETED:
        return {
          label: "Completed",
          icon: CheckCircle,
          color: "text-green-600 dark:text-green-400",
          bgColor: "bg-green-100 dark:bg-green-900/30",
        };
      case ProcessingStatus.FAILED:
        return {
          label: "Needs Review",
          icon: AlertCircle,
          color: "text-amber-600 dark:text-amber-400",
          bgColor: "bg-amber-100 dark:bg-amber-900/30",
        };
      default:
        return {
          label: "Unknown",
          icon: Clock,
          color: "text-muted-foreground",
          bgColor: "bg-muted",
        };
    }
  };

  const getStageLabel = (stage: ProcessingStage) => {
    switch (stage) {
      case ProcessingStage.QUEUED:
        return "Queued";
      case ProcessingStage.EXTRACTING:
        return "Extracting";
      case ProcessingStage.CHUNKING:
        return "Chunking";
      case ProcessingStage.EMBEDDING:
        return "Embedding";
      case ProcessingStage.INDEXING:
        return "Indexing";
      case ProcessingStage.COMPLETED:
        return "Completed";
      case ProcessingStage.FAILED:
        return "Failed";
      default:
        return "Processing";
    }
  };

  const getStageIcon = (stage: ProcessingStage) => {
    switch (stage) {
      case ProcessingStage.QUEUED:
        return Clock;
      case ProcessingStage.EXTRACTING:
        return FileText;
      case ProcessingStage.CHUNKING:
        return Layers;
      case ProcessingStage.EMBEDDING:
        return Database;
      case ProcessingStage.INDEXING:
        return Search;
      case ProcessingStage.COMPLETED:
        return CheckCircle;
      case ProcessingStage.FAILED:
        return AlertCircle;
      default:
        return Loader2;
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;
  const sizeClasses =
    size === "sm" ? "text-xs px-2 py-0.5 gap-1.5" : "text-sm px-2.5 py-1 gap-2";
  const iconSize = size === "sm" ? "h-3 w-3" : "h-4 w-4";

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${config.bgColor} ${config.color} ${sizeClasses}`}
      role="status"
      aria-label={`Document status: ${config.label}`}
    >
      <Icon className={`${iconSize} ${config.animate ? "animate-spin" : ""}`} />
      <span>{config.label}</span>
    </span>
  );
}
