import { ReactNode } from "react";
import { cn } from "@lib/utils";

interface AuthCardProps {
  children: ReactNode;
  className?: string;
}

export const AuthCard = ({ children, className }: AuthCardProps) => {
  return (
    <div
      className={cn(
        "w-full bg-card/60 backdrop-blur-2xl border border-border/70 rounded-2xl shadow-2xl overflow-hidden",
        "bg-gradient-to-br from-card/80 via-card/60 to-muted/30",
        className,
      )}
    >
      {children}
    </div>
  );
};
