import { useState, memo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, ChevronDown, Check, X } from 'lucide-react'
import { cn } from '@lib/utils'

export interface DocumentFilterOption {
  id: string
  original_filename: string
  file_type: string
}

interface DocumentFilterProps {
  documents: DocumentFilterOption[]
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  className?: string
}

export const DocumentFilter = memo(({ 
  documents, 
  selectedIds, 
  onSelectionChange,
  className 
}: DocumentFilterProps) => {
  const [isOpen, setIsOpen] = useState(false)

  const toggleDocument = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter(docId => docId !== id))
    } else {
      onSelectionChange([...selectedIds, id])
    }
  }

  const clearSelection = () => {
    onSelectionChange([])
  }

  const selectAll = () => {
    onSelectionChange(documents.map(doc => doc.id))
  }

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-muted rounded-lg hover:bg-muted/80 transition-colors text-sm"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <FileText className="w-4 h-4 text-muted-foreground" />
        <span className="flex-1 text-left">
          {selectedIds.length === 0
            ? 'All Documents'
            : `${selectedIds.length} document${selectedIds.length > 1 ? 's' : ''} selected`}
        </span>
        <ChevronDown className={cn('w-4 h-4 text-muted-foreground transition-transform', isOpen && 'rotate-180')} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 z-10"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full left-0 right-0 mt-2 bg-card border rounded-lg shadow-lg z-20 max-h-80 overflow-hidden"
            >
              <div className="p-2 border-b flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">
                  Select documents
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={selectAll}
                    className="text-xs px-2 py-1 hover:bg-muted rounded transition-colors"
                  >
                    All
                  </button>
                  <button
                    onClick={clearSelection}
                    className="text-xs px-2 py-1 hover:bg-muted rounded transition-colors"
                  >
                    Clear
                  </button>
                </div>
              </div>
              <div className="overflow-y-auto max-h-60 p-2 space-y-1" role="listbox">
                {documents.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => toggleDocument(doc.id)}
                    role="option"
                    aria-selected={selectedIds.includes(doc.id)}
                    className={cn(
                      'w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors text-sm text-left',
                      'hover:bg-muted',
                      selectedIds.includes(doc.id) && 'bg-primary/10'
                    )}
                  >
                    <div className={cn(
                      'w-4 h-4 rounded border flex items-center justify-center flex-shrink-0',
                      selectedIds.includes(doc.id)
                        ? 'bg-primary border-primary text-primary-foreground'
                        : 'border-border'
                    )}>
                      {selectedIds.includes(doc.id) && <Check className="w-3 h-3" />}
                    </div>
                    <FileText className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                    <span className="flex-1 truncate">{doc.original_filename}</span>
                    {selectedIds.includes(doc.id) && (
                      <X 
                        className="w-3 h-3 text-muted-foreground hover:text-foreground"
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleDocument(doc.id)
                        }}
                      />
                    )}
                  </button>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
})

DocumentFilter.displayName = 'DocumentFilter'
