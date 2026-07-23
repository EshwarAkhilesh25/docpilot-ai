// API Configuration
const apiOrigin = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";

export const API_CONFIG = {
  // Use Vite proxy in dev when VITE_API_BASE_URL is unset; otherwise hit backend directly.
  BASE_URL: apiOrigin ? `${apiOrigin}/api/v1` : "/api/v1",
  TIMEOUT: 30000,
};

// Routes
export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/dashboard",
  DOCUMENTS: "/documents",
  UPLOAD: "/upload",
  CHAT: "/chat",
  CONVERSATIONS: "/conversations",
  SETTINGS: "/settings",
} as const;

// Animation Durations (ms)
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 200,
  SLOW: 300,
  VERY_SLOW: 500,
} as const;

// Layout Dimensions
export const LAYOUT = {
  SIDEBAR_WIDTH: 256, // 16rem
  HEADER_HEIGHT: 64, // 4rem
  CONTAINER_MAX_WIDTH: 1400,
} as const;

// Breakpoints (px)
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  "2XL": 1400,
} as const;

// Z-Index Values
export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
} as const;

// Storage Keys
export const STORAGE_KEYS = {
  THEME: "docmind-theme",
} as const;

// Upload Configuration
export const UPLOAD_CONFIG = {
  ALLOWED_EXTENSIONS: [".pdf", ".docx", ".mp3", ".wav", ".mp4"] as const,
  MAX_FILE_SIZE: 50 * 1024 * 1024, // 50 MB
  POLLING_INTERVAL: 3000, // 3 seconds
  MAX_CONCURRENT_UPLOADS: 3,
} as const;
