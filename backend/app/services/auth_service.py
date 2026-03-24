from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join
from typing import Optional, Tuple
from jose import jwt, JWTError
from datetime import timedelta

from app.modules.repositories import UserRepository, PermissionRepository, RoleRepository
from app.core.utils import verify_password, create_access_token, create_refresh_token
from app.modules.models import SysUser, SysPermission, SysRolePermission
from app.modules.schemas import TokenResponse, LoginRequest, TokenData
from .session_service import session_service
from app.core.connects.database import db
from app.core.settings import settings
from app.core.utils import RedisUtil


class AuthService:
    """认证服务类"""
    
    def __init__(self, db_session: AsyncSession = Depends(db.get_db)):
        self.db = db_session
        self.user_repository = UserRepository(db_session)
        self.role_repository = RoleRepository(db_session)
        self.permission_repository = PermissionRepository(db_session)
        self.redis_util = RedisUtil()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[SysUser]:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[SysUser]: 验证成功返回用户对象，失败返回None
        """
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """
        用户登录
        
        Args:
            login_data: 登录请求数据
            
        Returns:
            TokenResponse: 包含访问令牌的响应
            
        Raises:
            HTTPException: 登录失败时抛出异常
        """
        # 检查是否被锁定
        lock_key = f"login_lock:{login_data.username}"
        fail_key = f"login_fail:{login_data.username}"
        locked = await self.redis_util.get(lock_key)
        if locked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="登录失败次数过多，账号已临时锁定，请15分钟后重试",
            )
        
        user = await self.authenticate_user(login_data.username, login_data.password)
        if not user:
            fail_count = await self.redis_util.get(fail_key)
            fail_count = int(fail_count) + 1 if fail_count else 1
            await self.redis_util.set(fail_key, fail_count, ex=900)
            if fail_count >= 5:
                await self.redis_util.set(lock_key, "1", ex=900)
                await self.redis_util.delete(fail_key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="登录失败次数过多，账号已临时锁定，请15分钟后重试",
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"用户名或密码错误，还可尝试{5 - fail_count}次",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        await self.redis_util.delete(fail_key)
        
        # 获取用户权限
        user_with_roles = await self.user_repository.get_user_with_roles(user.id)
        
        role_ids = [role.id for role in user_with_roles.roles]
        permissions = await self._get_permissions_for_roles(role_ids)
        
        token_data = {
            "user_id": user.id,
            "user_name": user.user_name,
            "permissions": list(set(permissions))
        }
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data=token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        # 创建用户会话
        user_data = {
            "user_id": user.id,
            "username": user.user_name,
            "permissions": token_data["permissions"],
            "roles": [role.role_code for role in user_with_roles.roles]
        }
        session_id = await session_service.create_session(
            user.id,
            user_data,
            expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
            session_id=session_id  # 添加会话ID到响应中
        )
    
    async def _get_permissions_for_roles(self, role_ids: list) -> list:
        """批量获取多个角色的权限代码列表，使用 Redis 缓存"""
        if not role_ids:
            return []
        
        all_codes = []
        uncached_role_ids = []
        
        for role_id in role_ids:
            cache_key = f"role_permissions:{role_id}"
            cached = await self.redis_util.get(cache_key)
            if cached is not None:
                all_codes.extend(cached)
            else:
                uncached_role_ids.append(role_id)
        
        if uncached_role_ids:
            query = select(
                SysRolePermission.role_id,
                SysPermission.permission_code
            ).select_from(
                join(
                    SysPermission,
                    SysRolePermission,
                    SysPermission.id == SysRolePermission.permission_id
                )
            ).where(SysRolePermission.role_id.in_(uncached_role_ids))
            
            result = await self.db.execute(query)
            rows = result.all()
            
            role_perm_map: dict = {}
            for role_id, perm_code in rows:
                role_perm_map.setdefault(role_id, []).append(perm_code)
                all_codes.append(perm_code)
            
            for role_id in uncached_role_ids:
                codes = role_perm_map.get(role_id, [])
                await self.redis_util.set(f"role_permissions:{role_id}", codes, ex=3600)
        
        return all_codes
    
    async def _invalidate_role_permissions_cache(self, role_id: int):
        """
        使角色权限缓存失效
        
        Args:
            role_id: 角色ID
        """
        cache_key = f"role_permissions:{role_id}"
        await self.redis_util.delete(cache_key)
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            TokenResponse: 新的访问令牌
            
        Raises:
            HTTPException: 刷新令牌无效或过期时抛出异常
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            
            token_type = payload.get("type")
            if token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌类型",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_id = payload.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 获取用户信息
            user = await self.user_repository.get_user_with_roles(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            role_ids = [role.id for role in user.roles]
            permissions = await self._get_permissions_for_roles(role_ids)
            
            token_data = {
                "user_id": user.id,
                "user_name": user.user_name,
                "permissions": list(set(permissions))
            }
            
            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            new_refresh_token = create_refresh_token(
                data=token_data,
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            
            # 更新用户会话
            user_data = {
                "user_id": user.id,
                "username": user.user_name,
                "permissions": token_data["permissions"],
                "roles": [role.role_code for role in user.roles]
            }
            session_id = await session_service.create_session(
                user.id,
                user_data,
                expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                session_id=session_id  # 添加session_id参数
            )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            ) 