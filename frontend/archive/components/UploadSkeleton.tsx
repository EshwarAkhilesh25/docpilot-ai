export function UploadCardSkeleton() {
  return (
    <div className="rounded-xl bg-card border border-border p-4">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-muted animate-pulse">
          <div className="h-5 w-5 bg-muted-foreground/20 rounded" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <div className="h-4 w-3/4 bg-muted animate-pulse rounded" />
            <div className="h-4 w-4 bg-muted animate-pulse rounded" />
          </div>
          
          <div className="flex items-center justify-between mb-2">
            <div className="h-3 w-16 bg-muted animate-pulse rounded" />
            <div className="h-5 w-16 bg-muted animate-pulse rounded-full" />
          </div>

          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-muted-foreground/20 w-1/3 animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  )
}

interface UploadQueueSkeletonProps {
  count?: number
}

export function UploadQueueSkeleton({ count = 3 }: UploadQueueSkeletonProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="h-4 w-32 bg-muted animate-pulse rounded" />
      </div>
      
      <div className="space-y-3">
        {Array.from({ length: count }).map((_, index) => (
          <UploadCardSkeleton key={index} />
        ))}
      </div>
    </div>
  )
}
