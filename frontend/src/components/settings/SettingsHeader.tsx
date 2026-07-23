import { motion } from "framer-motion";
import { pageTransition } from "@lib/animations";

interface SettingsHeaderProps {
  title: string;
  subtitle: string;
}

export function SettingsHeader({ title, subtitle }: SettingsHeaderProps) {
  return (
    <motion.div
      variants={pageTransition}
      initial="initial"
      animate="animate"
      className="mb-8"
    >
      <h1
        id="settings-heading"
        className="text-4xl font-bold text-foreground mb-2"
      >
        {title}
      </h1>
      <p className="text-lg text-muted-foreground">{subtitle}</p>
    </motion.div>
  );
}
