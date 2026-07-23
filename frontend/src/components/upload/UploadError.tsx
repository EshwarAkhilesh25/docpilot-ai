import { XCircle, AlertCircle } from "lucide-react";
import { ValidationError } from "@services/uploadService";

interface UploadErrorProps {
  errors: ValidationError[];
  onDismiss: () => void;
  apiError?: Error | string; // Keep prop for compatibility but don't show technical details
}

export function UploadError({ errors, onDismiss, apiError }: UploadErrorProps) {
  if (errors.length === 0 && !apiError) {
    return null;
  }

  return (
    <div className="rounded-xl bg-destructive/5 border border-destructive/20 p-5">
      <div className="flex items-start gap-4">
        <div className="p-2 rounded-full bg-destructive/10 text-destructive mt-0.5">
          <AlertCircle className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <h4 className="text-base font-semibold text-destructive mb-2">
            {apiError
              ? "We couldn't understand this document."
              : "There was a problem with your file."}
          </h4>

          {/* Show friendly suggestions for API errors */}
          {apiError && (
            <div className="text-sm text-destructive/90 mb-4">
              <p className="mb-2">Try uploading:</p>
              <ul className="list-disc pl-5 space-y-1 mb-3">
                <li>A clearer scan</li>
                <li>A higher quality PDF</li>
                <li>A text-based document</li>
              </ul>
              <div className="text-xs opacity-80 italic">
                If the document is image-only: This document appears to be a
                scanned image. We're trying to extract the text. This may take a
                little longer.
              </div>
            </div>
          )}

          {/* Show friendly validation errors */}
          {errors.length > 0 && (
            <ul className="space-y-1 mt-2">
              {errors.map((error, index) => (
                <li key={index} className="text-sm text-destructive/80">
                  <span className="font-medium">{error.file.name}:</span>{" "}
                  {error.error}
                </li>
              ))}
            </ul>
          )}
        </div>
        <button
          onClick={onDismiss}
          className="p-1.5 rounded-lg hover:bg-destructive/10 transition-colors text-destructive/60 hover:text-destructive"
          aria-label="Dismiss errors"
        >
          <XCircle className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
