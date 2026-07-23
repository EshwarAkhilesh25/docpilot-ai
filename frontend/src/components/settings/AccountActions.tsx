import { memo } from "react";
import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@lib/constants";
import { Button } from "@components/common/Button";
import { useAuthStore } from "@store/authStore";

export const AccountActions = memo(function AccountActions() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div
            className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center"
            aria-hidden="true"
          >
            <LogOut className="w-5 h-5 text-destructive" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-base font-semibold text-foreground mb-1">
            Logout
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            Sign out of your account and return to the login page.
          </p>
          <Button
            variant="destructive"
            onClick={handleLogout}
            className="touch-target w-full sm:w-auto"
          >
            <LogOut className="w-4 h-4 mr-2" aria-hidden="true" />
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
});
