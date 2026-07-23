import { cn } from "@lib/utils";

interface AuthHeaderProps {
  title: string;
  description?: string;
  className?: string;
}

export const AuthHeader = ({
  title,
  description,
  className,
}: AuthHeaderProps) => {
  return (
    <div className={cn("text-center mb-10", className)}>
      <h1 className="text-4xl font-bold gradient-text mb-3">{title}</h1>
      {description && (
        <p className="text-base text-muted-foreground">{description}</p>
      )}
    </div>
  );
};
