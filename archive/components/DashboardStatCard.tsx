import { motion } from 'framer-motion'
import { cardVariants } from '@lib/animations'
import { Loader2 } from 'lucide-react'

interface DashboardStatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  loading?: boolean
}

export function DashboardStatCard({ title, value, icon, loading }: DashboardStatCardProps) {
  return (
    <motion.div variants={cardVariants} className="relative">
      <div className="rounded-xl bg-card border border-border p-6 hover:border-primary/50 transition-colors">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground mb-2">{title}</p>
            {loading ? (
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            ) : (
              <p className="text-3xl font-bold text-foreground">{value}</p>
            )}
          </div>
          <div className="p-3 rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
