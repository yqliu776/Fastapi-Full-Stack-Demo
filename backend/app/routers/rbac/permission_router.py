from fastapi import APIRouter, Depends, Query, Path, Body
from typing import List, Optional

from app.modules.schemas import (
    PermissionCreate, PermissionUpdate, PermissionResponse, PermissionDetail, PermissionBatchResponse,
    ApiPermissionCreate, ApiPermissionUpdate
)
from app.core.decorators import has_permission
from app.core.models import ResponseModel
from app.services import RbacService


router = APIRouter(prefix="/permissions", tags=["权限管理"])

@router.post(
    "",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="创建权限"
)
async def create_permission(
    permission_data: PermissionCreate,
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    创建权限
    
    Args:
        permission_data: 权限创建数据
        rbac_service: RBAC服务实例
        
    Returns:
        创建后的权限响应
    """
    permission = await rbac_service.create_permission(permission_data)
    return ResponseModel(
        code=200,
        message="权限创建成功",
        data=permission
    )


@router.get(
    "",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取权限列表"
)
async def get_permissions(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    permission_name: Optional[str] = Query(None, description="权限名称"),
    permission_code: Optional[str] = Query(None, description="权限代码"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
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
    permissions = await rbac_service.get_all_permissions(skip, limit, permission_name, permission_code)
    return ResponseModel(
        code=200,
        message="获取权限列表成功",
        data=permissions
    )


@router.get(
    "/api-bindings",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取API权限绑定列表"
)
async def get_api_permission_bindings(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    method: Optional[str] = Query(None, description="HTTP方法"),
    path_pattern: Optional[str] = Query(None, description="API路径模式"),
    permission_code: Optional[str] = Query(None, description="权限代码"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    bindings = await rbac_service.get_all_api_permissions(
        skip=skip,
        limit=limit,
        method=method,
        path_pattern=path_pattern,
        permission_code=permission_code
    )
    return ResponseModel(
        code=200,
        message="获取API权限绑定列表成功",
        data=bindings
    )


@router.post(
    "/api-bindings",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="创建API权限绑定"
)
async def create_api_permission_binding(
    binding_data: ApiPermissionCreate,
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    binding = await rbac_service.create_api_permission(binding_data)
    return ResponseModel(
        code=200,
        message="API权限绑定创建成功",
        data=binding
    )


@router.put(
    "/api-bindings/{api_permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="更新API权限绑定"
)
async def update_api_permission_binding(
    api_permission_id: int = Path(..., description="API权限绑定ID"),
    binding_data: ApiPermissionUpdate = Body(...),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    binding = await rbac_service.update_api_permission(api_permission_id, binding_data)
    return ResponseModel(
        code=200,
        message="API权限绑定更新成功",
        data=binding
    )


@router.delete(
    "/api-bindings/{api_permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="删除API权限绑定"
)
async def delete_api_permission_binding(
    api_permission_id: int = Path(..., description="API权限绑定ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    result = await rbac_service.delete_api_permission(api_permission_id)
    return ResponseModel(
        code=200 if result else 400,
        message="API权限绑定删除成功" if result else "API权限绑定删除失败",
        data={"success": result}
    )


@router.get(
    "/role/{role_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取角色拥有的权限"
)
async def get_permissions_by_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取角色拥有的权限
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        权限列表响应
    """
    permissions = await rbac_service.get_permissions_by_role_id(role_id)
    return ResponseModel(
        code=200,
        message="获取角色权限成功",
        data=permissions
    )


@router.get(
    "/{permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="获取权限详情"
)
async def get_permission(
    permission_id: int = Path(..., description="权限ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取权限详情
    
    Args:
        permission_id: 权限ID
        rbac_service: RBAC服务实例
        
    Returns:
        权限详情响应
    """
    permission = await rbac_service.get_permission(permission_id)
    return ResponseModel(
        code=200,
        message="获取权限详情成功",
        data=permission
    )


@router.put(
    "/{permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="更新权限"
)
async def update_permission(
    permission_id: int = Path(..., description="权限ID"),
    permission_data: PermissionUpdate = Body(...),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    更新权限
    
    Args:
        permission_id: 权限ID
        permission_data: 权限更新数据
        rbac_service: RBAC服务实例
        
    Returns:
        更新后的权限响应
    """
    permission = await rbac_service.update_permission(permission_id, permission_data)
    return ResponseModel(
        code=200,
        message="权限更新成功",
        data=permission
    )


@router.delete(
    "/{permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="删除权限"
)
async def delete_permission(
    permission_id: int = Path(..., description="权限ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    删除权限
    
    Args:
        permission_id: 权限ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    result = await rbac_service.delete_permission(permission_id)
    return ResponseModel(
        code=200 if result else 400,
        message="权限删除成功" if result else "权限删除失败",
        data={"success": result}
    ) 
