"""FastAPI application entry point."""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from src.api.middleware import (
    AuthMiddleware,
    ErrorHandlerMiddleware,
    configure_cors,
)
from src.db import init_db
from src.db.connection import check_db_health

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("ENVIRONMENT") == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Validate required environment variables on startup
def validate_environment():
    """Validate required environment variables are set."""
    required_vars = {
        "DATABASE_URL": "PostgreSQL database connection string",
        "OPENAI_API_KEY": "OpenAI API key for agent functionality",
    }

    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"  - {var}: {description}")

    # Check for JWT_SECRET_KEY (with BETTER_AUTH_SECRET as fallback for backwards compatibility)
    auth_secret = os.getenv("JWT_SECRET_KEY") or os.getenv("BETTER_AUTH_SECRET", "")
    if not auth_secret:
        missing.append("  - JWT_SECRET_KEY or BETTER_AUTH_SECRET: Secret key for JWT token signing (min 32 chars)")

    if missing:
        error_msg = "Missing required environment variables:\n" + "\n".join(missing)
        error_msg += "\n\nPlease set these in your .env file or environment."
        logger.error(error_msg)
        sys.exit(1)

    # Validate JWT_SECRET_KEY length
    auth_secret = os.getenv("JWT_SECRET_KEY") or os.getenv("BETTER_AUTH_SECRET", "")
    if len(auth_secret) < 32:
        logger.error(
            "JWT_SECRET_KEY must be at least 32 characters long for security. "
            f"Current length: {len(auth_secret)}"
        )
        sys.exit(1)

    logger.info("✓ All required environment variables are set")


# Validate environment on module load
validate_environment()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Todo AI Chatbot API...")

    # Initialize database tables (for development only)
    # In production, use Alembic migrations instead
    if os.getenv("ENVIRONMENT") == "development":
        logger.info("Initializing database tables...")
        try:
            await init_db()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")

    # Check database health
    try:
        await check_db_health()
        logger.info("Database health check passed")
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")

    logger.info("Todo AI Chatbot API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Todo AI Chatbot API...")


# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot API",
    description="Natural language task management with AI-powered chatbot using MCP architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware (must be first)
configure_cors(app)

# Add error handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# Add authentication middleware
app.add_middleware(AuthMiddleware)


# Health check endpoint (public, no authentication)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint.

    Returns:
        dict: API status and database connectivity.
    """
    try:
        db_healthy = await check_db_health()
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "api": "operational",
                "database": "connected" if db_healthy else "disconnected",
            },
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "api": "operational",
                "database": "disconnected",
                "error": str(e),
            },
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information.

    Returns:
        dict: API welcome message and version.
    """
    return {
        "message": "Welcome to Todo AI Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
from src.api.routes import auth, chat, conversations

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info" if os.getenv("ENVIRONMENT") == "development" else "warning",
    )
