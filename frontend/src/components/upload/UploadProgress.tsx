import { UploadProgress as UploadProgressType } from "@services/uploadService";

interface UploadProgressProps {
  progress: UploadProgressType;
}

export function UploadProgress({ progress }: UploadProgressProps) {
  const formatSpeed = (bytesPerSecond?: number) => {
    if (!bytesPerSecond) return "";
    const k = 1024;
    const sizes = ["B/s", "KB/s", "MB/s", "GB/s"];
    const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k));
    return (
      Math.round((bytesPerSecond / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
    );
  };

  return (
    <div className="mt-2">
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="text-muted-foreground">
          {progress.loaded > 0 && (
            <>
              {progress.percentage}% ({formatSpeed(progress.speed)})
            </>
          )}
        </span>
        <span className="text-muted-foreground">
          {progress.loaded > 0 &&
            `${Math.round(progress.loaded / 1024)} KB / ${Math.round(progress.total / 1024)} KB`}
        </span>
      </div>
      <div
        className="h-1.5 bg-muted rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={progress.percentage}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full bg-primary transition-all duration-300"
          style={{ width: `${progress.percentage}%` }}
        />
      </div>
    </div>
  );
}
