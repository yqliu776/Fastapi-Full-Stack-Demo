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
    return ResponseModel.success(data=permission, message="权限创建成功")


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
    deleted: Optional[bool] = Query(None, description="删除状态过滤，false仅正常，true仅已删除"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取权限列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        permission_name: 权限名称过滤条件
        permission_code: 权限代码过滤条件
        deleted: 删除状态过滤条件
        rbac_service: RBAC服务实例
        
    Returns:
        权限列表响应
    """
    permissions = await rbac_service.get_all_permissions(skip, limit, permission_name, permission_code, deleted)
    return ResponseModel.success(data=permissions, message="获取权限列表成功")


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
    deleted: Optional[bool] = Query(None, description="删除状态过滤，false仅正常，true仅已删除"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取API权限绑定列表。

    支持按 HTTP 方法、接口路径模式和权限编码过滤，用于维护接口与权限码的映射关系。

    Args:
        skip: 跳过的记录数。
        limit: 返回的记录数。
        method: 可选 HTTP 方法过滤条件。
        path_pattern: 可选 API 路径模式过滤条件。
        permission_code: 可选权限代码过滤条件。
        deleted: 删除状态过滤条件。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 为API权限绑定分页列表。
    """
    bindings = await rbac_service.get_all_api_permissions(
        skip=skip,
        limit=limit,
        method=method,
        path_pattern=path_pattern,
        permission_code=permission_code,
        deleted=deleted
    )
    return ResponseModel.success(data=bindings, message="获取API权限绑定列表成功")


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
    """
    创建API权限绑定。

    将指定 HTTP 方法和路径模式绑定到权限编码，供权限校验装饰器识别接口访问权限。

    Args:
        binding_data: API权限绑定创建数据。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 为创建后的API权限绑定。
    """
    binding = await rbac_service.create_api_permission(binding_data)
    return ResponseModel.success(data=binding, message="API权限绑定创建成功")


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
    """
    更新API权限绑定。

    修改指定 API 权限绑定的 HTTP 方法、路径模式、权限编码或描述信息。

    Args:
        api_permission_id: API权限绑定ID。
        binding_data: API权限绑定更新数据。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 为更新后的API权限绑定。
    """
    binding = await rbac_service.update_api_permission(api_permission_id, binding_data)
    return ResponseModel.success(data=binding, message="API权限绑定更新成功")


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
    """
    删除API权限绑定。

    删除指定接口路径与权限编码的绑定关系，删除后该绑定不再参与接口权限校验。

    Args:
        api_permission_id: API权限绑定ID。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 包含删除成功标记。
    """
    result = await rbac_service.delete_api_permission(api_permission_id)
    if not result:
        return ResponseModel.error(
            code=400,
            message="API权限绑定删除失败",
            data={"success": result}
        )
    return ResponseModel.success(data={"success": result}, message="API权限绑定删除成功")


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
    return ResponseModel.success(data=permissions, message="获取角色权限成功")


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
    return ResponseModel.success(data=permission, message="获取权限详情成功")


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
    return ResponseModel.success(data=permission, message="权限更新成功")


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
    if not result:
        return ResponseModel.error(
            code=400,
            message="权限删除失败",
            data={"success": result}
        )
    return ResponseModel.success(data={"success": result}, message="权限删除成功")


@router.post(
    "/restore/{permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="恢复权限"
)
async def restore_permission(
    permission_id: int = Path(..., description="权限ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    恢复已软删除的权限
    
    Args:
        permission_id: 权限ID
        rbac_service: RBAC服务实例
        
    Returns:
        恢复后的权限响应
    """
    permission = await rbac_service.restore_permission(permission_id)
    return ResponseModel.success(data=permission, message="权限恢复成功")


@router.delete(
    "/purge/{permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="彻底删除权限"
)
async def purge_permission(
    permission_id: int = Path(..., description="权限ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    彻底删除权限及其关联数据（物理删除，不可恢复）
    
    Args:
        permission_id: 权限ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    await rbac_service.purge_permission(permission_id)
    return ResponseModel.success(data={"success": True}, message="权限已彻底删除")


@router.post(
    "/api-bindings/restore/{api_permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="恢复API权限绑定"
)
async def restore_api_permission_binding(
    api_permission_id: int = Path(..., description="API权限绑定ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    恢复已软删除的API权限绑定。
    """
    binding = await rbac_service.restore_api_permission(api_permission_id)
    return ResponseModel.success(data=binding, message="API权限绑定恢复成功")


@router.delete(
    "/api-bindings/purge/{api_permission_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["PERMISSION_MANAGE"]))],
    summary="彻底删除API权限绑定"
)
async def purge_api_permission_binding(
    api_permission_id: int = Path(..., description="API权限绑定ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    彻底删除API权限绑定（物理删除，不可恢复）。
    """
    await rbac_service.purge_api_permission(api_permission_id)
    return ResponseModel.success(data={"success": True}, message="API权限绑定已彻底删除")
