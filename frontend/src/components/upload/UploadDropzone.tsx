import { useCallback, useState } from "react";
import { Upload } from "lucide-react";
import { uploadService, ValidationError } from "@services/uploadService";

interface UploadDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  onValidationError: (errors: ValidationError[]) => void;
  disabled?: boolean;
  multiple?: boolean;
}

export function UploadDropzone({
  onFilesSelected,
  onValidationError,
  disabled = false,
  multiple = true,
}: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback(
    (files: File[]) => {
      // Validate files
      const errors = uploadService.validateFiles(files);

      if (errors.length > 0) {
        onValidationError(errors);
        // Filter out invalid files
        const validFiles = files.filter(
          (file) => !errors.some((error) => error.file === file),
        );
        if (validFiles.length > 0) {
          onFilesSelected(validFiles);
        }
      } else {
        onFilesSelected(files);
      }
    },
    [onValidationError, onFilesSelected],
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (!disabled) {
        setIsDragging(true);
      }
    },
    [disabled],
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files) as File[];
      handleFiles(files);
    },
    [disabled, handleFiles],
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;

      const files = Array.from(e.target.files || []) as File[];
      handleFiles(files);

      // Reset input
      e.target.value = "";
    },
    [disabled, handleFiles],
  );

  const handleClick = useCallback(() => {
    if (!disabled) {
      document.getElementById("file-input")?.click();
    }
  }, [disabled]);

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      className={`
        relative border-2 border-dashed rounded-xl p-6 sm:p-12 text-center cursor-pointer transition-all
        ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 hover:bg-muted/50"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : ""}
      `}
      role="button"
      tabIndex={0}
      aria-label="Upload files"
      onKeyDown={(e: React.KeyboardEvent) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      <input
        id="file-input"
        type="file"
        multiple={multiple}
        accept=".pdf,.docx,.mp3,.wav,.mp4"
        onChange={handleFileInput}
        className="hidden"
        disabled={disabled}
        aria-hidden="true"
      />

      <div className="flex flex-col items-center gap-4 pointer-events-none">
        <div
          className={`
          p-4 rounded-full transition-all
          ${isDragging ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}
        `}
        >
          <Upload className="h-8 w-8" />
        </div>

        <div className="flex flex-col items-center gap-2">
          <p className="text-lg font-medium text-foreground">
            {isDragging ? "Drop files here" : "Drag & drop your files here"}
          </p>
          <p className="text-sm text-muted-foreground">
            PDF, DOCX, MP3, WAV, MP4 (max 50MB)
          </p>
          <span className="touch-target px-6 py-2 mt-4 rounded-lg bg-primary text-primary-foreground font-medium pointer-events-auto hover:bg-primary/90 transition-colors inline-flex items-center justify-center">
            Select Files
          </span>
        </div>
      </div>
    </div>
  );
}
