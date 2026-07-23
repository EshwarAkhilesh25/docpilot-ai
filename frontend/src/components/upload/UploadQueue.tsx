import { motion } from "framer-motion";
import { UploadFile } from "@services/uploadService";
import { UploadCard } from "./UploadCard";
import { staggerContainer } from "@lib/animations";

interface UploadQueueProps {
  uploads: UploadFile[];
  onCancelUpload: (uploadId: string) => void;
  onRetryUpload: (uploadId: string) => void;
}

export function UploadQueue({
  uploads,
  onCancelUpload,
  onRetryUpload,
}: UploadQueueProps) {
  if (uploads.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-foreground">
          Upload Queue ({uploads.length})
        </h3>
      </div>

      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="space-y-3"
      >
        {uploads.map((upload) => (
          <UploadCard
            key={upload.id}
            upload={upload}
            onCancel={() => onCancelUpload(upload.id)}
            onRetry={() => onRetryUpload(upload.id)}
          />
        ))}
      </motion.div>
    </div>
  );
}
