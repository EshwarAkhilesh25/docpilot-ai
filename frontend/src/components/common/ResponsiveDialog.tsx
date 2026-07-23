import { ReactNode } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { Drawer } from "vaul";
import { useMediaQuery } from "@hooks/useMediaQuery";
import { X } from "lucide-react";
import { cn } from "@lib/utils";

interface ResponsiveDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  description?: string;
  trigger?: ReactNode;
  children: ReactNode;
  className?: string;
  footer?: ReactNode;
}

export function ResponsiveDialog({
  isOpen,
  onOpenChange,
  title,
  description,
  trigger,
  children,
  className,
  footer,
}: ResponsiveDialogProps) {
  const isDesktop = useMediaQuery("(min-width: 768px)");

  if (isDesktop) {
    return (
      <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
        {trigger && <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>}
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50 backdrop-blur-sm transition-opacity" />
          <Dialog.Content
            className={cn(
              "fixed left-1/2 top-1/2 z-50 flex w-full max-w-lg -translate-x-1/2 -translate-y-1/2 flex-col gap-4 border border-border bg-background p-6 shadow-2xl sm:rounded-xl",
              className,
            )}
          >
            <div className="flex items-start justify-between">
              <div>
                {title && (
                  <Dialog.Title className="text-lg font-semibold">
                    {title}
                  </Dialog.Title>
                )}
                {description && (
                  <Dialog.Description className="text-sm text-muted-foreground mt-1">
                    {description}
                  </Dialog.Description>
                )}
              </div>
              <Dialog.Close className="rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2">
                <X className="h-5 w-5" />
                <span className="sr-only">Close</span>
              </Dialog.Close>
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto">{children}</div>

            {footer && (
              <div className="mt-4 flex items-center justify-end border-t pt-4">
                {footer}
              </div>
            )}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    );
  }

  return (
    <Drawer.Root open={isOpen} onOpenChange={onOpenChange}>
      {trigger && <Drawer.Trigger asChild>{trigger}</Drawer.Trigger>}
      <Drawer.Portal>
        <Drawer.Overlay className="fixed inset-0 bg-black/50 z-50 transition-opacity" />
        <Drawer.Content
          className={cn(
            "bg-background border-t border-border flex flex-col rounded-t-[20px] fixed bottom-0 left-0 right-0 z-50",
            "outline-none before:absolute before:top-3 before:left-1/2 before:-translate-x-1/2 before:w-12 before:h-1.5 before:bg-muted before:rounded-full before:z-10",
            className,
          )}
        >
          <div className="flex flex-col max-h-[85vh] h-full">
            <div className="p-4 sm:p-6 pb-2 shrink-0 text-center mt-6">
              {title && (
                <Drawer.Title className="font-semibold text-lg">
                  {title}
                </Drawer.Title>
              )}
              {description && (
                <Drawer.Description className="text-sm text-muted-foreground mt-1">
                  {description}
                </Drawer.Description>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-4 sm:p-6 custom-scrollbar">
              {children}
            </div>

            {footer && (
              <div className="p-4 sm:p-6 border-t border-border bg-card pb-[max(1rem,env(safe-area-inset-bottom))] shrink-0">
                {footer}
              </div>
            )}
          </div>
        </Drawer.Content>
      </Drawer.Portal>
    </Drawer.Root>
  );
}
