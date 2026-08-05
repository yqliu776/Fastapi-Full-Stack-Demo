from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm.attributes import set_committed_value
from typing import Optional, List

from app.modules.models import SysMenu, SysRole, SysRoleMenu, SysUserRole
from .base_repository import BaseRepository


class MenuRepository(BaseRepository[SysMenu]):
    """
    菜单仓储类，提供菜单相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化菜单仓储"""
        super().__init__(db_session, SysMenu)
    
    async def get_by_menu_code(self, menu_code: str) -> Optional[SysMenu]:
        """
        通过菜单代码获取菜单
        
        Args:
            menu_code: 菜单代码
            
        Returns:
            菜单模型实例或None
        """
        query = select(SysMenu).where(
            and_(
                SysMenu.menu_code == menu_code,
                SysMenu.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_menu_with_roles(self, menu_id: int) -> Optional[SysMenu]:
        """
        获取菜单及其角色信息
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            包含角色关联的菜单模型实例或None
        """
        query = select(SysMenu).where(
            and_(
                SysMenu.id == menu_id,
                SysMenu.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        menu = result.scalar_one_or_none()
        
        if menu:
            roles_query = (
                select(SysRole)
                .join(SysRoleMenu, SysRoleMenu.role_id == SysRole.id)
                .where(
                    and_(
                        SysRoleMenu.menu_id == menu_id,
                        SysRoleMenu.delete_flag == 'N',
                        SysRole.delete_flag == 'N'
                    )
                )
                .order_by(SysRole.id)
            )
            roles_result = await self.db.execute(roles_query)
            set_committed_value(menu, "roles", list(roles_result.scalars().all()))
            
        return menu
    
    async def get_menu_tree(self) -> List[SysMenu]:
        """
        获取所有菜单，按照树形结构排序
        
        Returns:
            菜单模型实例列表，顶级菜单在前
        """
        query = select(SysMenu).where(
            SysMenu.delete_flag == 'N'
        ).order_by(
            # MySQL不支持nulls_first()语法，使用CASE表达式来实现相同功能
            SysMenu.parent_id.is_(None).desc(),
            SysMenu.parent_id,
            SysMenu.sort_order
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_menus_by_parent_id(self, parent_id: Optional[int] = None) -> List[SysMenu]:
        """
        获取指定父菜单下的所有子菜单
        
        Args:
            parent_id: 父菜单ID，如果为None则获取所有顶级菜单
            
        Returns:
            菜单模型实例列表
        """
        if parent_id is None:
            query = select(SysMenu).where(
                and_(
                    SysMenu.parent_id.is_(None),
                    SysMenu.delete_flag == 'N'
                )
            ).order_by(SysMenu.sort_order)
        else:
            query = select(SysMenu).where(
                and_(
                    SysMenu.parent_id == parent_id,
                    SysMenu.delete_flag == 'N'
                )
            ).order_by(SysMenu.sort_order)
            
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def check_menu_code_exists(self, menu_code: str) -> bool:
        """
        检查菜单代码是否已存在
         
        Args:
            menu_code: 菜单代码
             
        Returns:
            如果存在返回True，否则返回False
        """
        query = select(SysMenu.id).where(
            and_(
                SysMenu.menu_code == menu_code,
                SysMenu.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_menus_by_filter(
        self,
        skip: int = 0,
        limit: int = 100,
        menu_name: Optional[str] = None,
        deleted: Optional[bool] = False
    ) -> List[SysMenu]:
        """
        根据过滤条件获取菜单列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            menu_name: 菜单名称过滤条件
            deleted: 删除状态过滤，False仅正常(N)，True仅已删除(Y)，None不过滤
            
        Returns:
            菜单模型实例列表
        """
        filters = []
        
        if menu_name:
            filters.append(SysMenu.menu_name.like(f"%{menu_name}%"))
            
        return await self.get_multi(skip=skip, limit=limit, filters=filters, deleted=deleted)

    async def _collect_descendant_ids(self, menu_id: int) -> List[int]:
        """收集菜单自身及其所有子孙菜单ID，子孙在前（便于级联删除）。"""
        order: List[int] = []

        async def collect(mid: int) -> None:
            children_result = await self.db.execute(
                select(SysMenu.id).where(SysMenu.parent_id == mid)
            )
            for child_id in children_result.scalars().all():
                await collect(child_id)
            order.append(mid)

        await collect(menu_id)
        return order

    async def purge(self, *, id_: int) -> Optional[SysMenu]:
        """彻底删除菜单及其所有子孙菜单，同时清理角色-菜单关联记录。"""
        ids = await self._collect_descendant_ids(id_)
        if not ids:
            return None

        fetch = select(SysMenu).where(SysMenu.id == id_)
        obj = (await self.db.execute(fetch)).scalar_one_or_none()
        if not obj:
            return None

        await self.db.execute(
            delete(SysRoleMenu).where(SysRoleMenu.menu_id.in_(ids))
        )
        # 子孙在前，逐条物理删除以满足自引用约束
        for menu_id in ids:
            await self.db.execute(
                delete(SysMenu).where(SysMenu.id == menu_id)
            )
        await self.db.commit()
        return obj
    
    async def get_menus_by_role_id(self, role_id: int) -> List[SysMenu]:
        """
        获取角色拥有的所有菜单
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单模型实例列表
        """
        from sqlalchemy import join
        
        # 使用JOIN查询角色的菜单
        query = select(SysMenu).select_from(
            join(
                SysMenu,
                SysRoleMenu,
                SysMenu.id == SysRoleMenu.menu_id
            )
        ).where(
            and_(
                SysRoleMenu.role_id == role_id,
                SysRoleMenu.delete_flag == 'N',
                SysMenu.delete_flag == 'N'
            )
        ).order_by(
            # MySQL不支持nulls_first()语法，使用CASE表达式来实现相同功能
            # 如果parent_id为NULL, 则排在前面
            SysMenu.parent_id.is_(None).desc(),
            SysMenu.parent_id,
            SysMenu.sort_order
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_menus_by_user_id(self, user_id: int) -> List[SysMenu]:
        """
        获取当前用户通过角色拥有的所有菜单。

        Args:
            user_id: 用户ID

        Returns:
            菜单模型实例列表
        """
        super_admin_query = (
            select(SysRole.id)
            .join(SysUserRole, SysUserRole.role_id == SysRole.id)
            .where(
                and_(
                    SysUserRole.user_id == user_id,
                    SysUserRole.delete_flag == 'N',
                    SysRole.role_code == 'ROLE_SUPER_ADMIN',
                    SysRole.delete_flag == 'N'
                )
            )
        )
        super_admin_result = await self.db.execute(super_admin_query)
        if super_admin_result.scalar_one_or_none() is not None:
            return await self.get_menu_tree()

        query = (
            select(SysMenu)
            .distinct()
            .join(SysRoleMenu, SysMenu.id == SysRoleMenu.menu_id)
            .join(SysRole, SysRole.id == SysRoleMenu.role_id)
            .join(SysUserRole, SysUserRole.role_id == SysRole.id)
            .where(
                and_(
                    SysUserRole.user_id == user_id,
                    SysUserRole.delete_flag == 'N',
                    SysRole.delete_flag == 'N',
                    SysRoleMenu.delete_flag == 'N',
                    SysMenu.delete_flag == 'N'
                )
            )
            .order_by(
                SysMenu.parent_id.is_(None).desc(),
                SysMenu.parent_id,
                SysMenu.sort_order
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
