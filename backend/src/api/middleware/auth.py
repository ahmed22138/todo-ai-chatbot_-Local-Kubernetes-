"""Authentication middleware for FastAPI."""

import os
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.middleware.base import BaseHTTPMiddleware

from src.db.connection import async_session
from src.models.user import User
from src.services.auth_service import (
    AuthError,
    InvalidTokenError,
    TokenExpiredError,
    validate_bearer_token,
)

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens and attach user_id to request state.

    This middleware:
    1. Extracts Authorization header from requests
    2. Validates JWT token using Better Auth integration
    3. Attaches user_id to request.state for downstream handlers
    4. Returns 401 for invalid/expired tokens
    5. Returns 403 for missing tokens on protected routes

    Public routes (no auth required):
    - / (root - for health checks)
    - /health
    - /api/health
    - /api/auth/* (signup, login)
    - /docs
    - /redoc
    - /openapi.json
    """

    PUBLIC_PATHS = {"/", "/health", "/api/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication."""
        # Skip auth for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Skip auth for /api/auth/* endpoints (signup, login)
        if request.url.path.startswith("/api/auth/"):
            return await call_next(request)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Extract Authorization header
        authorization: Optional[str] = request.headers.get("Authorization")

        try:
            # Validate token and extract user_id
            user_id: UUID = validate_bearer_token(authorization)

            # DEVELOPMENT MODE: Auto-create user if doesn't exist
            environment = os.getenv("ENVIRONMENT", "production")
            if environment == "development" and authorization and "dev-token-" in authorization:
                async with async_session() as session:
                    # Check if user exists
                    result = await session.execute(
                        select(User).where(User.id == user_id)
                    )
                    user = result.scalar_one_or_none()

                    if not user:
                        # Create dev user
                        user = User(
                            id=user_id,
                            email=f"dev-user-{user_id}@example.com",
                            name=f"Dev User",
                        )
                        session.add(user)
                        await session.commit()

            # Attach user_id to request state for route handlers
            request.state.user_id = user_id

            # Continue to next middleware/route handler
            response = await call_next(request)
            return response

        except TokenExpiredError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Token expired", "message": str(e)},
                headers={"WWW-Authenticate": "Bearer"},
            )

        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid token", "message": str(e)},
                headers={"WWW-Authenticate": "Bearer"},
            )

        except AuthError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Authentication failed", "message": str(e)},
            )


async def get_current_user_id(request: Request) -> UUID:
    """Dependency to get current user_id from request state.

    Args:
        request: FastAPI request object with user_id in state.

    Returns:
        UUID: Current authenticated user's ID.

    Raises:
        HTTPException: 401 if user_id not found in request state.

    Example:
        @app.get("/me")
        async def get_me(user_id: UUID = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Not authenticated", "message": "User ID not found in request"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
