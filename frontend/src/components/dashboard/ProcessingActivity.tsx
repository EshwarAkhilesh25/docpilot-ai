import { motion } from "framer-motion";
import { cardVariants, staggerContainer } from "@lib/animations";
import {
  Activity,
  Upload,
  Settings,
  CheckCircle2,
  FileText,
  Database,
  XCircle,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "@services/dashboardService";
import { formatRelativeTime } from "@lib/helpers/format";
import { ProcessingJobSkeleton } from "./DashboardSkeleton";

const getStepIcon = (status: string, step: string) => {
  if (status === "failed") return <XCircle className="w-4 h-4 text-red-500" />;
  if (status === "completed")
    return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;

  if (step.includes("upload"))
    return <Upload className="w-4 h-4 text-blue-500" />;
  if (step.includes("analyz"))
    return <Settings className="w-4 h-4 text-purple-500" />;
  if (step.includes("ready"))
    return <Database className="w-4 h-4 text-indigo-500" />;
  if (step.includes("process"))
    return <FileText className="w-4 h-4 text-orange-500" />;
  return <Activity className="w-4 h-4 text-muted-foreground" />;
};

export function ProcessingActivity() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", "data"],
    queryFn: () => dashboardService.loadDashboardData(),
    staleTime: 30 * 1000,
    gcTime: 2 * 60 * 1000,
    retry: 2,
    refetchOnWindowFocus: true,
  });

  // Create mock timeline from recent documents to simulate premium UI
  const documents = data?.recentDocuments || [];
  interface TimelineItem {
    id: string;
    step: string;
    status: string;
    time: string;
  }
  let timeline: TimelineItem[] = [];

  if (documents.length > 0) {
    const latestDoc = documents[0];
    timeline = [
      {
        id: "1",
        step: `${latestDoc.original_filename} uploaded`,
        status: "completed",
        time: latestDoc.created_at,
      },
      {
        id: "2",
        step: "Document analyzed successfully",
        status: "completed",
        time: latestDoc.created_at,
      },
      {
        id: "3",
        step: `Ready for AI questions`,
        status:
          latestDoc.processing_status === "failed"
            ? "failed"
            : latestDoc.processing_status === "completed"
              ? "completed"
              : "processing",
        time: latestDoc.updated_at,
      },
      {
        id: "4",
        step: `Processing complete`,
        status:
          latestDoc.processing_status === "failed"
            ? "failed"
            : latestDoc.processing_status === "completed"
              ? "completed"
              : "processing",
        time: latestDoc.updated_at,
      },
    ];
  }

  if (isLoading) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm h-full">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Recent Activity</h2>
          </div>
          <ProcessingJobSkeleton />
        </div>
      </motion.div>
    );
  }

  if (error || timeline.length === 0) {
    return (
      <motion.div variants={cardVariants} initial="initial" animate="animate">
        <div className="rounded-xl bg-card border border-border p-6 shadow-sm h-full">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Recent Activity</h2>
          </div>
          <div className="text-center py-6 text-sm text-muted-foreground">
            {error ? "Failed to load activity" : "No recent activity"}
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div variants={cardVariants} initial="initial" animate="animate">
      <div className="rounded-xl bg-card border border-border p-6 shadow-sm h-full">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            <h2 id="processing-heading" className="text-lg font-semibold">
              Recent Activity
            </h2>
          </div>
          <button className="text-sm text-primary hover:underline focus:outline-none">
            View All
          </button>
        </div>
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="relative before:absolute before:inset-y-0 before:left-3.5 before:w-px before:bg-border space-y-4"
          role="list"
          aria-labelledby="processing-heading"
        >
          {timeline.map((item) => (
            <motion.div
              key={item.id}
              variants={cardVariants}
              className="relative flex items-start gap-4"
              role="listitem"
            >
              <div
                className={`relative z-10 flex items-center justify-center w-7 h-7 rounded-full bg-background border border-border shrink-0
                ${item.status === "processing" ? "animate-pulse border-yellow-500/50 shadow-[0_0_10px_rgba(234,179,8,0.2)]" : ""}
              `}
              >
                {getStepIcon(item.status, item.step.toLowerCase())}
              </div>
              <div className="flex-1 min-w-0 pt-1">
                <p
                  className={`text-sm font-medium truncate ${item.status === "failed" ? "text-destructive" : "text-foreground"}`}
                >
                  {item.step}
                </p>
              </div>
              <div className="text-xs text-muted-foreground pt-1.5 shrink-0 ml-4">
                {formatRelativeTime(item.time)}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  );
}
