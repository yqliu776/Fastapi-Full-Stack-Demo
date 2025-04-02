from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Path, Body

from app.core.decorators import has_permission
from app.modules.schemas import (
    PermissionCreate, PermissionUpdate, PermissionResponse, PermissionDetail, PermissionBatchResponse
)
from app.services import RBACService


router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.post(
    "",
    response_model=PermissionResponse,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="创建权限"
)
async def create_permission(
    permission_data: PermissionCreate,
    rbac_service: RBACService = Depends()
) -> PermissionResponse:
    """
    创建权限
    
    Args:
        permission_data: 权限创建数据
        rbac_service: RBAC服务实例
        
    Returns:
        创建后的权限响应
    """
    return await rbac_service.create_permission(permission_data)


@router.get(
    "",
    response_model=PermissionBatchResponse,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取权限列表"
)
async def get_permissions(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    permission_name: Optional[str] = Query(None, description="权限名称"),
    permission_code: Optional[str] = Query(None, description="权限代码"),
    rbac_service: RBACService = Depends()
) -> PermissionBatchResponse:
    """
    获取权限列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        permission_name: 权限名称过滤条件
        permission_code: 权限代码过滤条件
        rbac_service: RBAC服务实例
        
    Returns:
        权限列表响应
    """
    return await rbac_service.get_all_permissions(skip, limit, permission_name, permission_code)


@router.get(
    "/role/{role_id}",
    response_model=List[PermissionResponse],
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取角色拥有的权限"
)
async def get_permissions_by_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RBACService = Depends()
) -> List[PermissionResponse]:
    """
    获取角色拥有的权限
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        权限列表响应
    """
    return await rbac_service.get_permissions_by_role_id(role_id)


@router.get(
    "/{permission_id}",
    response_model=PermissionDetail,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取权限详情"
)
async def get_permission(
    permission_id: int = Path(..., description="权限ID"),
    rbac_service: RBACService = Depends()
) -> PermissionDetail:
    """
    获取权限详情
    
    Args:
        permission_id: 权限ID
        rbac_service: RBAC服务实例
        
    Returns:
        权限详情响应
    """
    return await rbac_service.get_permission(permission_id)


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="更新权限"
)
async def update_permission(
    permission_id: int = Path(..., description="权限ID"),
    permission_data: PermissionUpdate = Body(...),
    rbac_service: RBACService = Depends()
) -> PermissionResponse:
    """
    更新权限
    
    Args:
        permission_id: 权限ID
        permission_data: 权限更新数据
        rbac_service: RBAC服务实例
        
    Returns:
        更新后的权限响应
    """
    return await rbac_service.update_permission(permission_id, permission_data)


@router.delete(
    "/{permission_id}",
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="删除权限"
)
async def delete_permission(
    permission_id: int = Path(..., description="权限ID"),
    rbac_service: RBACService = Depends()
) -> dict:
    """
    删除权限
    
    Args:
        permission_id: 权限ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    result = await rbac_service.delete_permission(permission_id)
    return {"success": result, "message": "权限删除成功" if result else "权限删除失败"} 