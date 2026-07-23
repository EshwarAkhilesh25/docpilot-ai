import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Upload } from "lucide-react";
import { DashboardLayout } from "@components/layout/DashboardLayout";
import { DocumentToolbar } from "@components/documents/DocumentToolbar";
import { DocumentSearch } from "@components/documents/DocumentSearch";
import { DocumentFilters } from "@components/documents/DocumentFilters";
import { DocumentCard } from "@components/documents/DocumentCard";
import { DocumentGridSkeleton } from "@components/documents/DocumentSkeleton";
import { DeleteDocumentDialog } from "@components/documents/DeleteDocumentDialog";
import { Pagination } from "@components/documents/Pagination";
import { ErrorBoundary } from "@components/common/ErrorBoundary";
import { PremiumBackground } from "@components/common/PremiumBackground";
import { useDocuments, useDeleteDocument } from "@hooks/useDocuments";
import {
  documentService,
  ProcessingStatus,
  DocumentSummary,
} from "@services/documentService";
import { staggerContainer } from "@lib/animations";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { ROUTES } from "@lib/constants";
import { ArrowRight, CheckCircle2 } from "lucide-react";

export default function Documents() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize state from URL params
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [statusFilter, setStatusFilter] = useState<ProcessingStatus | null>(
    (searchParams.get("status") as ProcessingStatus) || null,
  );
  const [page, setPage] = useState(
    parseInt(searchParams.get("page") || "1", 10),
  );
  const pageSize = 20;

  // Sync state with URL params
  useEffect(() => {
    const params: Record<string, string> = {};
    if (page > 1) params.page = page.toString();
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;
    setSearchParams(params);
  }, [page, search, statusFilter, setSearchParams]);

  const { data, isLoading, error } = useDocuments({
    page,
    page_size: pageSize,
    search: search || undefined,
    status: statusFilter || undefined,
  });

  const deleteMutation = useDeleteDocument();
  const [deleteDialog, setDeleteDialog] = useState<{
    isOpen: boolean;
    documentId: string;
    documentName: string;
  }>({
    isOpen: false,
    documentId: "",
    documentName: "",
  });

  const handleDelete = useCallback(
    (documentId: string, documentName: string) => {
      setDeleteDialog({ isOpen: true, documentId, documentName });
    },
    [],
  );

  const handleDeleteConfirm = useCallback(async () => {
    try {
      await deleteMutation.mutateAsync(deleteDialog.documentId);
      setDeleteDialog({ isOpen: false, documentId: "", documentName: "" });
    } catch (error) {
      // Error handling - mutation will handle rollback
    }
  }, [deleteDialog.documentId, deleteMutation]);

  const handleDownload = useCallback(async (documentId: string) => {
    try {
      await documentService.downloadDocument(documentId);
    } catch (error) {
      void 0;
    }
  }, []);

  const handleViewDetails = useCallback(async (documentId: string) => {
    // View document in browser instead of downloading
    try {
      await documentService.viewDocument(documentId);
    } catch (err) {
      void 0;
    }
  }, []);

  const location = useLocation();
  const intent = location.state?.intent;
  const isSelectionMode = intent === "PROMPT" || intent === "COMPARE";
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const handleToggleSelection = useCallback((id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((docId) => docId !== id) : [...prev, id],
    );
  }, []);

  const handleProceedWithSelection = useCallback(() => {
    if (selectedIds.length === 0) return;
    const query = selectedIds.map((id) => `document=${id}`).join("&");
    navigate(`${ROUTES.CHAT}?${query}`, {
      state: location.state,
    });
  }, [selectedIds, navigate, location.state]);

  const handleChat = useCallback(
    (documentId: string) => {
      navigate(`${ROUTES.CHAT}?document=${documentId}`, {
        state: location.state, // Forward any intent/prompt selected from Dashboard
      });
    },
    [navigate, location.state],
  );

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const handleFilterChange = useCallback(
    (newFilter: ProcessingStatus | null) => {
      setStatusFilter(newFilter);
      setPage(1); // Reset to first page when filter changes
    },
    [],
  );

  const handleSearchChange = useCallback((newSearch: string) => {
    setSearch(newSearch);
    setPage(1); // Reset to first page when search changes
  }, []);

  // Auto-navigate to previous page if current page becomes empty after deletion
  useEffect(() => {
    if (data && data.items.length === 0 && page > 1) {
      setPage(page - 1);
    }
  }, [data, page]);

  return (
    <DashboardLayout>
      <PremiumBackground variant="subtle" />
      <ErrorBoundary>
        <div
          className="container mx-auto px-4 py-8 max-w-7xl"
          role="main"
          aria-label="Documents"
        >
          <DocumentToolbar totalDocuments={data?.total || 0} />

          {/* Toolbar with search and filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <DocumentSearch
                value={search}
                onChange={handleSearchChange}
                isLoading={isLoading}
              />
            </div>
            <DocumentFilters
              value={statusFilter}
              onChange={handleFilterChange}
            />
          </div>

          {/* Error state */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl bg-destructive/10 border border-destructive/20 p-6 mb-6"
            >
              <p className="text-sm text-destructive">
                Failed to load documents. Please try again.
              </p>
            </motion.div>
          )}

          {/* Loading state */}
          {isLoading && <DocumentGridSkeleton count={pageSize} />}

          {/* Empty state */}
          {!isLoading && data?.items.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl bg-card border border-border p-12 text-center"
            >
              <div className="inline-flex p-4 rounded-full bg-primary/10 text-primary mb-4">
                <FileText className="h-8 w-8" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                {search || statusFilter
                  ? "No matching documents"
                  : "No documents yet"}
              </h3>
              <p className="text-sm text-muted-foreground mb-6">
                {search || statusFilter
                  ? "Try adjusting your search or filter criteria."
                  : "Upload your first document to get started."}
              </p>
              {!search && !statusFilter && (
                <button
                  onClick={() => navigate(ROUTES.UPLOAD)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
                >
                  <Upload className="h-4 w-4" />
                  Upload Document
                </button>
              )}
            </motion.div>
          )}

          {/* Document grid */}
          {!isLoading && data && data.items.length > 0 && (
            <motion.div
              variants={staggerContainer}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-6"
            >
              {data.items.map((document: DocumentSummary) => (
                <DocumentCard
                  key={document.id}
                  document={document}
                  onDelete={() =>
                    handleDelete(document.id, document.original_filename)
                  }
                  onDownload={handleDownload}
                  onViewDetails={(id) => handleViewDetails(id)}
                  onChat={isSelectionMode ? undefined : handleChat}
                  selectable={isSelectionMode}
                  selected={selectedIds.includes(document.id)}
                  onToggleSelection={handleToggleSelection}
                />
              ))}
            </motion.div>
          )}

          {/* Pagination */}
          {!isLoading && data && data.total_pages > 1 && (
            <Pagination
              currentPage={data.page}
              totalPages={data.total_pages}
              pageSize={data.page_size}
              total={data.total}
              onPageChange={handlePageChange}
            />
          )}

          {/* Delete confirmation dialog */}
          <DeleteDocumentDialog
            isOpen={deleteDialog.isOpen}
            documentName={deleteDialog.documentName}
            onConfirm={handleDeleteConfirm}
            onCancel={() =>
              setDeleteDialog({
                isOpen: false,
                documentId: "",
                documentName: "",
              })
            }
          />

          {/* Floating Action Bar for Selection Mode */}
          <AnimatePresence>
            {isSelectionMode && (
              <motion.div
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 100, opacity: 0 }}
                className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-md px-4"
              >
                <div className="bg-card border border-border rounded-full shadow-lg p-3 sm:p-4 flex items-center justify-between">
                  <div className="flex items-center gap-2 sm:gap-3 text-sm sm:text-base font-medium">
                    <div className="p-1.5 sm:p-2 bg-primary/10 text-primary rounded-full">
                      <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5" />
                    </div>
                    {selectedIds.length}{" "}
                    {selectedIds.length === 1 ? "document" : "documents"}{" "}
                    selected
                  </div>

                  <button
                    onClick={handleProceedWithSelection}
                    disabled={
                      selectedIds.length === 0 ||
                      (intent === "COMPARE" && selectedIds.length < 2)
                    }
                    className="flex items-center gap-2 bg-primary text-primary-foreground px-4 sm:px-6 py-2 sm:py-2.5 rounded-full font-medium text-sm sm:text-base hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    Proceed
                    <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </ErrorBoundary>
    </DashboardLayout>
  );
}
