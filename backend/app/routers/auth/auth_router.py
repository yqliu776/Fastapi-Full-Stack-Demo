from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.schemas import TokenResponse, LoginRequest
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends()
) -> TokenResponse:
    """
    用户登录接口
    
    Args:
        login_data: 登录请求数据
        auth_service: 认证服务实例
        
    Returns:
        TokenResponse: 包含访问令牌的响应
    """
    return await auth_service.login(login_data)

@router.post("/login/oauth", response_model=TokenResponse)
async def oauth_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
) -> TokenResponse:
    """
    OAuth2密码模式登录接口
    
    Args:
        form_data: OAuth2表单数据
        auth_service: 认证服务实例
        
    Returns:
        TokenResponse: 包含访问令牌的响应
    """
    login_data = LoginRequest(
        username=form_data.username,
        password=form_data.password
    )
    return await auth_service.login(login_data)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends()
) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        auth_service: 认证服务实例
        
    Returns:
        TokenResponse: 包含新访问令牌的响应
    """
    return await auth_service.refresh_token(refresh_token)




