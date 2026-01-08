"""Error handling middleware for FastAPI."""

import logging
import traceback
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logger
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to catch exceptions and return friendly JSON error responses.

    This middleware:
    1. Catches all unhandled exceptions
    2. Logs technical details for debugging
    3. Returns user-friendly error messages
    4. Prevents sensitive information leakage
    5. Maps common errors to appropriate HTTP status codes

    Error Response Format:
    {
        "error": "Error category",
        "message": "User-friendly message",
        "request_id": "optional-request-id"
    }
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and handle errors."""
        try:
            response = await call_next(request)
            return response

        except IntegrityError as e:
            # Database constraint violations (unique, foreign key, etc.)
            logger.error(f"Database integrity error: {str(e)}", exc_info=True)

            # Extract user-friendly message
            error_msg = self._get_integrity_error_message(e)

            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "Constraint violation",
                    "message": error_msg,
                },
            )

        except SQLAlchemyError as e:
            # Other database errors
            logger.error(f"Database error: {str(e)}", exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Database error",
                    "message": "We're having trouble accessing the database. Please try again in a moment.",
                },
            )

        except ValueError as e:
            # Invalid input values
            logger.warning(f"Validation error: {str(e)}")

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Invalid input",
                    "message": str(e),
                },
            )

        except PermissionError as e:
            # Permission/authorization errors
            logger.warning(f"Permission denied: {str(e)}")

            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Permission denied",
                    "message": "You don't have permission to perform this action.",
                },
            )

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(
                f"Unexpected error: {str(e)}\n{traceback.format_exc()}",
                exc_info=True,
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": "Oops! Something went wrong on our end. Our team has been notified and we're working on it.",
                },
            )

    @staticmethod
    def _get_integrity_error_message(error: IntegrityError) -> str:
        """Extract user-friendly message from IntegrityError.

        Args:
            error: SQLAlchemy IntegrityError.

        Returns:
            str: User-friendly error message.
        """
        error_str = str(error.orig).lower()

        if "unique" in error_str or "duplicate" in error_str:
            if "email" in error_str:
                return "This email address is already registered."
            return "This item already exists. Please use a different value."

        if "foreign key" in error_str or "violates foreign key" in error_str:
            if "user_id" in error_str:
                return "The user you're trying to reference doesn't exist."
            if "conversation_id" in error_str:
                return "The conversation you're trying to reference doesn't exist."
            return "The item you're trying to reference doesn't exist."

        if "not null" in error_str:
            return "A required field is missing. Please provide all necessary information."

        # Default message for unknown constraint violations
        return "We couldn't complete this action due to a data constraint. Please check your input and try again."
