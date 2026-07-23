import { ReactNode } from "react";
import { cn } from "@lib/utils";

interface AuthFooterProps {
  children: ReactNode;
  className?: string;
}

export const AuthFooter = ({ children, className }: AuthFooterProps) => {
  return (
    <div
      className={cn(
        "text-center text-sm text-muted-foreground mt-6",
        className,
      )}
    >
      {children}
    </div>
  );
};
