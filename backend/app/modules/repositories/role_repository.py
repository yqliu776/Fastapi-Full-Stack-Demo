from typing import Optional, List

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.models.rbac_model import SysRole, SysPermission, SysMenu, SysRolePermission, SysRoleMenu
from app.modules.repositories.base_repository import BaseRepository
from app.core.utils.redis_util import RedisUtil


class RoleRepository(BaseRepository[SysRole]):
    """
    角色仓储类，提供角色相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化角色仓储"""
        super().__init__(db_session, SysRole)
        self.redis_util = RedisUtil()
    
    async def get_by_role_code(self, role_code: str) -> Optional[SysRole]:
        """
        通过角色代码获取角色
        
        Args:
            role_code: 角色代码
            
        Returns:
            角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_with_permissions(self, role_id: int) -> Optional[SysRole]:
        """
        获取角色及其权限信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            包含权限关联的角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if role:
            # 加载权限关系
            await self.db.refresh(role, ["permissions"])
            
        return role
    
    async def get_role_with_menus(self, role_id: int) -> Optional[SysRole]:
        """
        获取角色及其菜单信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            包含菜单关联的角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if role:
            # 加载菜单关系
            await self.db.refresh(role, ["menus"])
            
        return role
        
    async def get_role_with_all_relations(self, role_id: int) -> Optional[SysRole]:
        """
        获取角色及其所有关联信息（权限、菜单、用户）
        
        Args:
            role_id: 角色ID
            
        Returns:
            包含所有关联的角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if role:
            # 加载所有关联关系
            await self.db.refresh(role, ["permissions", "menus", "users"])
            
        return role
    
    async def check_role_code_exists(self, role_code: str) -> bool:
        """
        检查角色代码是否已存在
        
        Args:
            role_code: 角色代码
            
        Returns:
            如果存在返回True，否则返回False
        """
        query = select(SysRole.id).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def add_permissions_to_role(self, role_id: int, permission_ids: List[int], audit_info: dict) -> bool:
        """
        为角色添加权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            audit_info: 审计信息，包含创建人、最后更新人等
            
        Returns:
            添加成功返回True
        """
        # 首先检查角色是否存在
        role = await self.get(role_id)
        if not role:
            return False
            
        # 添加权限关联
        for permission_id in permission_ids:
            role_permission = SysRolePermission(
                role_id=role_id,
                permission_id=permission_id,
                **audit_info
            )
            self.db.add(role_permission)
            
        await self.db.commit()
        return True
    
    async def remove_permissions_from_role(self, role_id: int, permission_ids: List[int]) -> bool:
        """
        从角色移除权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            
        Returns:
            移除成功返回True
        """
        from sqlalchemy import delete as sql_delete
        
        # 删除指定的角色-权限关联
        delete_query = sql_delete(SysRolePermission).where(
            and_(
                SysRolePermission.role_id == role_id,
                SysRolePermission.permission_id.in_(permission_ids)
            )
        )
        
        await self.db.execute(delete_query)
        await self.db.commit()
        return True
    
    async def add_menus_to_role(self, role_id: int, menu_ids: List[int], audit_info: dict) -> bool:
        """
        为角色添加菜单
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            audit_info: 审计信息，包含创建人、最后更新人等
            
        Returns:
            添加成功返回True
        """
        # 首先检查角色是否存在
        role = await self.get(role_id)
        if not role:
            return False
            
        # 添加菜单关联
        for menu_id in menu_ids:
            role_menu = SysRoleMenu(
                role_id=role_id,
                menu_id=menu_id,
                **audit_info
            )
            self.db.add(role_menu)
            
        await self.db.commit()
        return True
    
    async def remove_menus_from_role(self, role_id: int, menu_ids: List[int]) -> bool:
        """
        从角色移除菜单
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            
        Returns:
            移除成功返回True
        """
        from sqlalchemy import delete as sql_delete
        
        # 删除指定的角色-菜单关联
        delete_query = sql_delete(SysRoleMenu).where(
            and_(
                SysRoleMenu.role_id == role_id,
                SysRoleMenu.menu_id.in_(menu_ids)
            )
        )
        
        await self.db.execute(delete_query)
        await self.db.commit()
        return True
    
    async def update_role_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """
        更新角色的权限列表
        
        Args:
            role_id: 角色ID
            permission_ids: 新的权限ID列表
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 删除现有权限关联
            await self.db.execute(
                delete(SysRolePermission).where(SysRolePermission.role_id == role_id)
            )
            
            # 添加新的权限关联
            for permission_id in permission_ids:
                role_permission = SysRolePermission(
                    role_id=role_id,
                    permission_id=permission_id
                )
                self.db.add(role_permission)
            
            await self.db.commit()
            
            # 使权限缓存失效
            await self.redis_util.delete(f"role_permissions:{role_id}")
            
            return True
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def delete_role(self, role_id: int) -> bool:
        """
        删除角色（软删除）
        
        Args:
            role_id: 角色ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            role = await self.get_by_id(role_id)
            if not role:
                return False
                
            role.delete_flag = 'Y'
            await self.db.commit()
            
            # 使权限缓存失效
            await self.redis_util.delete(f"role_permissions:{role_id}")
            
            return True
        except Exception as e:
            await self.db.rollback()
            raise e