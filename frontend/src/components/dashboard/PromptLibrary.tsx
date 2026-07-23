import { motion } from "framer-motion";
import {
  cardVariants,
  staggerContainer,
  listItemVariants,
} from "@lib/animations";
import { Sparkles, Code, PenTool, FileText, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@lib/constants";

const PROMPT_TEMPLATES = [
  {
    title: "Executive Summary",
    description: "Condense long reports into 3 key takeaways",
    icon: FileText,
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
  {
    title: "Content Creator",
    description: "Transform docs into engaging blog posts",
    icon: PenTool,
    color: "text-purple-500",
    bg: "bg-purple-500/10",
  },
  {
    title: "Data Extraction",
    description: "Pull metrics and KPIs from raw data",
    icon: Code,
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
  },
];

export function PromptLibrary() {
  const navigate = useNavigate();

  return (
    <motion.div
      variants={cardVariants}
      initial="initial"
      animate="animate"
      className="h-full"
    >
      <div className="rounded-xl bg-card border border-border p-4 sm:p-6 shadow-sm flex flex-col h-full">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Prompt Library</h2>
            <p className="text-sm text-muted-foreground">
              Quick start your workflows
            </p>
          </div>
        </div>

        <motion.div
          variants={staggerContainer}
          className="space-y-4 flex-1 flex flex-col justify-center"
        >
          {PROMPT_TEMPLATES.map((template, i) => (
            <motion.button
              key={i}
              variants={listItemVariants}
              onClick={() =>
                navigate(ROUTES.DOCUMENTS, {
                  state: { intent: "PROMPT", prompt: template.title },
                })
              }
              className="touch-target flex flex-row items-center gap-4 w-full p-4 sm:p-5 rounded-xl bg-background border border-border hover:border-primary/50 transition-all group text-left shadow-sm"
            >
              <div
                className={`p-3 sm:p-2.5 rounded-lg shrink-0 ${template.bg} ${template.color}`}
              >
                <template.icon className="h-8 w-8 sm:h-7 sm:w-7 md:h-6 md:w-6" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-semibold text-foreground group-hover:text-primary transition-colors">
                  {template.title}
                </h3>
                <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                  {template.description}
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
