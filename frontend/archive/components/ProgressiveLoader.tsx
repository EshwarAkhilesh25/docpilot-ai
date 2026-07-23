import { memo } from 'react'
import { motion } from 'framer-motion'

interface ProgressiveLoaderProps {
  items: number
  renderItem: (index: number) => React.ReactNode
  className?: string
  staggerDelay?: number
}

export const ProgressiveLoader = memo(({ 
  items, 
  renderItem, 
  className,
  staggerDelay = 0.1 
}: ProgressiveLoaderProps) => {
  return (
    <div className={className}>
      {Array.from({ length: items }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * staggerDelay, duration: 0.3 }}
        >
          {renderItem(index)}
        </motion.div>
      ))}
    </div>
  )
})

ProgressiveLoader.displayName = 'ProgressiveLoader'
