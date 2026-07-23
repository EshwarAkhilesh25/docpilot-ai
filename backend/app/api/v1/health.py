from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.migration_verification import MigrationVerifier

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    pass
    return {
        "status": "healthy",
        "service": "DocMind API",
        "version": settings.APP_VERSION,
    }


@router.get("/health/detailed")
async def detailed_health_check(request: Request):
    """Detailed infrastructure health check.

    Reports only infrastructure readiness status without exposing sensitive information.
    """
    pass

    import typing

    health_status: dict[str, typing.Any] = {
        "status": "healthy",
        "service": "DocMind API",
        "version": settings.APP_VERSION,
        "components": {
            "database": {
                "status": "unknown",
            },
            "storage": {
                "status": "unknown",
            },
            "vector_index": {
                "status": "unknown",
            },
            "providers": {
                "llm": "not_configured",
                "transcription": "not_configured",
            },
        },
    }

    # Check database migration status
    try:
        verifier = MigrationVerifier()
        migration_status = verifier.verify_migrations()

        if migration_status["error"]:
            if "unreachable" in migration_status["error"].lower():
                health_status["components"]["database"]["status"] = "unhealthy"
                health_status["status"] = "degraded"
            else:
                health_status["components"]["database"]["status"] = "warning"
                health_status["status"] = "degraded"
        else:
            health_status["components"]["database"]["status"] = "healthy"
            health_status["components"]["database"]["migration_status"] = (
                "up_to_date" if migration_status["is_up_to_date"] else "pending"
            )

            if migration_status["has_pending_migrations"]:
                health_status["status"] = "degraded"

    except Exception:
        pass
        health_status["components"]["database"]["status"] = "unhealthy"
        health_status["status"] = "unhealthy"

    # Check storage directory availability
    try:
        from pathlib import Path

        storage_path = Path(settings.STORAGE_PATH)
        if storage_path.exists() and storage_path.is_dir():
            health_status["components"]["storage"]["status"] = "healthy"
        else:
            health_status["components"]["storage"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception:
        pass
        health_status["components"]["storage"]["status"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check vector index directory availability
    try:
        from pathlib import Path

        faiss_path = Path(settings.FAISS_INDEX_PATH)
        if faiss_path.exists() and faiss_path.is_dir():
            health_status["components"]["vector_index"]["status"] = "healthy"
        else:
            health_status["components"]["vector_index"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception:
        pass
        health_status["components"]["vector_index"]["status"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check optional provider configuration
    if settings.GROQ_API_KEY:
        health_status["components"]["providers"]["llm"] = "configured"
        health_status["components"]["providers"]["transcription"] = "configured"

    # Check if bootstrap has provider factories registered (metadata only, no instantiation)
    if hasattr(request.app.state, "bootstrap"):
        bootstrap = request.app.state.bootstrap
        # Use has() to check registration without triggering instantiation
        if bootstrap._provider_registry.has("llm"):
            health_status["components"]["providers"]["llm"] = "available"
        if bootstrap._provider_registry.has("transcription"):
            health_status["components"]["providers"]["transcription"] = "available"
        if bootstrap._provider_registry.has("embedding"):
            health_status["components"]["providers"]["embedding"] = "available"
        if bootstrap._provider_registry.has("storage"):
            health_status["components"]["providers"]["storage"] = "available"
        if bootstrap._provider_registry.has("vector_index"):
            health_status["components"]["providers"]["vector_index"] = "available"
        if bootstrap._provider_registry.has("keyword_index"):
            health_status["components"]["providers"]["keyword_index"] = "available"

    return health_status
