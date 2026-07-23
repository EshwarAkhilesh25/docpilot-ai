import {
  FileText,
  MessageSquare,
  ArrowUp,
  ArrowDown,
  CheckCircle2,
} from "lucide-react";
import { DashboardStatSkeleton } from "./DashboardSkeleton";
import { useQuery } from "@tanstack/react-query";
import { dashboardService, DashboardData } from "@services/dashboardService";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import aiCodeGeneratorGif from "@/AI Code Generator.gif";
import aiBotFrameGif from "@/Ai Bot Create Wireframe for Product Design Automation.gif";
import glassmorphismGif from "@/Glassmorphism Document Lottie Animation.gif";

function AnimatedCounter({ value }: { value: string | number }) {
  const [displayValue, setDisplayValue] = useState(
    typeof value === "number" ? 0 : value,
  );

  useEffect(() => {
    if (typeof value !== "number") {
      setDisplayValue(value);
      return;
    }

    const duration = 1000;
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing out quint
      const easeProgress = 1 - Math.pow(1 - progress, 5);
      setDisplayValue(Math.floor(easeProgress * value));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value]);

  return <span>{displayValue}</span>;
}

export function DashboardStats() {
  const {
    data: stats,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["dashboard", "data"],
    queryFn: () => dashboardService.loadDashboardData(),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 2,
    refetchOnWindowFocus: false,
    select: (data: DashboardData) => data.stats,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <DashboardStatSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-destructive/10 border border-destructive/20 rounded-xl text-destructive text-sm text-center">
        Failed to load statistics
      </div>
    );
  }

  // Mock trends for premium feel
  const statCards = [
    {
      title: "Total Documents",
      value: stats?.totalDocuments || 0,
      icon: <FileText className="h-5 w-5 text-blue-500" />,
      trend: { value: "3 today", isUp: true, color: "text-green-500" },
      bgGif: aiCodeGeneratorGif,
    },
    {
      title: "Total Conversations",
      value: stats?.totalConversations || 0,
      icon: <MessageSquare className="h-5 w-5 text-purple-500" />,
      trend: { value: "12 today", isUp: true, color: "text-green-500" },
      bgGif: aiBotFrameGif,
      imgClass: "scale-150 translate-x-4",
    },
    {
      title: "Ready Documents",
      value: stats?.completedDocuments || 0,
      icon: <CheckCircle2 className="h-5 w-5 text-teal-500" />,
      trend: {
        value: "Available for AI",
        isUp: true,
        color: "text-slate-400",
        isNeutral: true,
      },
      bgGif: glassmorphismGif,
      imgClass: "scale-110 translate-x-2",
    },
  ];

  const containerVariants = {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="grid grid-cols-1 sm:grid-cols-3 gap-4"
    >
      <h2 id="stats-heading" className="sr-only">
        Dashboard Statistics
      </h2>
      {statCards.map((stat) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          whileHover={{ y: -4 }}
          className="relative p-5 rounded-xl bg-card border border-border shadow-sm hover:shadow-md transition-all group overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-primary/5 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity z-0" />

          <div className="absolute inset-0 w-full h-full pointer-events-none z-0 overflow-hidden rounded-xl flex items-center justify-end p-2 opacity-90">
            <img
              src={stat.bgGif}
              alt="AI Decor"
              className={`max-w-full max-h-full object-contain object-right ${stat.imgClass || ""}`}
            />
          </div>

          <div className="flex items-center gap-3 mb-3 relative z-10">
            <div className="p-2.5 rounded-lg bg-background border border-border group-hover:border-primary/30 transition-colors shadow-sm">
              {stat.icon}
            </div>
            <h3 className="text-sm font-medium text-muted-foreground">
              {stat.title}
            </h3>
          </div>

          <div className="flex flex-col gap-1 relative z-10">
            <span className="text-3xl font-bold tracking-tight text-foreground">
              <AnimatedCounter value={stat.value} />
            </span>

            {stat.trend && (
              <div
                className={`flex items-center gap-1 text-xs font-medium ${stat.trend.color}`}
              >
                {!stat.trend.isNeutral &&
                  (stat.trend.isUp ? (
                    <ArrowUp className="w-3 h-3" />
                  ) : (
                    <ArrowDown className="w-3 h-3" />
                  ))}
                <span>{stat.trend.value}</span>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
