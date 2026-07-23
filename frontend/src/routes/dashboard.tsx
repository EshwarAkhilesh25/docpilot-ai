import { motion } from "framer-motion";
import { useAuthStore } from "@store/authStore";
import { DashboardLayout } from "@components/layout/DashboardLayout";
import { DashboardHero } from "@components/dashboard/DashboardHero";
import { DashboardStats } from "@components/dashboard/DashboardStats";
import { RecentDocuments } from "@components/dashboard/RecentDocuments";
import { RecentConversations } from "@components/dashboard/RecentConversations";
import { ProcessingActivity } from "@components/dashboard/ProcessingActivity";
import { AISuggestions } from "@components/dashboard/AISuggestions";
import { PromptLibrary } from "@components/dashboard/PromptLibrary";
import { ErrorBoundary } from "@components/common/ErrorBoundary";
import { PremiumBackground } from "@components/common/PremiumBackground";
import { pageTransition } from "@lib/animations";

export default function Dashboard() {
  const { user } = useAuthStore();

  return (
    <DashboardLayout>
      <PremiumBackground variant="mesh" />
      <motion.div
        variants={pageTransition}
        initial="initial"
        animate="animate"
        exit="exit"
        className="w-full min-h-screen pb-12"
        role="main"
        aria-label="Dashboard"
      >
        <div className="space-y-8 max-w-7xl mx-auto">
          {/* Hero Section */}
          <ErrorBoundary>
            <section aria-labelledby="dashboard-heading">
              <h2 id="dashboard-heading" className="sr-only">
                Dashboard Overview
              </h2>
              <DashboardHero userName={user?.full_name || "User"} />
            </section>
          </ErrorBoundary>

          {/* Stats Cards */}
          <ErrorBoundary>
            <section aria-labelledby="stats-heading">
              <DashboardStats />
            </section>
          </ErrorBoundary>

          {/* Mobile Layout */}
          <div className="flex flex-col gap-6 md:hidden">
            <ErrorBoundary>
              <section aria-labelledby="suggestions-heading">
                <AISuggestions />
              </section>
            </ErrorBoundary>
            <ErrorBoundary>
              <section aria-labelledby="documents-heading">
                <RecentDocuments />
              </section>
            </ErrorBoundary>
            <ErrorBoundary>
              <section aria-labelledby="processing-heading">
                <ProcessingActivity />
              </section>
            </ErrorBoundary>
            <ErrorBoundary>
              <section aria-labelledby="conversations-heading">
                <RecentConversations />
              </section>
            </ErrorBoundary>
            <ErrorBoundary>
              <section aria-labelledby="prompt-library-heading">
                <PromptLibrary />
              </section>
            </ErrorBoundary>
          </div>

          {/* Desktop Layout */}
          <div className="hidden md:grid gap-6 md:grid-cols-2 items-start">
            {/* Left Column */}
            <div className="flex flex-col gap-6">
              <ErrorBoundary>
                <section aria-labelledby="documents-heading-desktop">
                  <RecentDocuments />
                </section>
              </ErrorBoundary>

              <ErrorBoundary>
                <section aria-labelledby="prompt-library-heading-desktop">
                  <PromptLibrary />
                </section>
              </ErrorBoundary>

              <ErrorBoundary>
                <section aria-labelledby="conversations-heading-desktop">
                  <RecentConversations />
                </section>
              </ErrorBoundary>
            </div>

            {/* Right Column */}
            <div className="flex flex-col gap-6">
              <ErrorBoundary>
                <section aria-labelledby="suggestions-heading-desktop">
                  <AISuggestions />
                </section>
              </ErrorBoundary>

              <ErrorBoundary>
                <section aria-labelledby="processing-heading-desktop">
                  <ProcessingActivity />
                </section>
              </ErrorBoundary>
            </div>
          </div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
