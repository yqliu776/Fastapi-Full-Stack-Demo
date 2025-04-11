from typing import List, Optional, Dict, Any, Tuple
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.schemas import PermissionCreate, PermissionUpdate, PermissionResponse, PermissionDetail, PermissionBatchResponse
from app.modules.schemas import MenuCreate, MenuUpdate, MenuResponse, MenuDetail, MenuTreeNode, MenuBatchResponse
from app.modules.schemas import RoleCreate, RoleUpdate, RoleResponse, RoleDetail, RoleBatchResponse
from app.modules.repositories import RoleRepository, MenuRepository, PermissionRepository
from app.modules.models import SysRole, SysPermission, SysMenu
from app.core.connects import db


class RBACService:
    """
    RBAC服务类，提供角色、权限和菜单的业务逻辑实现
    """
    
    def __init__(self, db_session: AsyncSession = Depends(db.get_db)):
        """初始化RBAC服务"""
        self.db = db_session
        self.role_repository = RoleRepository(db_session)
        self.permission_repository = PermissionRepository(db_session)
        self.menu_repository = MenuRepository(db_session)
    
    #========== 角色相关方法 ==========
    
    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        """
        创建角色
        
        Args:
            role_data: 角色创建数据
            
        Returns:
            创建后的角色响应
            
        Raises:
            HTTPException: 角色代码已存在时抛出异常
        """
        # 检查角色代码是否已存在
        exists = await self.role_repository.check_role_code_exists(role_data.role_code)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"角色代码 '{role_data.role_code}' 已存在"
            )
        
        # 创建角色
        role = await self.role_repository.create(role_data.model_dump())
        
        # 转换为响应模型
        return RoleResponse.model_validate(role)
    
    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleResponse:
        """
        更新角色
        
        Args:
            role_id: 角色ID
            role_data: 角色更新数据
            
        Returns:
            更新后的角色响应
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 更新角色
        updated_role = await self.role_repository.update(
            id_=role_id,
            obj_in=role_data.model_dump(exclude_unset=True)
        )
        
        # 转换为响应模型
        return RoleResponse.model_validate(updated_role)
    
    async def delete_role(self, role_id: int) -> bool:
        """
        删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            删除成功返回True
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 删除角色
        result = await self.role_repository.delete(id_=role_id)
        
        return result is not None
    
    async def get_role(self, role_id: int) -> RoleDetail:
        """
        获取角色详情
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色详情响应
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 获取角色及其所有关联
        role = await self.role_repository.get_role_with_all_relations(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
            
        # 先构建基本角色信息
        role_dict = {
            "id": role.id,
            "role_name": role.role_name,
            "role_code": role.role_code,
            "creation_date": role.creation_date,
            "last_update_date": role.last_update_date,
            "success": True,
            "message": "获取角色详情成功"
        }
        
        # 转换权限列表
        permissions_list = []
        if hasattr(role, "permissions") and role.permissions:
            for permission in role.permissions:
                # 确保每个权限都是字典格式
                permissions_list.append({
                    "id": permission.id,
                    "permission_name": permission.permission_name,
                    "permission_code": permission.permission_code
                })
        
        # 转换菜单列表
        menus_list = []
        if hasattr(role, "menus") and role.menus:
            for menu in role.menus:
                # 确保每个菜单都是字典格式
                menus_list.append({
                    "id": menu.id,
                    "menu_name": menu.menu_name,
                    "menu_code": menu.menu_code,
                    "menu_path": menu.menu_path if hasattr(menu, "menu_path") else None
                })
        
        # 构建完整的角色详情响应
        role_dict["permissions"] = permissions_list
        role_dict["menus"] = menus_list
        
        # 使用字典直接创建RoleDetail模型
        return RoleDetail.model_validate(role_dict)
    
    async def get_all_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        role_name: Optional[str] = None,
        role_code: Optional[str] = None
    ) -> RoleBatchResponse:
        """
        获取角色列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            role_name: 角色名称过滤条件
            role_code: 角色代码过滤条件
            
        Returns:
            角色列表响应
        """
        # 构建过滤条件
        filters = []
        
        if role_name:
            filters.append(SysRole.role_name.like(f"%{role_name}%"))
            
        if role_code:
            filters.append(SysRole.role_code.like(f"%{role_code}%"))
        
        # 获取角色列表
        roles = await self.role_repository.get_multi(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        # 获取总记录数
        total = await self.role_repository.get_count(filters=filters)
        
        # 转换为响应模型
        return RoleBatchResponse(
            items=[RoleResponse.model_validate(role) for role in roles],
            total=total,
            success=True,
            message="获取角色列表成功"
        )
    
    async def add_permissions_to_role(
        self, 
        role_id: int, 
        permission_ids: List[int],
        audit_info: Dict[str, Any]
    ) -> bool:
        """
        为角色添加权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            audit_info: 审计信息
            
        Returns:
            添加成功返回True
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 添加权限
        result = await self.role_repository.add_permissions_to_role(
            role_id=role_id,
            permission_ids=permission_ids,
            audit_info=audit_info
        )
        
        return result
    
    async def remove_permissions_from_role(
        self, 
        role_id: int, 
        permission_ids: List[int]
    ) -> bool:
        """
        从角色移除权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            
        Returns:
            移除成功返回True
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 移除权限
        result = await self.role_repository.remove_permissions_from_role(
            role_id=role_id,
            permission_ids=permission_ids
        )
        
        return result
    
    async def add_menus_to_role(
        self, 
        role_id: int, 
        menu_ids: List[int],
        audit_info: Dict[str, Any]
    ) -> bool:
        """
        为角色添加菜单
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            audit_info: 审计信息
            
        Returns:
            添加成功返回True
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 添加菜单
        result = await self.role_repository.add_menus_to_role(
            role_id=role_id,
            menu_ids=menu_ids,
            audit_info=audit_info
        )
        
        return result
    
    async def remove_menus_from_role(
        self, 
        role_id: int, 
        menu_ids: List[int]
    ) -> bool:
        """
        从角色移除菜单
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            
        Returns:
            移除成功返回True
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 移除菜单
        result = await self.role_repository.remove_menus_from_role(
            role_id=role_id,
            menu_ids=menu_ids
        )
        
        return result
    
    #========== 权限相关方法 ==========
    
    async def create_permission(self, permission_data: PermissionCreate) -> PermissionResponse:
        """
        创建权限
        
        Args:
            permission_data: 权限创建数据
            
        Returns:
            创建后的权限响应
            
        Raises:
            HTTPException: 权限代码已存在时抛出异常
        """
        # 检查权限代码是否已存在
        exists = await self.permission_repository.check_permission_code_exists(permission_data.permission_code)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"权限代码 '{permission_data.permission_code}' 已存在"
            )
        
        # 创建权限
        permission = await self.permission_repository.create(permission_data.model_dump())
        
        # 转换为响应模型
        return PermissionResponse.model_validate(permission)
    
    async def update_permission(self, permission_id: int, permission_data: PermissionUpdate) -> PermissionResponse:
        """
        更新权限
        
        Args:
            permission_id: 权限ID
            permission_data: 权限更新数据
            
        Returns:
            更新后的权限响应
            
        Raises:
            HTTPException: 权限不存在时抛出异常
        """
        # 检查权限是否存在
        permission = await self.permission_repository.get(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"权限ID '{permission_id}' 不存在"
            )
        
        # 更新权限
        updated_permission = await self.permission_repository.update(
            id_=permission_id,
            obj_in=permission_data.model_dump(exclude_unset=True)
        )
        
        # 转换为响应模型
        return PermissionResponse.model_validate(updated_permission)
    
    async def delete_permission(self, permission_id: int) -> bool:
        """
        删除权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            删除成功返回True
            
        Raises:
            HTTPException: 权限不存在时抛出异常
        """
        # 检查权限是否存在
        permission = await self.permission_repository.get(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"权限ID '{permission_id}' 不存在"
            )
        
        # 删除权限
        result = await self.permission_repository.delete(id_=permission_id)
        
        return result is not None
    
    async def get_permission(self, permission_id: int) -> PermissionDetail:
        """
        获取权限详情
        
        Args:
            permission_id: 权限ID
            
        Returns:
            权限详情响应
            
        Raises:
            HTTPException: 权限不存在时抛出异常
        """
        # 获取权限及其所有关联
        permission = await self.permission_repository.get_permission_with_roles(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"权限ID '{permission_id}' 不存在"
            )
        
        # 构建权限基本信息
        permission_dict = {
            "id": permission.id,
            "permission_name": permission.permission_name,
            "permission_code": permission.permission_code,
            "creation_date": permission.creation_date,
            "last_update_date": permission.last_update_date,
            "success": True,
            "message": "获取权限详情成功"
        }
        
        # 转换角色列表
        roles_list = []
        if hasattr(permission, "roles") and permission.roles:
            for role in permission.roles:
                # 确保每个角色都是字典格式
                roles_list.append({
                    "id": role.id,
                    "role_name": role.role_name,
                    "role_code": role.role_code
                })
                
        # 构建完整的权限详情响应
        permission_dict["roles"] = roles_list
        
        # 使用字典直接创建PermissionDetail模型
        return PermissionDetail.model_validate(permission_dict)
    
    async def get_all_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
        permission_name: Optional[str] = None,
        permission_code: Optional[str] = None
    ) -> PermissionBatchResponse:
        """
        获取权限列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            permission_name: 权限名称过滤条件
            permission_code: 权限代码过滤条件
            
        Returns:
            权限列表响应
        """
        # 获取权限列表
        permissions = await self.permission_repository.get_permissions_by_filter(
            skip=skip,
            limit=limit,
            permission_name=permission_name,
            permission_code=permission_code
        )
        
        # 构建过滤条件
        filters = []
        
        if permission_name:
            filters.append(SysPermission.permission_name.like(f"%{permission_name}%"))
            
        if permission_code:
            filters.append(SysPermission.permission_code.like(f"%{permission_code}%"))
        
        # 获取总记录数
        total = await self.permission_repository.get_count(filters=filters)
        
        # 转换为响应模型
        return PermissionBatchResponse(
            items=[PermissionResponse.model_validate(permission) for permission in permissions],
            total=total,
            success=True,
            message="获取权限列表成功"
        )
    
    async def get_permissions_by_role_id(self, role_id: int) -> List[PermissionResponse]:
        """
        获取角色拥有的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限列表响应
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 获取角色权限
        permissions = await self.permission_repository.get_permissions_by_role_id(role_id)
        
        # 转换为响应模型
        permission_responses = []
        for permission in permissions:
            permission_dict = {
                "id": permission.id,
                "permission_name": permission.permission_name,
                "permission_code": permission.permission_code,
                "creation_date": permission.creation_date,
                "last_update_date": permission.last_update_date
            }
            permission_responses.append(PermissionResponse.model_validate(permission_dict))
            
        return permission_responses
    
    #========== 菜单相关方法 ==========
    
    async def create_menu(self, menu_data: MenuCreate) -> MenuResponse:
        """
        创建菜单
        
        Args:
            menu_data: 菜单创建数据
            
        Returns:
            创建后的菜单响应
            
        Raises:
            HTTPException: 菜单代码已存在时抛出异常
        """
        # 检查菜单代码是否已存在
        exists = await self.menu_repository.check_menu_code_exists(menu_data.menu_code)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"菜单代码 '{menu_data.menu_code}' 已存在"
            )
        
        # 检查父菜单是否存在
        if menu_data.parent_id is not None:
            parent = await self.menu_repository.get(menu_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"父菜单ID '{menu_data.parent_id}' 不存在"
                )
        
        # 创建菜单
        menu = await self.menu_repository.create(menu_data.model_dump())
        
        # 转换为响应模型
        return MenuResponse.model_validate(menu)
    
    async def update_menu(self, menu_id: int, menu_data: MenuUpdate) -> MenuResponse:
        """
        更新菜单
        
        Args:
            menu_id: 菜单ID
            menu_data: 菜单更新数据
            
        Returns:
            更新后的菜单响应
            
        Raises:
            HTTPException: 菜单不存在时抛出异常
        """
        # 检查菜单是否存在
        menu = await self.menu_repository.get(menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"菜单ID '{menu_id}' 不存在"
            )
        
        # 检查父菜单是否存在
        if menu_data.parent_id is not None:
            parent = await self.menu_repository.get(menu_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"父菜单ID '{menu_data.parent_id}' 不存在"
                )
            
            # 避免出现循环引用（将自己设为自己的父菜单）
            if menu_data.parent_id == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能将菜单自身设为父菜单"
                )
        
        # 更新菜单
        updated_menu = await self.menu_repository.update(
            id_=menu_id,
            obj_in=menu_data.model_dump(exclude_unset=True)
        )
        
        # 转换为响应模型
        return MenuResponse.model_validate(updated_menu)
    
    async def delete_menu(self, menu_id: int) -> bool:
        """
        删除菜单
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            删除成功返回True
            
        Raises:
            HTTPException: 菜单不存在时抛出异常
        """
        # 检查菜单是否存在
        menu = await self.menu_repository.get(menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"菜单ID '{menu_id}' 不存在"
            )
        
        # 检查是否有子菜单
        children = await self.menu_repository.get_menus_by_parent_id(menu_id)
        if children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="菜单存在子菜单，请先删除子菜单"
            )
        
        # 删除菜单
        result = await self.menu_repository.delete(id_=menu_id)
        
        return result is not None
    
    async def get_menu(self, menu_id: int) -> MenuDetail:
        """
        获取菜单详情
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            菜单详情响应
            
        Raises:
            HTTPException: 菜单不存在时抛出异常
        """
        # 获取菜单及其所有关联
        menu = await self.menu_repository.get_menu_with_roles(menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"菜单ID '{menu_id}' 不存在"
            )
        
        # 构建菜单基本信息
        menu_dict = {
            "id": menu.id,
            "menu_name": menu.menu_name,
            "menu_code": menu.menu_code,
            "menu_path": menu.menu_path,
            "parent_id": menu.parent_id,
            "sort_order": menu.sort_order,
            "creation_date": menu.creation_date,
            "last_update_date": menu.last_update_date,
            "success": True,
            "message": "获取菜单详情成功"
        }
        
        # 转换角色列表
        roles_list = []
        if hasattr(menu, "roles") and menu.roles:
            for role in menu.roles:
                # 确保每个角色都是字典格式
                roles_list.append({
                    "id": role.id,
                    "role_name": role.role_name,
                    "role_code": role.role_code
                })
        
        # 获取子菜单
        children = await self.menu_repository.get_menus_by_parent_id(menu_id)
        
        # 转换子菜单列表
        children_list = []
        if children:
            for child in children:
                # 构建子菜单基本信息
                child_dict = {
                    "id": child.id,
                    "menu_name": child.menu_name,
                    "menu_code": child.menu_code,
                    "menu_path": child.menu_path,
                    "parent_id": child.parent_id,
                    "sort_order": child.sort_order,
                    "creation_date": child.creation_date,
                    "last_update_date": child.last_update_date
                }
                
                # 获取孙菜单
                grandchildren = await self.menu_repository.get_menus_by_parent_id(child.id)
                
                # 转换孙菜单列表
                grandchildren_list = []
                if grandchildren:
                    for grandchild in grandchildren:
                        # 确保每个孙菜单都是字典格式
                        grandchildren_list.append({
                            "id": grandchild.id,
                            "menu_name": grandchild.menu_name,
                            "menu_code": grandchild.menu_code,
                            "menu_path": grandchild.menu_path,
                            "parent_id": grandchild.parent_id,
                            "sort_order": grandchild.sort_order,
                            "creation_date": grandchild.creation_date,
                            "last_update_date": grandchild.last_update_date,
                            "children": []
                        })
                
                # 添加孙菜单到子菜单
                child_dict["children"] = grandchildren_list
                children_list.append(child_dict)
        
        # 构建完整的菜单详情响应
        menu_dict["roles"] = roles_list
        menu_dict["children"] = children_list
        
        # 使用字典直接创建MenuDetail模型
        return MenuDetail.model_validate(menu_dict)
    
    async def get_all_menus(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> MenuBatchResponse:
        """
        获取菜单列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            菜单列表响应
        """
        # 获取菜单列表
        menus = await self.menu_repository.get_multi(
            skip=skip,
            limit=limit
        )
        
        # 获取总记录数
        total = await self.menu_repository.get_count()
        
        # 转换为响应模型
        return MenuBatchResponse(
            items=[MenuResponse.model_validate(menu) for menu in menus],
            total=total,
            success=True,
            message="获取菜单列表成功"
        )
    
    async def get_menu_tree(self) -> List[MenuTreeNode]:
        """
        获取菜单树
        
        Returns:
            菜单树节点列表
        """
        # 获取所有菜单
        all_menus = await self.menu_repository.get_menu_tree()
        
        # 构建菜单树
        menu_map = {}
        for menu in all_menus:
            # 确保每个菜单都是字典格式
            menu_dict = {
                "id": menu.id,
                "menu_name": menu.menu_name,
                "menu_code": menu.menu_code,
                "menu_path": menu.menu_path,
                "parent_id": menu.parent_id,
                "sort_order": menu.sort_order,
                "children": []
            }
            menu_map[menu.id] = MenuTreeNode.model_validate(menu_dict)
            
        # 构建树形结构
        root_menus = []
        for menu_id, menu_node in menu_map.items():
            if menu_node.parent_id is None:
                # 顶级菜单
                root_menus.append(menu_node)
            else:
                # 子菜单
                parent = menu_map.get(menu_node.parent_id)
                if parent:
                    if parent.children is None:
                        parent.children = []
                    parent.children.append(menu_node)
        
        return root_menus
    
    async def get_menus_by_role_id(self, role_id: int) -> List[MenuResponse]:
        """
        获取角色拥有的所有菜单
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单列表响应
            
        Raises:
            HTTPException: 角色不存在时抛出异常
        """
        # 检查角色是否存在
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID '{role_id}' 不存在"
            )
        
        # 获取角色菜单
        menus = await self.menu_repository.get_menus_by_role_id(role_id)
        
        # 转换为响应模型
        menu_responses = []
        for menu in menus:
            menu_dict = {
                "id": menu.id,
                "menu_name": menu.menu_name,
                "menu_code": menu.menu_code,
                "menu_path": menu.menu_path,
                "parent_id": menu.parent_id,
                "sort_order": menu.sort_order,
                "creation_date": menu.creation_date,
                "last_update_date": menu.last_update_date
            }
            menu_responses.append(MenuResponse.model_validate(menu_dict))
            
        return menu_responses 