export function DocumentCardSkeleton() {
  return (
    <div className="rounded-xl bg-card border border-border p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <div className="p-3 rounded-lg bg-muted animate-pulse" />
          <div className="flex-1 min-w-0 space-y-2">
            <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
            <div className="h-3 bg-muted rounded animate-pulse w-1/2" />
          </div>
        </div>
        <div className="h-6 w-16 bg-muted rounded-full animate-pulse" />
      </div>
      <div className="inline-flex items-center px-2 py-0.5 rounded-md bg-muted animate-pulse h-5 w-12" />
    </div>
  );
}

export function DocumentGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <DocumentCardSkeleton key={i} />
      ))}
    </div>
  );
}
