import { memo } from "react";
import { User as UserIcon, Mail, Calendar } from "lucide-react";
import { User } from "@services/settingsService";
import { formatTime } from "@lib/helpers/format";

interface ProfileCardProps {
  user: User;
}

export const ProfileCard = memo(function ProfileCard({
  user,
}: ProfileCardProps) {
  return (
    <div
      className="flex items-start gap-4"
      role="region"
      aria-label="Profile information"
    >
      <div className="flex-shrink-0">
        <div
          className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center"
          aria-hidden="true"
        >
          <UserIcon className="w-8 h-8 text-primary" />
        </div>
      </div>
      <div className="flex-1 space-y-3">
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1 block">
            Full Name
          </label>
          <p
            className="text-base font-semibold text-foreground"
            aria-label={`Full name: ${user.full_name}`}
          >
            {user.full_name}
          </p>
        </div>
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1 block">
            Email Address
          </label>
          <div className="flex items-center gap-2">
            <Mail
              className="w-4 h-4 text-muted-foreground"
              aria-hidden="true"
            />
            <p
              className="text-sm text-foreground"
              aria-label={`Email address: ${user.email}`}
            >
              {user.email}
            </p>
          </div>
        </div>
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1 block">
            Account Created
          </label>
          <div className="flex items-center gap-2">
            <Calendar
              className="w-4 h-4 text-muted-foreground"
              aria-hidden="true"
            />
            <p
              className="text-sm text-foreground"
              aria-label={`Account created: ${formatTime(user.created_at)}`}
            >
              {formatTime(user.created_at)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
});
