"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.study_helper.api.deps import get_db
from src.study_helper.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from src.study_helper.services.auth import register_user, authenticate_user
from src.study_helper.core.security import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (email, password, full_name)
        db: Database session
        
    Returns:
        TokenResponse with access_token and user data
        
    Raises:
        HTTPException 409: If email already exists
        HTTPException 422: If validation fails (handled by Pydantic)
    """
    try:
        # Register user with hashed password
        user = await register_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Generate JWT access token
        access_token = create_access_token(user_id=user.id)
        
        # Return token and user data
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
        
    except IntegrityError:
        # Email already exists (unique constraint violation)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return access token.
    
    Args:
        credentials: Login credentials (email, password)
        db: Database session
        
    Returns:
        TokenResponse with access_token and user data
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Authenticate user
    user = await authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate JWT access token
    access_token = create_access_token(user_id=user.id)
    
    # Return token and user data
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
