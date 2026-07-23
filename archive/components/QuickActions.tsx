import { motion } from 'framer-motion'
import { cardVariants, staggerContainer } from '@lib/animations'
import { Upload, MessageSquare, FileText, MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { ROUTES } from '@lib/constants'

interface QuickActionProps {
  title: string
  description: string
  icon: React.ReactNode
  onClick: () => void
}

function QuickAction({ title, description, icon, onClick }: QuickActionProps) {
  return (
    <motion.button
      variants={cardVariants}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="touch-target flex flex-col items-center justify-center text-center p-4 sm:p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-colors group h-full"
    >
      <div className="p-3 rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors mb-3">
        {icon}
      </div>
      <div>
        <h3 className="font-semibold text-sm sm:text-base text-foreground mb-1">{title}</h3>
        <p className="hidden sm:block text-xs text-muted-foreground">{description}</p>
      </div>
    </motion.button>
  )
}

export function QuickActions() {
  const navigate = useNavigate()

  const actions = [
    {
      title: 'Upload Document',
      description: 'Add a new document to your workspace',
      icon: <Upload className="h-5 w-5" />,
      onClick: () => navigate(ROUTES.UPLOAD),
    },
    {
      title: 'Start Chat',
      description: 'Ask questions about your documents',
      icon: <MessageSquare className="h-5 w-5" />,
      onClick: () => navigate(ROUTES.CHAT),
    },
    {
      title: 'Browse Documents',
      description: 'View and manage your documents',
      icon: <FileText className="h-5 w-5" />,
      onClick: () => navigate(ROUTES.DOCUMENTS),
    },
    {
      title: 'View Conversations',
      description: 'Review your chat history',
      icon: <MessageCircle className="h-5 w-5" />,
      onClick: () => navigate(ROUTES.CONVERSATIONS),
    },
  ]

  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="grid grid-cols-2 lg:grid-cols-4 gap-4"
    >
      {actions.map((action, index) => (
        <QuickAction
          key={index}
          title={action.title}
          description={action.description}
          icon={action.icon}
          onClick={action.onClick}
        />
      ))}
    </motion.div>
  )
}
