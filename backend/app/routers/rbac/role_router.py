from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from typing import Optional

from app.modules.schemas import (
    RoleCreate, RoleUpdate, RoleResponse, RoleDetail, RoleBatchResponse,
    RolePermissionOperation, RolePermissionReplace, RoleMenuOperation, RoleMenuReplace
)
from app.core.models.response_models import ResponseModel
from app.core.decorators import has_permission
from app.routers.auth import get_current_user
from app.services import RbacService


router = APIRouter(prefix="/roles", tags=["角色管理"])

@router.post(
    "",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="创建角色"
)
async def create_role(
    role_data: RoleCreate,
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    创建角色
    
    Args:
        role_data: 角色创建数据
        rbac_service: RBAC服务实例
        
    Returns:
        创建后的角色响应
    """
    role = await rbac_service.create_role(role_data)
    return ResponseModel(
        code=200,
        message="角色创建成功",
        data=role
    )


@router.put(
    "/{role_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="更新角色"
)
async def update_role(
    role_id: int = Path(..., description="角色ID"),
    role_data: RoleUpdate = Body(...),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    更新角色
    
    Args:
        role_id: 角色ID
        role_data: 角色更新数据
        rbac_service: RBAC服务实例
        
    Returns:
        更新后的角色响应
    """
    role = await rbac_service.update_role(role_id, role_data)
    return ResponseModel(
        code=200,
        message="角色更新成功",
        data=role
    )


@router.delete(
    "/{role_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="删除角色"
)
async def delete_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    删除角色
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    result = await rbac_service.delete_role(role_id)
    return ResponseModel(
        code=200 if result else 400,
        message="角色删除成功" if result else "角色删除失败",
        data={"success": result}
    )


@router.get(
    "/{role_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="获取角色详情"
)
async def get_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取角色详情
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        角色详情响应
    """
    role = await rbac_service.get_role(role_id)
    return ResponseModel(
        code=200,
        message="获取角色详情成功",
        data=role
    )


@router.get(
    "",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="获取角色列表"
)
async def get_roles(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    role_name: Optional[str] = Query(None, description="角色名称"),
    role_code: Optional[str] = Query(None, description="角色代码"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
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
    roles = await rbac_service.get_all_roles(skip, limit, role_name, role_code)
    return ResponseModel(
        code=200,
        message="获取角色列表成功",
        data=roles
    )


@router.post(
    "/{role_id}/permissions",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="为角色分配权限"
)
async def assign_permissions_to_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RolePermissionOperation = Body(...),
    rbac_service: RbacService = Depends(),
    current_user = Depends(get_current_user)
) -> ResponseModel:
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
    if role_id != operation.role_id:
        raise HTTPException(status_code=400, detail="请求参数不一致")
        
    audit_info = {
        "created_by": current_user.user_name,
        "last_updated_by": current_user.user_name,
        "last_update_login": current_user.user_name
    }
    
    result = await rbac_service.add_permissions_to_role(
        role_id=role_id,
        permission_ids=operation.permission_ids,
        audit_info=audit_info
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="权限分配失败")
    
    return ResponseModel.success(data={"success": result}, message="权限分配成功")


@router.delete(
    "/{role_id}/permissions",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="移除角色的权限"
)
async def remove_permissions_from_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RolePermissionOperation = Body(...),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    移除角色的权限
    
    Args:
        role_id: 角色ID
        operation: 角色权限操作数据
        rbac_service: RBAC服务实例
        
    Returns:
        操作结果
    """
    if role_id != operation.role_id:
        raise HTTPException(status_code=400, detail="请求参数不一致")
        
    result = await rbac_service.remove_permissions_from_role(
        role_id=role_id,
        permission_ids=operation.permission_ids
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="权限移除失败")
    
    return ResponseModel.success(data={"success": result}, message="权限移除成功")


@router.put(
    "/{role_id}/permissions",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="保存角色权限完整集合"
)
async def replace_role_permissions(
    role_id: int = Path(..., description="角色ID"),
    operation: RolePermissionReplace = Body(...),
    rbac_service: RbacService = Depends(),
    current_user = Depends(get_current_user)
) -> ResponseModel:
    """
    保存角色权限完整集合。

    用请求中的权限ID列表替换角色当前所有权限关系，适用于权限编辑页面一次性保存勾选结果。

    Args:
        role_id: 角色ID。
        operation: 角色权限替换数据，包含完整权限ID集合。
        rbac_service: RBAC服务实例。
        current_user: 当前认证用户，用于审计字段。

    Returns:
        ResponseModel: 统一响应模型，data 包含保存成功标记。

    Raises:
        HTTPException: 权限保存失败时返回 400。
    """
    audit_info = {
        "created_by": current_user.user_name,
        "last_updated_by": current_user.user_name,
        "last_update_login": current_user.user_name
    }

    result = await rbac_service.replace_permissions_for_role(
        role_id=role_id,
        permission_ids=operation.permission_ids,
        audit_info=audit_info
    )

    if not result:
        raise HTTPException(status_code=400, detail="权限保存失败")

    return ResponseModel.success(data={"success": result}, message="权限保存成功")


@router.post(
    "/{role_id}/menus",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="为角色分配菜单"
)
async def assign_menus_to_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RoleMenuOperation = Body(...),
    rbac_service: RbacService = Depends(),
    current_user = Depends(get_current_user)
) -> ResponseModel:
    """
    为角色分配菜单。

    将请求中的菜单ID追加分配给指定角色，保留角色已有菜单关系。

    Args:
        role_id: 角色ID。
        operation: 角色菜单分配数据，包含待追加的菜单ID集合。
        rbac_service: RBAC服务实例。
        current_user: 当前认证用户，用于审计字段。

    Returns:
        ResponseModel: 统一响应模型，data 包含分配成功标记。

    Raises:
        HTTPException: 路径角色ID与请求体不一致，或菜单分配失败时返回 400。
    """
    if role_id != operation.role_id:
        raise HTTPException(status_code=400, detail="请求参数不一致")
        
    audit_info = {
        "created_by": current_user.user_name,
        "last_updated_by": current_user.user_name,
        "last_update_login": current_user.user_name
    }
    
    result = await rbac_service.add_menus_to_role(
        role_id=role_id,
        menu_ids=operation.menu_ids,
        audit_info=audit_info
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="菜单分配失败")
    
    return ResponseModel.success(data={"success": result}, message="菜单分配成功")


