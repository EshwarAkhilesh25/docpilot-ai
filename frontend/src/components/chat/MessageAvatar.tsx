import { memo } from "react";
import { MessageRole } from "@services/chatService";
import { Bot, User } from "lucide-react";
import { cn } from "@lib/utils";

interface MessageAvatarProps {
  role: string;
}

export const MessageAvatar = memo(({ role }: MessageAvatarProps) => {
  const isUser = role === MessageRole.USER;

  return (
    <div
      className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser
          ? "bg-primary text-primary-foreground"
          : "bg-secondary text-secondary-foreground",
      )}
    >
      {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
    </div>
  );
});

MessageAvatar.displayName = "MessageAvatar";
