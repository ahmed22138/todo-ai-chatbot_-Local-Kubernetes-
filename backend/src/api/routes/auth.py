"""Authentication routes for signup and login."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.db.connection import async_session
from src.models.user import User
from src.services.auth_service import create_access_token

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


# Request/Response Models
class SignupRequest(BaseModel):
    """Signup request with email, password, and optional name."""

    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    name: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response with token and user info."""

    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: Optional[str] = None


# Password utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password from database.

    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """Create a new user account.

    Args:
        request: Signup request with email, password, and optional name.

    Returns:
        AuthResponse: JWT token and user information.

    Raises:
        HTTPException 400: If email already exists.
        HTTPException 422: If password is too short.
    """
    # Hash the password
    hashed_password = hash_password(request.password)

    # Create user
    user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed_password,
    )

    async with async_session() as session:
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Generate JWT token
    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        user_id=str(user.id),
        email=user.email,
        name=user.name,
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token.

    Args:
        request: Login request with email and password.

    Returns:
        AuthResponse: JWT token and user information.

    Raises:
        HTTPException 401: If email not found or password incorrect.
    """
    async with async_session() as session:
        # Find user by email
        result = await session.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()

        # Check if user exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

    # Generate JWT token
    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        user_id=str(user.id),
        email=user.email,
        name=user.name,
    )
