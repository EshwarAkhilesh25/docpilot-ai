# Application Constants
APP_NAME = "DocMind API"
API_V1_PREFIX = "/api/v1"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# File Upload
MAX_FILE_SIZE_MB = 50
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

# AI Processing
MAX_CONTEXT_LENGTH = 4096
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Response Messages
MSG_SUCCESS = "Operation completed successfully"
MSG_CREATED = "Resource created successfully"
MSG_UPDATED = "Resource updated successfully"
MSG_DELETED = "Resource deleted successfully"
MSG_NOT_FOUND = "Resource not found"
MSG_BAD_REQUEST = "Invalid request"
MSG_UNAUTHORIZED = "Authentication required"
MSG_FORBIDDEN = "Access denied"
MSG_CONFLICT = "Resource already exists"
MSG_SERVER_ERROR = "Internal server error"

# Headers
HEADER_AUTHORIZATION = "Authorization"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_ACCEPT = "Accept"

# Bearer Token
BEARER_PREFIX = "Bearer"
