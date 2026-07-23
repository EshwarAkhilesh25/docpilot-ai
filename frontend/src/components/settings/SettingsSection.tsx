import { ReactNode } from "react";
import { motion } from "framer-motion";
import { cardVariants } from "@lib/animations";
import { cn } from "@lib/utils";

interface SettingsSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export function SettingsSection({
  title,
  description,
  children,
  className,
}: SettingsSectionProps) {
  return (
    <motion.div
      variants={cardVariants}
      initial="initial"
      animate="animate"
      className={cn(
        "rounded-xl bg-card border border-border p-4 sm:p-6 shadow-sm",
        className,
      )}
    >
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-1">{title}</h2>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      <div>{children}</div>
    </motion.div>
  );
}
