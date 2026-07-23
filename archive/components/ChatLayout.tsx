import { ReactNode, useState } from 'react'
import { Menu, X } from 'lucide-react'
import { cn } from '@lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ROUTES } from '@lib/constants'
import { ThemeToggle } from '../common/ThemeToggle'

interface ChatLayoutProps {
  children: ReactNode
}

export const ChatLayout = ({ children }: ChatLayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-[100dvh] bg-background flex flex-col w-full overflow-hidden">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-[40]">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 -ml-2 rounded-md hover:bg-muted text-foreground focus:outline-none"
            >
              <Menu className="w-5 h-5" />
            </button>
            <Link to={ROUTES.DASHBOARD} className="text-xl font-bold gradient-text">DocPilot AI</Link>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex overflow-hidden relative">
        
        {/* Backdrop for Mobile Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm z-[45] lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}
        </AnimatePresence>

        {/* Sidebar for conversations */}
        <aside className={cn(
          "fixed inset-y-0 left-0 bg-card border-r border-border flex flex-col z-[50] lg:relative lg:z-auto transition-transform duration-300 ease-in-out w-[280px] sm:w-80",
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}>
          <div className="p-4 flex items-center justify-between lg:hidden border-b border-border">
            <h2 className="text-sm font-semibold text-foreground">AI Conversations</h2>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="p-1 rounded hover:bg-muted text-muted-foreground"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="p-4 hidden lg:block">
            <h2 className="text-sm font-semibold text-muted-foreground">Conversations</h2>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
            {/* Conversation list will be added here */}
          </div>
        </aside>

        {/* Chat area */}
        <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
          {children}
        </div>
      </main>
    </div>
  )
}
