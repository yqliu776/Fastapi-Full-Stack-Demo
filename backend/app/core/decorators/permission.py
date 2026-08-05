from fastapi import Depends, HTTPException, Request, status
from typing import List, Optional, Callable
from functools import wraps
from jose import JWTError, jwt

from app.core.settings import settings
from app.services import AuthService, RbacService, oauth2_scheme


def _get_route_path_pattern(request: Request) -> str:
    route = request.scope.get("route")
    if route and getattr(route, "path", None):
        return route.path
    return request.url.path


def has_permission(required_permissions: List[str]):
    """
    权限验证装饰器，检查当前用户是否拥有所需权限
    
    Args:
        required_permissions: 所需的权限代码列表，用户拥有任意一个即可通过
    
    Returns:
        依赖函数，用于FastAPI路由的权限验证
    """
    
    async def permission_checker(
        request: Request,
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(),
        rbac_service: RbacService = Depends()
    ) -> bool:
        """
        检查用户权限
        
        Args:
            token: JWT令牌
            
        Returns:
            如果权限验证通过，返回True
            
        Raises:
            HTTPException: 权限验证失败时抛出异常
        """
        try:
            # 解析令牌
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # 检查token类型，只允许access token
            token_type = payload.get("type")
            if token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌类型",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            jti = payload.get("jti")
            if jti:
                blacklisted = await auth_service.redis_util.get(f"token_blacklist:{jti}")
                if blacklisted is not None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="无效的身份凭证",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            user_id = payload.get("user_id")
            if user_id is not None:
                role_codes = await auth_service.user_repository.get_active_role_codes(user_id)
                if "ROLE_SUPER_ADMIN" in role_codes:
                    return True
                permissions = await auth_service.get_permission_codes_for_user(user_id)
            else:
                role_codes = payload.get("roles") or []
                if "ROLE_SUPER_ADMIN" in role_codes:
                    return True
                permissions: Optional[List[str]] = payload.get("permissions") or []

            if not permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权限信息"
                )
            
            route_permission = await rbac_service.get_api_permission_for_route(
                request.method,
                _get_route_path_pattern(request)
            )
            effective_permissions = [route_permission] if route_permission else required_permissions

            # 如果没有配置API绑定，也没有要求任何权限，直接通过
            if not effective_permissions:
                return True
                
            if not any(permission in permissions for permission in effective_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您没有执行此操作的权限"
                )
                    
            return True
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的身份凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    return permission_checker
