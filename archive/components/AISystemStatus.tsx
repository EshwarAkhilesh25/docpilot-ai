import { motion } from 'framer-motion'
import { cardVariants, staggerContainer } from '@lib/animations'
import { Activity, CheckCircle2 } from 'lucide-react'

export function AISystemStatus() {
  const systems = [
    { name: 'OCR Engine', status: 'Healthy' },
    { name: 'Embeddings (Text2Vec)', status: 'Healthy' },
    { name: 'Vector Database (FAISS)', status: 'Healthy' },
    { name: 'Keyword Search (BM25)', status: 'Healthy' },
    { name: 'LLM (Groq)', status: 'Healthy' },
    { name: 'PostgreSQL Database', status: 'Healthy' },
  ]

  return (
    <motion.div variants={cardVariants} initial="initial" animate="animate">
      <div className="rounded-xl bg-card border border-border p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-500" />
            <h2 className="text-lg font-semibold">System Health</h2>
          </div>
          <span className="text-xs font-medium px-2 py-1 bg-emerald-500/10 text-emerald-500 rounded-full border border-emerald-500/20">
            All Systems Operational
          </span>
        </div>
        
        <motion.div 
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-3 mt-4"
        >
          {systems.map((system, index) => (
            <motion.div
              key={index}
              variants={cardVariants}
              className="flex items-center justify-between text-sm"
            >
              <div className="flex items-center gap-2 text-muted-foreground">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                {system.name}
              </div>
              <span className="text-emerald-500 font-medium">{system.status}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  )
}
