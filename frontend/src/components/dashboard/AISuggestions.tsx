import { motion } from "framer-motion";
import {
  cardVariants,
  staggerContainer,
  listItemVariants,
} from "@lib/animations";
import {
  Sparkles,
  FileText,
  BarChart2,
  HelpCircle,
  FileSearch,
  Search,
  ArrowRight,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@lib/constants";

export function AISuggestions() {
  const navigate = useNavigate();

  const suggestions = [
    {
      title: "Summarize Document",
      description: "Get a quick summary of long files",
      intent: "SUMMARIZE",
      icon: FileText,
      color: "text-orange-500",
      bg: "bg-orange-500/10",
    },
    {
      title: "Extract key points",
      description: "Find all important metrics and KPIs",
      intent: "KEY_FINDINGS",
      icon: FileSearch,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
    },
    {
      title: "Compare two documents",
      description: "See differences between two versions",
      intent: "COMPARE",
      icon: BarChart2,
      color: "text-green-500",
      bg: "bg-green-500/10",
    },
    {
      title: "Generate interview questions",
      description: "Create Q&A based on the text",
      intent: "GENERAL_QA",
      icon: HelpCircle,
      color: "text-purple-500",
      bg: "bg-purple-500/10",
    },
    {
      title: "Find specific information",
      description: "Search across your entire library",
      intent: "GENERAL_QA",
      icon: Search,
      color: "text-pink-500",
      bg: "bg-pink-500/10",
    },
  ];

  return (
    <motion.div variants={cardVariants} initial="initial" animate="animate">
      <div className="rounded-xl bg-card border border-border p-4 sm:p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-semibold">Recommended Actions</h2>
        </div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-2"
        >
          {suggestions.map((suggestion, index) => (
            <motion.button
              key={index}
              variants={listItemVariants}
              onClick={() =>
                navigate(ROUTES.DOCUMENTS, {
                  state: {
                    intent: suggestion.intent,
                    prompt: suggestion.title,
                  },
                })
              }
              className="touch-target flex flex-row items-center gap-4 w-full p-4 sm:p-5 rounded-xl bg-background border border-border hover:border-primary/50 transition-all group text-left shadow-sm"
            >
              <div
                className={`p-3 sm:p-2.5 rounded-lg shrink-0 ${suggestion.bg} ${suggestion.color}`}
              >
                <suggestion.icon className="h-8 w-8 sm:h-7 sm:w-7 md:h-6 md:w-6" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-semibold text-foreground group-hover:text-primary transition-colors">
                  {suggestion.title}
                </h3>
                <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                  {suggestion.description}
                </p>
              </div>
              <div className="shrink-0 pl-2">
                <ArrowRight className="h-5 w-5 text-muted-foreground opacity-50 group-hover:opacity-100 group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </div>
            </motion.button>
          ))}
        </motion.div>
      </div>
    </motion.div>
  );
}
