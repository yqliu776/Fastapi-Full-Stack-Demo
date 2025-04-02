from fastapi.security import OAuth2PasswordBearer

from .auth_service import AuthService

# OAuth2密码流认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/oauth")

__all__ = [
    "AuthService",
    "oauth2_scheme"
]


