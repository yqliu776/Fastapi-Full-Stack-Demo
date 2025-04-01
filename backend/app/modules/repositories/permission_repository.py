from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.models.rbac_model import SysPermission, SysRole
from app.modules.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[SysPermission]):
    """
    权限仓储类，提供权限相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化权限仓储"""
        super().__init__(db_session, SysPermission)
    
    async def get_by_code(self, permission_code: str) -> Optional[SysPermission]:
        """
        通过权限代码获取权限
        
        Args:
            permission_code: 权限代码
            
        Returns:
            权限模型实例或None
        """
        query = select(SysPermission).where(
            and_(
                SysPermission.permission_code == permission_code,
                SysPermission.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_permissions_by_role(self, role_id: int) -> List[SysPermission]:
        """
        获取角色拥有的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限模型实例列表
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            return []
        
        # 加载角色权限关系
        await self.db.refresh(role, ["permissions"])
        return role.permissions
    
    async def get_permissions_by_role_code(self, role_code: str) -> List[SysPermission]:
        """
        通过角色代码获取所有权限
        
        Args:
            role_code: 角色代码
            
        Returns:
            权限模型实例列表
        """
        query = select(SysRole).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            return []
        
        # 加载角色权限关系
        await self.db.refresh(role, ["permissions"])
        return role.permissions
    
    async def check_permission_code_exists(self, permission_code: str) -> bool:
        """
        检查权限代码是否已存在
        
        Args:
            permission_code: 权限代码
            
        Returns:
            如果存在返回True，否则返回False
        """
        query = select(SysPermission.id).where(
            and_(
                SysPermission.permission_code == permission_code,
                SysPermission.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_permissions_by_filter(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        permission_name: Optional[str] = None,
        permission_code: Optional[str] = None
    ) -> List[SysPermission]:
        """
        根据过滤条件获取权限列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            permission_name: 权限名称过滤条件
            permission_code: 权限代码过滤条件
            
        Returns:
            权限模型实例列表
        """
        filters = []
        
        if permission_name:
            filters.append(SysPermission.permission_name.like(f"%{permission_name}%"))
            
        if permission_code:
            filters.append(SysPermission.permission_code.like(f"%{permission_code}%"))
            
        return await self.get_multi(skip=skip, limit=limit, filters=filters) 