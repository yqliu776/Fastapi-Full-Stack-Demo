from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from sqlalchemy import select, and_

from app.modules.models import SysPermission
from .base_repository import BaseRepository


class PermissionRepository(BaseRepository[SysPermission]):
    """
    权限仓储类，提供权限相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化权限仓储"""
        super().__init__(db_session, SysPermission)
    
    async def get_by_permission_code(self, permission_code: str) -> Optional[SysPermission]:
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
                SysPermission.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_permission_with_roles(self, permission_id: int) -> Optional[SysPermission]:
        """
        获取权限及其角色信息
        
        Args:
            permission_id: 权限ID
            
        Returns:
            包含角色关联的权限模型实例或None
        """
        query = select(SysPermission).where(
            and_(
                SysPermission.id == permission_id,
                SysPermission.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        permission = result.scalar_one_or_none()
        
        if permission:
            # 加载角色关系
            await self.db.refresh(permission, ["roles"])
            
        return permission
    
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
                SysPermission.delete_flag == 'N'
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
        
    async def get_permissions_by_role_id(self, role_id: int) -> List[SysPermission]:
        """
        获取角色拥有的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限模型实例列表
        """
        from sqlalchemy import join
        from app.modules.models.rbac_model import SysRolePermission
        
        # 使用JOIN查询角色的权限
        query = select(SysPermission).select_from(
            join(
                SysPermission,
                SysRolePermission,
                SysPermission.id == SysRolePermission.permission_id
            )
        ).where(
            and_(
                SysRolePermission.role_id == role_id,
                SysPermission.delete_flag == 'N'
            )
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all()) 