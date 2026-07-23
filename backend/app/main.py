from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.bootstrap import initialize_application, shutdown_application
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.session import engine
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_exception_handlers

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    pass

    # Initialize infrastructure
    try:
        bootstrap = await initialize_application()
        app.state.bootstrap = bootstrap
    except Exception:
        pass
        raise

    yield

    # Shutdown
    pass

    # Shutdown infrastructure
    try:
        await shutdown_application()
    except Exception:
        pass

    # Close database connections
    try:
        await engine.dispose()
        pass
    except Exception:
        pass


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Setup CORS first (must be before other middleware)
    setup_cors(app)
    setup_exception_handlers(app)

    app.include_router(api_router, prefix="/api/v1")

    # Add middleware to log all requests (after CORS)
    @app.middleware("http")
    async def log_requests(request, call_next):
        pass
        pass
        response = await call_next(request)
        pass
        pass
        return response

    pass

    return app


app = create_app()
