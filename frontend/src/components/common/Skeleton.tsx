import { memo } from "react";
import { cn } from "@lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular" | "card" | "list";
  width?: string | number;
  height?: string | number;
}

export const Skeleton = memo(
  ({ className, variant = "rectangular", width, height }: SkeletonProps) => {
    const variantStyles = {
      text: "h-4 w-full rounded",
      circular: "h-10 w-10 rounded-full",
      rectangular: "h-12 w-full rounded-lg",
      card: "h-32 w-full rounded-xl",
      list: "h-16 w-full rounded-lg",
    };

    return (
      <div
        className={cn(
          "animate-pulse bg-muted",
          variantStyles[variant],
          className,
        )}
        style={{ width, height }}
        aria-hidden="true"
      />
    );
  },
);

Skeleton.displayName = "Skeleton";

// Pre-configured skeleton components for common patterns
export const SkeletonCard = memo(({ className }: { className?: string }) => (
  <div className={cn("p-4 space-y-3", className)}>
    <Skeleton variant="circular" className="h-12 w-12" />
    <Skeleton variant="text" className="h-4 w-3/4" />
    <Skeleton variant="text" className="h-4 w-1/2" />
  </div>
));

SkeletonCard.displayName = "SkeletonCard";

export const SkeletonList = memo(
  ({ count = 3, className }: { count?: number; className?: string }) => (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} variant="list" />
      ))}
    </div>
  ),
);

SkeletonList.displayName = "SkeletonList";

export const SkeletonText = memo(
  ({ lines = 3, className }: { lines?: number; className?: string }) => (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          className={i === lines - 1 ? "w-1/2" : "w-full"}
        />
      ))}
    </div>
  ),
);

SkeletonText.displayName = "SkeletonText";
