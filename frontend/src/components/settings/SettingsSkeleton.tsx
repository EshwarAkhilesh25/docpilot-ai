export function SettingsSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="h-10 w-48 bg-muted rounded mb-2 animate-pulse" />
        <div className="h-6 w-96 bg-muted rounded animate-pulse" />
      </div>

      {/* Profile Section Skeleton */}
      <div className="rounded-xl bg-card border border-border p-6">
        <div className="mb-6">
          <div className="h-6 w-32 bg-muted rounded mb-1 animate-pulse" />
          <div className="h-4 w-64 bg-muted rounded animate-pulse" />
        </div>
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-full bg-muted animate-pulse" />
          <div className="flex-1 space-y-3">
            <div className="h-4 w-48 bg-muted rounded animate-pulse" />
            <div className="h-4 w-64 bg-muted rounded animate-pulse" />
            <div className="h-4 w-56 bg-muted rounded animate-pulse" />
          </div>
        </div>
      </div>

      {/* Appearance Section Skeleton */}
      <div className="rounded-xl bg-card border border-border p-6">
        <div className="mb-6">
          <div className="h-6 w-32 bg-muted rounded mb-1 animate-pulse" />
          <div className="h-4 w-64 bg-muted rounded animate-pulse" />
        </div>
        <div className="grid grid-cols-3 gap-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-muted/50"
            >
              <div className="w-6 h-6 bg-muted rounded animate-pulse" />
              <div className="h-4 w-16 bg-muted rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>

      {/* Account Section Skeleton */}
      <div className="rounded-xl bg-card border border-border p-6">
        <div className="mb-6">
          <div className="h-6 w-32 bg-muted rounded mb-1 animate-pulse" />
          <div className="h-4 w-64 bg-muted rounded animate-pulse" />
        </div>
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-muted animate-pulse" />
          <div className="flex-1 space-y-3">
            <div className="h-6 w-24 bg-muted rounded animate-pulse" />
            <div className="h-4 w-80 bg-muted rounded animate-pulse" />
            <div className="h-10 w-32 bg-muted rounded animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  );
}
