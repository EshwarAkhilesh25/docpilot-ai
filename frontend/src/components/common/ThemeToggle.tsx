import { Moon, Sun } from "lucide-react";
import { useThemeStore } from "@store/themeStore";

export const ThemeToggle = () => {
  const { theme, setTheme } = useThemeStore();

  // Determine current effective theme
  const isDark =
    theme === "dark" ||
    (theme === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  const toggleTheme = () => {
    setTheme(isDark ? "light" : "dark");
  };

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-md hover:bg-muted text-foreground focus:outline-none transition-colors"
      aria-label="Toggle theme"
    >
      {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>
  );
};
