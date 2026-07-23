import { memo } from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { useThemeStore } from "@store/themeStore";
import { cn } from "@lib/utils";

const themes = [
  { value: "light" as const, label: "Light", icon: Sun },
  { value: "dark" as const, label: "Dark", icon: Moon },
  { value: "system" as const, label: "System", icon: Monitor },
];

export const AppearanceSettings = memo(function AppearanceSettings() {
  const { theme, setTheme } = useThemeStore();

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        {themes.map((themeOption) => {
          const Icon = themeOption.icon;
          const isActive = theme === themeOption.value;

          return (
            <button
              key={themeOption.value}
              onClick={() => setTheme(themeOption.value)}
              className={cn(
                "touch-target flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all",
                "hover:border-primary/50",
                "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                isActive
                  ? "border-primary bg-primary/10"
                  : "border-border bg-card",
              )}
              aria-label={`Switch to ${themeOption.label} theme`}
              aria-pressed={isActive}
            >
              <Icon
                className={cn(
                  "w-6 h-6",
                  isActive ? "text-primary" : "text-muted-foreground",
                )}
              />
              <span
                className={cn(
                  "text-sm font-medium",
                  isActive ? "text-foreground" : "text-muted-foreground",
                )}
              >
                {themeOption.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
});
