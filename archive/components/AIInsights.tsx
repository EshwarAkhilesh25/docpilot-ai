import { motion } from 'framer-motion'
import { cardVariants, staggerContainer } from '@lib/animations'
import { LineChart, CheckCircle2 } from 'lucide-react'

function MiniChart({ color }: { color: string }) {
  return (
    <svg className="w-full h-8 mt-2" viewBox="0 0 100 30" preserveAspectRatio="none">
      <path
        d="M0,25 C20,20 30,10 50,15 C70,20 80,5 100,10"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function AIInsights() {
  const insights = [
    { title: 'Documents Indexed', value: '3', trend: '↑ 200% from yesterday', color: '#8b5cf6' }, // purple
    { title: 'Questions Asked', value: '14', trend: '↑ 75% from yesterday', color: '#0ea5e9' }, // sky
    { title: 'Retrieval Quality', value: '98%', trend: 'Excellent', color: '#10b981', isTextTrend: true }, // emerald
    { title: 'Avg. Response', value: '2.1s', trend: '↓ 0.4s improvement', color: '#f43f5e' }, // rose
  ]

  return (
    <motion.div variants={cardVariants} initial="initial" animate="animate">
      <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <LineChart className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-semibold">Workspace Insights</h2>
          </div>
          <button className="text-sm text-primary hover:underline focus:outline-none">
            View Details
          </button>
        </div>
        
        <motion.div 
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4"
        >
          {insights.map((insight, index) => (
            <motion.div
              key={index}
              variants={cardVariants}
              className="p-4 rounded-lg bg-background border border-border/50 hover:border-border transition-colors"
            >
              <h3 className="text-sm text-muted-foreground mb-1">{insight.title}</h3>
              <div className="text-2xl font-bold text-foreground mb-1">{insight.value}</div>
              <div className={`text-xs ${insight.isTextTrend ? 'text-emerald-500' : 'text-muted-foreground'}`}>
                {insight.trend}
              </div>
              <MiniChart color={insight.color} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  )
}
