import { cn } from '@lib/utils'

interface DividerProps {
  text?: string
  className?: string
}

export const Divider = ({ text, className }: DividerProps) => {
  return (
    <div className={cn('relative my-6', className)}>
      <div className="absolute inset-0 flex items-center">
        <span className="w-full border-t border-border" />
      </div>
      {text && (
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-card px-2 text-muted-foreground">{text}</span>
        </div>
      )}
    </div>
  )
}
