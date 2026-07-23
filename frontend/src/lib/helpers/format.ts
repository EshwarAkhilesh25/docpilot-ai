/**
 * Format file size in bytes to human-readable format
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (bytes == null || isNaN(bytes) || bytes < 0) return "";
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  // Safe bounds check for sizes array
  if (i < 0 || i >= sizes.length) return "";

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

/**
 * Format date string to relative time (e.g., "5m ago", "2h ago")
 */
export function formatTime(dateString: string | null | undefined): string {
  if (!dateString) return "Recently added";

  const date = new Date(dateString);
  if (isNaN(date.getTime())) return "Recently added";

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();

  // Handle future dates or slight clock skews
  if (diffMs < 0) return "Just uploaded";

  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just uploaded";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

export const formatRelativeTime = formatTime;
