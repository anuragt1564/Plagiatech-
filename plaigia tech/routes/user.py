from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from auth import (
    fake_users_db, get_current_user, get_password_hash, 
    authenticate_user, create_access_token, UserInDB
)
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["user"])

# Models
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class User(UserBase):
    id: int
    is_premium: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UsageStats(BaseModel):
    total_checks: int
    remaining_free_checks: int
    is_premium: bool

# Routes
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, request: Request):
    """
    Register a new user.
    """
    logger.info(f"Registration attempt for username: {user.username}")
    
    if user.username in fake_users_db:
        logger.warning(f"Registration failed: Username {user.username} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    del user_dict["password"]
    user_dict["hashed_password"] = hashed_password
    user_dict["id"] = len(fake_users_db) + 1
    user_dict["created_at"] = datetime.utcnow()
    
    fake_users_db[user.username] = user_dict
    
    logger.info(f"User registered successfully: {user.username}")
    return {**user_dict, "id": user_dict["id"], "is_premium": False}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get access token for authentication.
    """
    logger.info(f"Login attempt for username: {form_data.username}")
    
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expire_time = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login time
    user_dict = fake_users_db[user.username]
    user_dict["last_login"] = datetime.utcnow()
    
    logger.info(f"Login successful for username: {form_data.username}")
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user information.
    """
    logger.info(f"User {current_user.username} accessed their profile")
    return current_user

@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(current_user: UserInDB = Depends(get_current_user)):
    """
    Get usage statistics for the current user.
    """
    usage_count = current_user.usage_count
    remaining = max(0, 10 - usage_count) if not current_user.is_premium else float('inf')
    
    return {
        "total_checks": usage_count,
        "remaining_free_checks": remaining,
        "is_premium": current_user.is_premium
    }

@router.post("/premium")
async def upgrade_to_premium(current_user: UserInDB = Depends(get_current_user)):
    """
    Upgrade user to premium status.
    """
    # In production, implement payment processing here
    logger.info(f"User {current_user.username} upgrading to premium")
    
    user_dict = fake_users_db[current_user.username]
    user_dict["is_premium"] = True
    
    logger.info(f"User {current_user.username} upgraded to premium successfully")
    return {"message": "Upgraded to premium successfully"}

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_user_history(current_user: UserInDB = Depends(get_current_user)):
    """
    Get history of user's plagiarism checks and rephrasing requests.
    """
    # In production, retrieve from database
    # For demonstration, return mock data
    logger.info(f"User {current_user.username} accessed their history")
    
    return [
        {
            "type": "plagiarism",
            "text": "Sample text for plagiarism check",
            "result": {"percentage": 10.5, "sources": ["https://example.com/source1"]},
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "type": "rephrase",
            "original": "Sample text for rephrasing",
            "rephrased": "Rephrased sample text",
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
