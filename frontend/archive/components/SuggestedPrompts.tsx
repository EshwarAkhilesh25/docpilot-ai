import { memo } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, ArrowRight } from 'lucide-react'
import { cn } from '@lib/utils'
import { SUGGESTED_PROMPTS } from '../../constants/suggestedPrompts'

interface SuggestedPromptsProps {
  prompts?: string[]
  onSelectPrompt: (prompt: string) => void
  className?: string
}

export const SuggestedPrompts = memo(({ 
  prompts = SUGGESTED_PROMPTS, 
  onSelectPrompt,
  className 
}: SuggestedPromptsProps) => {
  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center gap-2 text-muted-foreground">
        <Sparkles className="w-4 h-4" />
        <span className="text-sm font-medium">Suggested questions</span>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {prompts.map((prompt, index) => (
          <motion.button
            key={prompt}
            onClick={() => onSelectPrompt(prompt)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center justify-between gap-2 p-4 bg-muted/50 hover:bg-muted border border-border rounded-lg text-left transition-all duration-200 group"
          >
            <span className="text-sm text-foreground">{prompt}</span>
            <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors opacity-0 group-hover:opacity-100" />
          </motion.button>
        ))}
      </div>
    </div>
  )
})

SuggestedPrompts.displayName = 'SuggestedPrompts'
