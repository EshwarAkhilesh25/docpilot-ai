import { motion } from "framer-motion";
import { cardVariants, staggerContainer } from "@lib/animations";
import { FileText, MoreHorizontal, Upload, MessageSquare } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { dashboardService, RecentDocument } from "@services/dashboardService";
import { DocumentListSkeleton } from "./DashboardSkeleton";
import { ROUTES } from "@lib/constants";
import { useNavigate } from "react-router-dom";
import { formatFileSize, formatRelativeTime } from "@lib/helpers/format";

export function RecentDocuments() {
  const navigate = useNavigate();
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", "data"],
    queryFn: () => dashboardService.loadDashboardData(),
    staleTime: 2 * 60 * 1000,
    gcTime: 5 * 60 * 1000,
    retry: 2,
    refetchOnWindowFocus: false,
  });

  const documents = data?.recentDocuments || [];

  if (isLoading) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Knowledge Library</h2>
          </div>
          <DocumentListSkeleton />
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Knowledge Library</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            Failed to load documents
          </p>
        </div>
      </motion.div>
    );
  }

  if (documents.length === 0) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 id="documents-heading" className="text-lg font-semibold">
              Knowledge Library
            </h2>
          </div>
          <div className="text-center py-8">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground mb-2">
              No documents uploaded yet
            </p>
            <button
              onClick={() => navigate(ROUTES.DOCUMENTS)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors text-sm mt-4"
            >
              <Upload className="h-4 w-4" />
              Upload Document
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div variants={cardVariants} initial="initial" animate="animate">
      <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 id="documents-heading" className="text-lg font-semibold">
            Knowledge Library
          </h2>
          <button
            onClick={() => navigate(ROUTES.DOCUMENTS)}
            className="text-sm text-primary hover:underline focus:outline-none"
          >
            View all
          </button>
        </div>
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-2"
          role="list"
          aria-labelledby="documents-heading"
        >
          {documents.map((doc: RecentDocument) => {
            const isPDF = doc.original_filename?.toLowerCase().endsWith(".pdf");

            return (
              <motion.div
                key={doc.id}
                variants={cardVariants}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 border border-transparent hover:border-border transition-all group"
                role="listitem"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div
                    className={`p-2.5 rounded-lg text-white text-xs font-bold ${isPDF ? "bg-red-500" : "bg-blue-500"}`}
                  >
                    {isPDF ? "PDF" : "DOC"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-sm font-medium truncate text-foreground/90 group-hover:text-foreground transition-colors cursor-pointer"
                      onClick={() => navigate(ROUTES.DOCUMENTS)}
                    >
                      {doc.original_filename}
                    </p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                      <span>{formatRelativeTime(doc.created_at)}</span>
                      <span>•</span>
                      <span>{formatFileSize(doc.file_size)}</span>
                      {doc.metadata?.page_count && (
                        <>
                          <span>•</span>
                          <span>{doc.metadata.page_count} pages</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="hidden sm:flex items-center gap-4 ml-4">
                  {doc.processing_status?.toLowerCase() === "completed" ? (
                    <span className="hidden sm:inline-flex px-2 py-0.5 text-[10px] font-medium rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                      Indexed
                    </span>
                  ) : doc.processing_status?.toLowerCase() === "failed" ? (
                    <span className="hidden sm:inline-flex px-2 py-0.5 text-[10px] font-medium rounded-full bg-amber-500/10 text-amber-500 border border-amber-500/20">
                      Needs Review
                    </span>
                  ) : doc.processing_status?.toLowerCase() === "processing" ? (
                    <span className="hidden sm:inline-flex px-2 py-0.5 text-[10px] font-medium rounded-full bg-yellow-500/10 text-yellow-500 border border-yellow-500/20">
                      Processing
                    </span>
                  ) : (
                    <span className="hidden sm:inline-flex px-2 py-0.5 text-[10px] font-medium rounded-full bg-slate-500/10 text-slate-500 border border-slate-500/20">
                      {doc.processing_status || "Unknown"}
                    </span>
                  )}

                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() =>
                        navigate(`${ROUTES.CHAT}?document=${doc.id}`)
                      }
                      className="p-1.5 hover:bg-background border border-transparent hover:border-border rounded-md text-muted-foreground hover:text-indigo-400 transition-colors"
                      title="Chat with document"
                    >
                      <MessageSquare className="h-4 w-4" />
                    </button>
                    <button className="p-1.5 hover:bg-background border border-transparent hover:border-border rounded-md text-muted-foreground hover:text-foreground transition-colors">
                      <MoreHorizontal className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </motion.div>
  );
}
