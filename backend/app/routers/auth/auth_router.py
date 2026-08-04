from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from typing import Optional
import time

from app.modules.schemas import TokenResponse, LoginRequest, UserDetail
from app.services import AuthService, oauth2_scheme
from app.core.models import ResponseModel
from app.core.settings import settings

router = APIRouter(prefix="/auth", tags=["认证"])

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends()
) -> UserDetail:
    """
    获取当前登录用户信息
    
    Args:
        token: JWT令牌
        auth_service: 认证服务实例
        
    Returns:
        UserDetail: 用户详细信息
    
    Raises:
        HTTPException: 令牌无效或过期时抛出异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的身份凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        
        jti = payload.get("jti")
        if jti:
            blacklisted = await auth_service.redis_util.get(f"token_blacklist:{jti}")
            if blacklisted is not None:
                raise credentials_exception
        
        user_id: Optional[int] = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
        # 获取用户详细信息
        user = await auth_service.user_repository.get_user_with_roles(user_id)
        if user is None:
            raise credentials_exception
            
        # 转换为UserDetail响应模型
        return UserDetail(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            creation_date=user.creation_date,
            last_update_date=user.last_update_date,
            roles=[{"role_name": role.role_name, "role_code": role.role_code} for role in user.roles]
        )
    except JWTError:
        raise credentials_exception

@router.post("/login", response_model=ResponseModel, summary="用户登录")
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    用户登录接口
    
    Args:
        login_data: 登录请求数据
        auth_service: 认证服务实例
        
    Returns:
        ResponseModel: 包含访问令牌的响应
    """
    start_time = time.time()
    token = await auth_service.login(login_data)
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=token,
        message="登录成功",
        process_time=process_time
    )

@router.post("/login/oauth", response_model=ResponseModel, summary="OAuth2密码模式登录")
async def oauth_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    OAuth2密码模式登录接口
    
    Args:
        form_data: OAuth2表单数据
        auth_service: 认证服务实例
        
    Returns:
        ResponseModel: 包含访问令牌的响应
    """
    start_time = time.time()
    login_data = LoginRequest(
        username=form_data.username,
        password=form_data.password
    )
    token = await auth_service.login(login_data)
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=token,
        message="登录成功",
        process_time=process_time
    )

@router.get("/me", response_model=ResponseModel, summary="获取当前用户信息")
async def get_user_info(current_user: UserDetail = Depends(get_current_user)) -> ResponseModel:
    """
    获取当前登录用户信息
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        ResponseModel: 用户详细信息
    """
    start_time = time.time()
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=current_user,
        message="获取用户信息成功",
        process_time=process_time
    )

@router.post("/logout", response_model=ResponseModel, summary="用户登出")
async def logout(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    用户登出接口。

    将当前访问令牌加入 Redis 黑名单，使该令牌在过期前不再可用；如果令牌已经无效，
    仍会清理前端登录状态并返回登出成功。

    Args:
        token: 当前请求携带的 Bearer Token。
        auth_service: 认证服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 为 None，message 为登出结果。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            import time
            remaining = max(int(exp - time.time()), 0)
            if remaining > 0:
                redis_util = auth_service.redis_util
                await redis_util.set(f"token_blacklist:{jti}", "1", ex=remaining)
    except JWTError:
        pass
    return ResponseModel.success(data=None, message="登出成功")


@router.post("/refresh", response_model=ResponseModel, summary="刷新访问令牌")
async def refresh_token(
    fresh_token: str = Body(..., embed=True, alias="refresh_token"),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    刷新访问令牌
    
    Args:
        fresh_token: 刷新令牌
        auth_service: 认证服务实例
        
    Returns:
        ResponseModel: 包含新访问令牌的响应
    """
    start_time = time.time()
    token = await auth_service.refresh_token(fresh_token)
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=token,
        message="令牌刷新成功",
        process_time=process_time
    )




