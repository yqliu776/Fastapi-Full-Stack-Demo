from fastapi.security import OAuth2PasswordBearer

from .auth_service import AuthService
from .rbac_service import RbacService
from .session_service import SessionService, session_service

# OAuth2密码流认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/oauth")

__all__ = [
    "AuthService",
    "RbacService",
    "SessionService",
    "session_service",
    "oauth2_scheme"
]