@router.delete(
    "/{role_id}/menus",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="移除角色的菜单"
)
async def remove_menus_from_role(
    role_id: int = Path(..., description="角色ID"),
    operation: RoleMenuOperation = Body(...),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    移除角色的菜单。

    从指定角色移除请求中的菜单ID集合，其他菜单授权保持不变。

    Args:
        role_id: 角色ID。
        operation: 角色菜单移除数据，包含待移除的菜单ID集合。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 包含移除成功标记。

    Raises:
        HTTPException: 路径角色ID与请求体不一致，或菜单移除失败时返回 400。
    """
    if role_id != operation.role_id:
        raise HTTPException(status_code=400, detail="请求参数不一致")
        
    result = await rbac_service.remove_menus_from_role(
        role_id=role_id,
        menu_ids=operation.menu_ids
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="菜单移除失败")
    
    return ResponseModel.success(data={"success": result}, message="菜单移除成功") 


@router.put(
    "/{role_id}/menus",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["ROLE_MANAGE"]))],
    summary="保存角色菜单完整集合"
)
async def replace_role_menus(
    role_id: int = Path(..., description="角色ID"),
    operation: RoleMenuReplace = Body(...),
    rbac_service: RbacService = Depends(),
    current_user = Depends(get_current_user)
) -> ResponseModel:
    """
    保存角色菜单完整集合。

    用请求中的菜单ID列表替换角色当前所有菜单关系，适用于菜单授权页面一次性保存勾选结果。

    Args:
        role_id: 角色ID。
        operation: 角色菜单替换数据，包含完整菜单ID集合。
        rbac_service: RBAC服务实例。
        current_user: 当前认证用户，用于审计字段。

    Returns:
        ResponseModel: 统一响应模型，data 包含保存成功标记。

    Raises:
        HTTPException: 菜单保存失败时返回 400。
    """
    audit_info = {
        "created_by": current_user.user_name,
        "last_updated_by": current_user.user_name,
        "last_update_login": current_user.user_name
    }

    result = await rbac_service.replace_menus_for_role(
        role_id=role_id,
        menu_ids=operation.menu_ids,
        audit_info=audit_info
    )

    if not result:
        raise HTTPException(status_code=400, detail="菜单保存失败")

    return ResponseModel.success(data={"success": result}, message="菜单保存成功")
