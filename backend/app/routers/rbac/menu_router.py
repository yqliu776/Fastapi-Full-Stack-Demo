from fastapi import APIRouter, Depends, Query, Path, Body
from typing import List, Optional

from app.modules.schemas import (
    MenuCreate, MenuUpdate, MenuResponse, MenuDetail, MenuBatchResponse, MenuTreeNode
)
from app.core.decorators import has_permission
from app.core.models import ResponseModel
from app.routers.auth import get_current_user
from app.services import RbacService


router = APIRouter(prefix="/menus", tags=["菜单管理"])

@router.post(
    "",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="创建菜单"
)
async def create_menu(
    menu_data: MenuCreate,
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    创建菜单
    
    Args:
        menu_data: 菜单创建数据
        rbac_service: RBAC服务实例
        
    Returns:
        创建后的菜单响应
    """
    menu = await rbac_service.create_menu(menu_data)
    return ResponseModel.success(data=menu, message="菜单创建成功")


@router.get(
    "",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取菜单列表"
)
async def get_menus(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    menu_name: Optional[str] = Query(None, description="菜单名称"),
    deleted: Optional[bool] = Query(None, description="删除状态过滤，false仅正常，true仅已删除"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取菜单列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        menu_name: 菜单名称过滤条件
        deleted: 删除状态过滤条件
        rbac_service: RBAC服务实例
        
    Returns:
        菜单列表响应
    """
    menus = await rbac_service.get_all_menus(skip, limit, menu_name, deleted)
    return ResponseModel.success(data=menus, message="获取菜单列表成功")


@router.post(
    "/restore/{menu_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="恢复菜单"
)
async def restore_menu(
    menu_id: int = Path(..., description="菜单ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    恢复已软删除的菜单
    
    Args:
        menu_id: 菜单ID
        rbac_service: RBAC服务实例
        
    Returns:
        恢复后的菜单响应
    """
    menu = await rbac_service.restore_menu(menu_id)
    return ResponseModel.success(data=menu, message="菜单恢复成功")


@router.delete(
    "/purge/{menu_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="彻底删除菜单"
)
async def purge_menu(
    menu_id: int = Path(..., description="菜单ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    彻底删除菜单及其所有子孙菜单和关联数据（物理删除，不可恢复）
    
    Args:
        menu_id: 菜单ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    await rbac_service.purge_menu(menu_id)
    return ResponseModel.success(data={"success": True}, message="菜单已彻底删除")


@router.get(
    "/tree",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取菜单树"
)
async def get_menu_tree(
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取菜单树
    
    Args:
        rbac_service: RBAC服务实例
        
    Returns:
        菜单树节点列表
    """
    menu_tree = await rbac_service.get_menu_tree()
    return ResponseModel.success(data=menu_tree, message="获取菜单树成功")


@router.get(
    "/role/{role_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取角色拥有的菜单"
)
async def get_menus_by_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取角色拥有的菜单
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        菜单列表响应
    """
    menus = await rbac_service.get_menus_by_role_id(role_id)
    return ResponseModel.success(data=menus, message="获取角色菜单成功")


@router.get(
    "/current",
    response_model=ResponseModel,
    summary="获取当前用户菜单列表"
)
async def get_current_user_menus(
    current_user = Depends(get_current_user),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取当前登录用户可访问的菜单列表。

    根据当前用户拥有的角色查询可访问菜单，不返回其他角色独有的菜单项。

    Args:
        current_user: 当前认证用户。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 为当前用户可访问菜单列表。
    """
    menus = await rbac_service.get_menus_by_user_id(current_user.id)
    return ResponseModel.success(data=menus, message="获取当前用户菜单成功")


@router.get(
    "/current/tree",
    response_model=ResponseModel,
    summary="获取当前用户菜单树"
)
async def get_current_user_menu_tree(
    current_user = Depends(get_current_user),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取当前登录用户可访问的菜单树。

    根据当前用户拥有的角色查询可访问菜单，并按父子关系组装为树形结构。

    Args:
        current_user: 当前认证用户。
        rbac_service: RBAC服务实例。

    Returns:
        ResponseModel: 统一响应模型，data 为当前用户可访问菜单树。
    """
    menu_tree = await rbac_service.get_menu_tree_by_user_id(current_user.id)
    return ResponseModel.success(data=menu_tree, message="获取当前用户菜单树成功")


@router.get(
    "/{menu_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取菜单详情"
)
async def get_menu(
    menu_id: int = Path(..., description="菜单ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    获取菜单详情
    
    Args:
        menu_id: 菜单ID
        rbac_service: RBAC服务实例
        
    Returns:
        菜单详情响应
    """
    menu = await rbac_service.get_menu(menu_id)
    return ResponseModel.success(data=menu, message="获取菜单详情成功")


@router.put(
    "/{menu_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="更新菜单"
)
async def update_menu(
    menu_id: int = Path(..., description="菜单ID"),
    menu_data: MenuUpdate = Body(...),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    更新菜单
    
    Args:
        menu_id: 菜单ID
        menu_data: 菜单更新数据
        rbac_service: RBAC服务实例
        
    Returns:
        更新后的菜单响应
    """
    menu = await rbac_service.update_menu(menu_id, menu_data)
    return ResponseModel.success(data=menu, message="菜单更新成功")


@router.delete(
    "/{menu_id}",
    response_model=ResponseModel,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="删除菜单"
)
async def delete_menu(
    menu_id: int = Path(..., description="菜单ID"),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    删除菜单
    
    Args:
        menu_id: 菜单ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    result = await rbac_service.delete_menu(menu_id)
    if not result:
        return ResponseModel.error(
            code=400,
            message="菜单删除失败",
            data={"success": result}
        )
    return ResponseModel.success(data={"success": result}, message="菜单删除成功")
