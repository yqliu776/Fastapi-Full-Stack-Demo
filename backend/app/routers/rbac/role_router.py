from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, Body

from app.core.decorators import has_permission
from app.modules.schemas import (
    RoleCreate, RoleUpdate, RoleResponse, RoleDetail, RoleBatchResponse,
    RolePermissionOperation, RoleMenuOperation
)
from app.services import RBACService
from app.routers.auth.auth_router import get_current_user


router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post(
    "",
    response_model=RoleResponse,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="创建角色"
)
async def create_role(
    role_data: RoleCreate,
    rbac_service: RBACService = Depends()
) -> RoleResponse:
    """
    创建角色
    
    Args:
        role_data: 角色创建数据
        rbac_service: RBAC服务实例
        
    Returns:
        创建后的角色响应
    """
    return await rbac_service.create_role(role_data)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="更新角色"
)
async def update_role(
    role_id: int = Path(..., description="角色ID"),
    role_data: RoleUpdate = Body(...),
    rbac_service: RBACService = Depends()
) -> RoleResponse:
    """
    更新角色
    
    Args:
        role_id: 角色ID
        role_data: 角色更新数据
        rbac_service: RBAC服务实例
        
    Returns:
        更新后的角色响应
    """
    return await rbac_service.update_role(role_id, role_data)


@router.delete(
    "/{role_id}",
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="删除角色"
)
async def delete_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RBACService = Depends()
) -> dict:
    """
    删除角色
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    result = await rbac_service.delete_role(role_id)
    return {"success": result, "message": "角色删除成功" if result else "角色删除失败"}


@router.get(
    "/{role_id}",
    response_model=RoleDetail,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="获取角色详情"
)
async def get_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RBACService = Depends()
) -> RoleDetail:
    """
    获取角色详情
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        角色详情响应
    """
    return await rbac_service.get_role(role_id)


@router.get(
    "",
    response_model=RoleBatchResponse,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="获取角色列表"
)
async def get_roles(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    role_name: Optional[str] = Query(None, description="角色名称"),
    role_code: Optional[str] = Query(None, description="角色代码"),
    rbac_service: RBACService = Depends()
) -> RoleBatchResponse:
    """
    获取角色列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        role_name: 角色名称过滤条件
        role_code: 角色代码过滤条件
        rbac_service: RBAC服务实例
        
    Returns:
        角色列表响应
    """
    return await rbac_service.get_all_roles(skip, limit, role_name, role_code)


@router.post(
    "/{role_id}/permissions",
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="为角色分配权限"
)
async def assign_permissions_to_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RolePermissionOperation = Body(...),
    rbac_service: RBACService = Depends(),
    current_user = Depends(get_current_user)
) -> dict:
    """
    为角色分配权限
    
    Args:
        role_id: 角色ID
        operation: 角色权限操作数据
        rbac_service: RBAC服务实例
        current_user: 当前登录用户
        
    Returns:
        操作结果
    """
    # 验证路径参数和请求体中的角色ID是否一致
    if role_id != operation.role_id:
        return {"success": False, "message": "请求参数不一致"}
        
    # 构建审计信息
    audit_info = {
        "created_by": operation.operator,
        "last_updated_by": operation.operator,
        "last_update_login": operation.operation_login
    }
    
    result = await rbac_service.add_permissions_to_role(
        role_id=role_id,
        permission_ids=operation.permission_ids,
        audit_info=audit_info
    )
    
    return {"success": result, "message": "权限分配成功" if result else "权限分配失败"}


@router.delete(
    "/{role_id}/permissions",
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="移除角色的权限"
)
async def remove_permissions_from_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RolePermissionOperation = Body(...),
    rbac_service: RBACService = Depends()
) -> dict:
    """
    移除角色的权限
    
    Args:
        role_id: 角色ID
        operation: 角色权限操作数据
        rbac_service: RBAC服务实例
        
    Returns:
        操作结果
    """
    # 验证路径参数和请求体中的角色ID是否一致
    if role_id != operation.role_id:
        return {"success": False, "message": "请求参数不一致"}
        
    result = await rbac_service.remove_permissions_from_role(
        role_id=role_id,
        permission_ids=operation.permission_ids
    )
    
    return {"success": result, "message": "权限移除成功" if result else "权限移除失败"}


@router.post(
    "/{role_id}/menus",
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="为角色分配菜单"
)
async def assign_menus_to_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RoleMenuOperation = Body(...),
    rbac_service: RBACService = Depends()
) -> dict:
    """
    为角色分配菜单
    
    Args:
        role_id: 角色ID
        operation: 角色菜单操作数据
        rbac_service: RBAC服务实例
        
    Returns:
        操作结果
    """
    # 验证路径参数和请求体中的角色ID是否一致
    if role_id != operation.role_id:
        return {"success": False, "message": "请求参数不一致"}
        
    # 构建审计信息
    audit_info = {
        "created_by": operation.operator,
        "last_updated_by": operation.operator,
        "last_update_login": operation.operation_login
    }
    
    result = await rbac_service.add_menus_to_role(
        role_id=role_id,
        menu_ids=operation.menu_ids,
        audit_info=audit_info
    )
    
    return {"success": result, "message": "菜单分配成功" if result else "菜单分配失败"}


@router.delete(
    "/{role_id}/menus",
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="移除角色的菜单"
)
async def remove_menus_from_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RoleMenuOperation = Body(...),
    rbac_service: RBACService = Depends()
) -> dict:
    """
    移除角色的菜单
    
    Args:
        role_id: 角色ID
        operation: 角色菜单操作数据
        rbac_service: RBAC服务实例
        
    Returns:
        操作结果
    """
    # 验证路径参数和请求体中的角色ID是否一致
    if role_id != operation.role_id:
        return {"success": False, "message": "请求参数不一致"}
        
    result = await rbac_service.remove_menus_from_role(
        role_id=role_id,
        menu_ids=operation.menu_ids
    )
    
    return {"success": result, "message": "菜单移除成功" if result else "菜单移除失败"} 