import { useState, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import {
  UploadCloud,
  FileText,
  MessageSquare,
  CheckCircle2,
} from "lucide-react";
import { DashboardLayout } from "@components/layout/DashboardLayout";
import { UploadDropzone } from "@components/upload/UploadDropzone";
import { UploadQueue } from "@components/upload/UploadQueue";
import { UploadError } from "@components/upload/UploadError";
import { ErrorBoundary } from "@components/common/ErrorBoundary";
import { PremiumBackground } from "@components/common/PremiumBackground";

import { useUploadFile, useCancelUpload } from "@hooks/useUpload";
import {
  UploadFile,
  UploadStatus,
  ValidationError,
} from "@services/uploadService";
import {
  documentService,
  ProcessingStatus,
  DocumentSummary,
} from "@services/documentService";
import { useDocuments } from "@hooks/useDocuments";
import { useNavigate } from "react-router-dom";
import { ROUTES, UPLOAD_CONFIG } from "@lib/constants";
import { pageTransition } from "@lib/animations";

export default function Upload() {
  const navigate = useNavigate();
  const [uploads, setUploads] = useState<UploadFile[]>([]);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>(
    [],
  );
  const [apiError, setApiError] = useState<Error | null>(null);

  const uploadMutation = useUploadFile();
  const { cancel } = useCancelUpload();
  const { data: documentsData } = useDocuments({
    page: 1,
    page_size: 100,
    status: ProcessingStatus.PROCESSING,
  });

  // Restore processing state from backend on page load
  useEffect(() => {
    if (documentsData?.items) {
      const processingUploads: UploadFile[] = documentsData.items
        .filter(
          (doc: DocumentSummary) =>
            doc.processing_status === ProcessingStatus.PROCESSING ||
            doc.processing_status === ProcessingStatus.UPLOADED,
        )
        .map((doc: DocumentSummary) => ({
          id: `processing-${doc.id}`,
          file: new File([], doc.stored_filename), // Placeholder file for display
          status: UploadStatus.PROCESSING,
          progress: { loaded: 0, total: doc.file_size || 0, percentage: 0 },
          documentId: doc.id,
          processingJobId: doc.processing_job_id,
        }));

      if (processingUploads.length > 0) {
        setUploads((prev: UploadFile[]) => {
          const existingIds = new Set(
            prev.map((u: UploadFile) => u.documentId),
          );
          const newUploads = processingUploads.filter(
            (u: UploadFile) => !existingIds.has(u.documentId),
          );
          return [...prev, ...newUploads];
        });
      }
    }
  }, [documentsData]);

  const startUpload = useCallback(
    async (upload: UploadFile) => {
      setUploads((prev: UploadFile[]) =>
        prev.map((u: UploadFile) =>
          u.id === upload.id ? { ...u, status: UploadStatus.UPLOADING } : u,
        ),
      );

      try {
        const response = await uploadMutation.mutateAsync({
          file: upload.file,
          uploadId: upload.id,
          onProgress: (progress) => {
            setUploads((prev: UploadFile[]) =>
              prev.map((u: UploadFile) =>
                u.id === upload.id ? { ...u, progress } : u,
              ),
            );
          },
        });

        setUploads((prev: UploadFile[]) =>
          prev.map((u: UploadFile) =>
            u.id === upload.id
              ? {
                  ...u,
                  status: UploadStatus.PROCESSING,
                  documentId: response.document_id,
                  processingJobId: response.processing_job_id,
                  progress: {
                    loaded: upload.file.size,
                    total: upload.file.size,
                    percentage: 100,
                  },
                }
              : u,
          ),
        );
      } catch (error: Error | unknown) {
        // Set API error for display on screen
        const err = error instanceof Error ? error : new Error("Upload failed");
        setApiError(err);

        setUploads((prev: UploadFile[]) =>
          prev.map((u: UploadFile) =>
            u.id === upload.id
              ? {
                  ...u,
                  status: UploadStatus.FAILED,
                  error: err.message || "Upload failed",
                }
              : u,
          ),
        );
      }
    },
    [uploadMutation],
  );

  const handleFilesSelected = useCallback(
    (files: File[]) => {
      // Check for duplicate files
      const duplicates: File[] = [];
      const validFiles: File[] = [];

      files.forEach((file: File) => {
        const isDuplicate = uploads.some(
          (u: UploadFile) =>
            u.file.name === file.name &&
            u.file.size === file.size &&
            u.file.lastModified === file.lastModified,
        );
        if (isDuplicate) {
          duplicates.push(file);
        } else {
          validFiles.push(file);
        }
      });

      if (duplicates.length > 0) {
        setValidationErrors(
          duplicates.map((file: File) => ({
            file,
            error: "This file is already in the upload queue",
          })),
        );
      }

      if (validFiles.length === 0) return;

      const newUploads: UploadFile[] = validFiles.map((file: File) => ({
        id: Math.random().toString(36).substring(7),
        file,
        status: UploadStatus.QUEUED,
        progress: { loaded: 0, total: file.size, percentage: 0 },
      }));

      setUploads((prev: UploadFile[]) => [...prev, ...newUploads]);

      // Start uploads sequentially (respect max concurrent)
      const activeCount = uploads.filter(
        (u: UploadFile) =>
          u.status === UploadStatus.QUEUED ||
          u.status === UploadStatus.UPLOADING,
      ).length;

      const slotsAvailable = UPLOAD_CONFIG.MAX_CONCURRENT_UPLOADS - activeCount;
      const filesToStart = newUploads.slice(0, Math.max(0, slotsAvailable));

      filesToStart.forEach((upload) => {
        startUpload(upload);
      });
    },
    [uploads, startUpload],
  );

  const handleValidationError = useCallback((errors: ValidationError[]) => {
    setValidationErrors(errors);
  }, []);

  const handleCancelUpload = useCallback(
    (uploadId: string) => {
      cancel(uploadId);
      setUploads((prev: UploadFile[]) =>
        prev.map((u: UploadFile) =>
          u.id === uploadId ? { ...u, status: UploadStatus.CANCELLED } : u,
        ),
      );
    },
    [cancel],
  );

  const handleRetryUpload = useCallback(
    (uploadId: string) => {
      const upload = uploads.find((u: UploadFile) => u.id === uploadId);
      if (upload) {
        setUploads((prev: UploadFile[]) =>
          prev.map((u: UploadFile) =>
            u.id === uploadId
              ? {
                  ...u,
                  status: UploadStatus.QUEUED,
                  error: undefined,
                  progress: {
                    loaded: 0,
                    total: upload.file.size,
                    percentage: 0,
                  },
                }
              : u,
          ),
        );
        startUpload(upload);
      }
    },
    [uploads, startUpload],
  );

  // Shared polling mechanism for all processing documents
  useEffect(() => {
    const processingUploads = uploads.filter(
      (u: UploadFile) => u.status === UploadStatus.PROCESSING && u.documentId,
    );

    if (processingUploads.length === 0) return;

    const pollInterval = setInterval(async () => {
      const documentIds = processingUploads.map(
        (u: UploadFile) => u.documentId!,
      );

      try {
        const statuses = await Promise.all(
          documentIds.map((id: string) =>
            documentService.getProcessingStatus(id),
          ),
        );

        setUploads((prev: UploadFile[]) => {
          let hasChanges = false;
          const updated = prev.map((u: UploadFile) => {
            if (!u.documentId || u.status !== UploadStatus.PROCESSING) return u;

            const statusIndex = documentIds.indexOf(u.documentId);
            if (statusIndex === -1) return u;

            const status = statuses[statusIndex];

            // Check if processing is complete
            if (status.status === "completed" || status.status === "failed") {
              hasChanges = true;
              return {
                ...u,
                status:
                  status.status === "completed"
                    ? UploadStatus.COMPLETED
                    : UploadStatus.FAILED,
                processingStage: status.stage,
                processingProgress: status.progress,
                ingestionReport: status.ingestion_report,
              };
            }

            // Update processing stage and progress
            if (
              u.processingStage !== status.stage ||
              u.processingProgress !== status.progress
            ) {
              hasChanges = true;
              return {
                ...u,
                processingStage: status.stage,
                processingProgress: status.progress,
                ingestionReport: status.ingestion_report,
              };
            }

            return u;
          });

          return hasChanges ? updated : prev;
        });
      } catch (error) {
        // Continue polling on error, individual failures are handled per document
      }
    }, UPLOAD_CONFIG.POLLING_INTERVAL);

    return () => clearInterval(pollInterval);
  }, [uploads]);

  // Start next queued upload when one completes
  useEffect(() => {
    const uploadingCount = uploads.filter(
      (u: UploadFile) => u.status === UploadStatus.UPLOADING,
    ).length;
    const queuedUploads = uploads.filter(
      (u: UploadFile) => u.status === UploadStatus.QUEUED,
    );

    if (
      uploadingCount < UPLOAD_CONFIG.MAX_CONCURRENT_UPLOADS &&
      queuedUploads.length > 0
    ) {
      const slotsAvailable =
        UPLOAD_CONFIG.MAX_CONCURRENT_UPLOADS - uploadingCount;
      const filesToStart = queuedUploads.slice(0, slotsAvailable);

      filesToStart.forEach((upload: UploadFile) => {
        startUpload(upload);
      });
    }
  }, [uploads, startUpload]);

  const handleOpenDocument = useCallback(
    (documentId?: string) => {
      navigate(
        documentId ? `${ROUTES.DOCUMENTS}?id=${documentId}` : ROUTES.DOCUMENTS,
      );
    },
    [navigate],
  );

  const handleStartChat = useCallback(
    (documentId?: string) => {
      navigate(
        documentId ? `${ROUTES.CHAT}?document=${documentId}` : ROUTES.CHAT,
      );
    },
    [navigate],
  );

  // Queue ordering: active > processing > completed > failed
  const sortedUploads = [...uploads].sort((a, b) => {
    const statusPriority: Record<UploadStatus, number> = {
      [UploadStatus.QUEUED]: 1,
      [UploadStatus.UPLOADING]: 1,
      [UploadStatus.PROCESSING]: 2,
      [UploadStatus.COMPLETED]: 3,
      [UploadStatus.FAILED]: 4,
      [UploadStatus.CANCELLED]: 5,
      [UploadStatus.UPLOADED]: 2,
    };

    const priorityA = statusPriority[a.status] || 99;
    const priorityB = statusPriority[b.status] || 99;

    if (priorityA !== priorityB) {
      return priorityA - priorityB;
    }

    // Stable ordering within same priority
    return uploads.indexOf(a) - uploads.indexOf(b);
  });

  const activeUploads = sortedUploads.filter(
    (u) =>
      u.status === UploadStatus.QUEUED || u.status === UploadStatus.UPLOADING,
  );

  const completedUploads = sortedUploads.filter(
    (u) => u.status === UploadStatus.COMPLETED,
  );
  const failedUploads = sortedUploads.filter(
    (u) => u.status === UploadStatus.FAILED,
  );

  return (
    <DashboardLayout>
      <PremiumBackground variant="particles" />
      <ErrorBoundary>
        <motion.div
          variants={pageTransition}
          initial="initial"
          animate="animate"
          exit="exit"
          className="container mx-auto px-4 py-8 max-w-7xl"
          role="main"
          aria-label="Upload documents"
        >
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Upload Documents
            </h1>
            <p className="text-muted-foreground">
              Upload PDF, MP3, WAV, or MP4 files for processing and analysis
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Upload Area */}
            <div className="lg:col-span-2">
              <UploadDropzone
                onFilesSelected={handleFilesSelected}
                onValidationError={handleValidationError}
                disabled={activeUploads.length > 0}
              />

              {/* Validation Errors */}
              {(validationErrors.length > 0 || apiError) && (
                <div className="mt-4">
                  <UploadError
                    errors={validationErrors}
                    apiError={apiError || undefined}
                    onDismiss={() => {
                      setValidationErrors([]);
                      setApiError(null);
                    }}
                  />
                </div>
              )}

              {/* Upload Queue */}
              {(activeUploads.length > 0 ||
                completedUploads.length > 0 ||
                failedUploads.length > 0) && (
                <div className="mt-6">
                  <UploadQueue
                    uploads={[
                      ...activeUploads,
                      ...completedUploads,
                      ...failedUploads,
                    ]}
                    onCancelUpload={handleCancelUpload}
                    onRetryUpload={handleRetryUpload}
                  />
                </div>
              )}

              {/* Success Actions */}
              {completedUploads.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                  className="mt-6 p-6 rounded-xl bg-green-500/10 border border-green-500/20 relative overflow-hidden"
                >
                  {/* Animated glow effect */}
                  <motion.div
                    className="absolute inset-0 bg-green-500/5"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />

                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{
                          delay: 0.2,
                          type: "spring",
                          stiffness: 200,
                        }}
                        className="p-2 rounded-full bg-green-500/20"
                      >
                        <motion.div
                          animate={{ rotate: [0, 360] }}
                          transition={{
                            duration: 1,
                            delay: 0.3,
                            ease: "easeOut",
                          }}
                        >
                          <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
                        </motion.div>
                      </motion.div>
                      <motion.h3
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="text-base font-semibold text-green-700 dark:text-green-400"
                      >
                        ✓ {completedUploads.length} document
                        {completedUploads.length > 1 ? "s" : ""} uploaded
                        successfully
                        <br />
                        <span className="text-sm font-normal opacity-90">
                          AI can now answer questions about{" "}
                          {completedUploads.length > 1
                            ? "these documents"
                            : "this document"}
                        </span>
                      </motion.h3>
                    </div>

                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 }}
                      className="flex gap-3"
                    >
                      <button
                        onClick={() =>
                          handleOpenDocument(completedUploads[0].documentId!)
                        }
                        className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
                      >
                        <FileText className="h-4 w-4" />
                        View Documents
                      </button>
                      <button
                        onClick={() =>
                          handleStartChat(completedUploads[0].documentId!)
                        }
                        className="inline-flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors text-sm font-medium"
                      >
                        <MessageSquare className="h-4 w-4" />
                        Start Chat
                      </button>
                    </motion.div>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Info Panel with 3D Scene */}
            <div className="lg:col-span-1">
              <div className="rounded-xl bg-card border border-border p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <UploadCloud className="h-5 w-5" />
                  </div>
                  <h3 className="font-semibold text-foreground">
                    Upload Guidelines
                  </h3>
                </div>

                <div className="space-y-4 text-sm">
                  <div>
                    <h4 className="font-medium text-foreground mb-2">
                      Supported Formats
                    </h4>
                    <ul className="space-y-1 text-muted-foreground">
                      <li>• PDF documents</li>
                      <li>• MP3 audio files</li>
                      <li>• WAV audio files</li>
                      <li>• MP4 video files</li>
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-medium text-foreground mb-2">
                      File Size Limit
                    </h4>
                    <p className="text-muted-foreground">
                      Maximum 50MB per file
                    </p>
                  </div>

                  <div>
                    <h4 className="font-medium text-foreground mb-2">
                      Processing
                    </h4>
                    <p className="text-muted-foreground">
                      We'll analyze your document securely so AI can answer
                      questions about it.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </ErrorBoundary>
    </DashboardLayout>
  );
}
