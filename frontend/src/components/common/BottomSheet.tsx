import { ReactNode } from "react";
import { Drawer } from "vaul";
import { cn } from "@lib/utils";

interface BottomSheetProps {
  trigger?: ReactNode;
  children: ReactNode;
  title?: string;
  description?: string;
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  className?: string;
}

export function BottomSheet({
  trigger,
  children,
  title,
  description,
  isOpen,
  onOpenChange,
  className,
}: BottomSheetProps) {
  return (
    <Drawer.Root open={isOpen} onOpenChange={onOpenChange}>
      {trigger && <Drawer.Trigger asChild>{trigger}</Drawer.Trigger>}

      <Drawer.Portal>
        <Drawer.Overlay className="fixed inset-0 bg-black/40 z-50 transition-opacity" />
        <Drawer.Content
          className={cn(
            // Mobile (Bottom Sheet)
            "bg-background border-t border-border flex flex-col rounded-t-[20px] mt-24 fixed bottom-0 left-0 right-0 z-50",
            "outline-none before:absolute before:top-3 before:left-1/2 before:-translate-x-1/2 before:w-12 before:h-1.5 before:bg-muted before:rounded-full before:z-10",
            // Desktop (Centered Modal)
            "md:bottom-auto md:top-1/2 md:-translate-y-1/2 md:left-1/2 md:-translate-x-1/2 md:w-full md:max-w-md md:rounded-xl md:border md:before:hidden md:mt-0",
            className,
          )}
        >
          <div className="p-4 sm:p-6 bg-background rounded-t-[20px] md:rounded-xl flex-1">
            <div className="max-w-md mx-auto w-full">
              {(title || description) && (
                <div className="mb-4 text-center mt-4">
                  {title && (
                    <Drawer.Title className="text-lg font-semibold text-foreground">
                      {title}
                    </Drawer.Title>
                  )}
                  {description && (
                    <Drawer.Description className="text-sm text-muted-foreground mt-1">
                      {description}
                    </Drawer.Description>
                  )}
                </div>
              )}
              {children}
            </div>
          </div>
        </Drawer.Content>
      </Drawer.Portal>
    </Drawer.Root>
  );
}
