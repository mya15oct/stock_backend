from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from services.auth_service import AuthService
from db.auth_repo import AuthRepository

router = APIRouter()
auth_service = AuthService()

# --- Models ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class OAuthLogin(BaseModel):
    provider: str
    token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None

# --- Endpoints ---

from fastapi import BackgroundTasks

@router.post("/api/auth/register", tags=["Authentication"])
async def register(user: UserRegister, background_tasks: BackgroundTasks):
    """Register a new user."""
    return await auth_service.register_user(user.email, user.password, user.full_name, background_tasks)

@router.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password (multipart/form-data)."""
    return auth_service.login_user(form_data.username, form_data.password)

@router.post("/api/auth/oauth/login", response_model=Token, tags=["Authentication"])
async def oauth_login(data: OAuthLogin):
    """Login with verified OAuth token (Google/Facebook)."""
    return await auth_service.login_with_oauth(data.provider, data.token)

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendOTPRequest(BaseModel):
    email: EmailStr

@router.post("/api/auth/resend-otp", tags=["Authentication"])
async def resend_otp(data: ResendOTPRequest, background_tasks: BackgroundTasks):
    """Resend verification OTP."""
    return await auth_service.resend_verification_otp(data.email, background_tasks)

@router.post("/api/auth/verify-otp", response_model=Token, tags=["Authentication"])
async def verify_otp(data: VerifyOTPRequest):
    """Verify OTP and return Access Token (Auto Login)."""
    return auth_service.verify_user_otp(data.email, data.otp)

# @router.get("/api/auth/verify-email", tags=["Authentication"])
# async def verify_email(token: str):
#    ... (Deprecate or keep as legacy?) 
#    Actually, let's keep it but maybe it's unused in new UI. 
#    For cleanliness, I will comment it out or leave it if user wants fallback.
#    Since user specifically asked to CHANGE flow, I should probably prioritize the new one.
#    But to avoid breaking things too fast, I'll just add the new one.

@router.put("/api/auth/profile", tags=["Authentication"])
async def update_profile(
    updates: UserUpdate,
    current_user_id: str = "TODO: Extract from JWT Middleware" 
):
    """Update user profile."""
    # NOTE: Since Gateway handles auth, we expect user_id in headers or similar.
    # BUT, since we are implementing JWT in backend too (for generating it), 
    # we should also be able to validate it here if Gateway passes it through.
    # For MVP, we will assume user_id is passed in Header 'X-User-Id' by Gateway
    # OR we can implement a dependency to parse JWT again here. 
    # Given the plan says Gateway does Validation, Gateway should send 'X-User-Id'.
    
    # However, to test locally without Gateway first, let's allow a header override
    pass
    
    # We will implement this properly after checking how Gateway forwards user info.
    # For now, let's create the endpoint structure.
    return {"message": "Profile update endpoint - connects in next step"}
