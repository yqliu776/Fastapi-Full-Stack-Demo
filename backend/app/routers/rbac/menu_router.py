from typing import List

from fastapi import APIRouter, Depends, Query, Path, Body

from app.core.decorators import has_permission
from app.modules.schemas import (
    MenuCreate, MenuUpdate, MenuResponse, MenuDetail, MenuBatchResponse, MenuTreeNode
)
from app.services import RBACService


router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.post(
    "",
    response_model=MenuResponse,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="创建菜单"
)
async def create_menu(
    menu_data: MenuCreate,
    rbac_service: RBACService = Depends()
) -> MenuResponse:
    """
    创建菜单
    
    Args:
        menu_data: 菜单创建数据
        rbac_service: RBAC服务实例
        
    Returns:
        创建后的菜单响应
    """
    return await rbac_service.create_menu(menu_data)


@router.get(
    "",
    response_model=MenuBatchResponse,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取菜单列表"
)
async def get_menus(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    rbac_service: RBACService = Depends()
) -> MenuBatchResponse:
    """
    获取菜单列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        rbac_service: RBAC服务实例
        
    Returns:
        菜单列表响应
    """
    return await rbac_service.get_all_menus(skip, limit)


@router.get(
    "/tree",
    response_model=List[MenuTreeNode],
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取菜单树"
)
async def get_menu_tree(
    rbac_service: RBACService = Depends()
) -> List[MenuTreeNode]:
    """
    获取菜单树
    
    Args:
        rbac_service: RBAC服务实例
        
    Returns:
        菜单树节点列表
    """
    return await rbac_service.get_menu_tree()


@router.get(
    "/role/{role_id}",
    response_model=List[MenuResponse],
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取角色拥有的菜单"
)
async def get_menus_by_role(
    role_id: int = Path(..., description="角色ID"),
    rbac_service: RBACService = Depends()
) -> List[MenuResponse]:
    """
    获取角色拥有的菜单
    
    Args:
        role_id: 角色ID
        rbac_service: RBAC服务实例
        
    Returns:
        菜单列表响应
    """
    return await rbac_service.get_menus_by_role_id(role_id)


@router.get(
    "/{menu_id}",
    response_model=MenuDetail,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="获取菜单详情"
)
async def get_menu(
    menu_id: int = Path(..., description="菜单ID"),
    rbac_service: RBACService = Depends()
) -> MenuDetail:
    """
    获取菜单详情
    
    Args:
        menu_id: 菜单ID
        rbac_service: RBAC服务实例
        
    Returns:
        菜单详情响应
    """
    return await rbac_service.get_menu(menu_id)


@router.put(
    "/{menu_id}",
    response_model=MenuResponse,
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="更新菜单"
)
async def update_menu(
    menu_id: int = Path(..., description="菜单ID"),
    menu_data: MenuUpdate = Body(...),
    rbac_service: RBACService = Depends()
) -> MenuResponse:
    """
    更新菜单
    
    Args:
        menu_id: 菜单ID
        menu_data: 菜单更新数据
        rbac_service: RBAC服务实例
        
    Returns:
        更新后的菜单响应
    """
    return await rbac_service.update_menu(menu_id, menu_data)


@router.delete(
    "/{menu_id}",
    dependencies=[Depends(has_permission(["MENU_MANAGE"]))],
    summary="删除菜单"
)
async def delete_menu(
    menu_id: int = Path(..., description="菜单ID"),
    rbac_service: RBACService = Depends()
) -> dict:
    """
    删除菜单
    
    Args:
        menu_id: 菜单ID
        rbac_service: RBAC服务实例
        
    Returns:
        删除结果
    """
    result = await rbac_service.delete_menu(menu_id)
    return {"success": result, "message": "菜单删除成功" if result else "菜单删除失败"} 