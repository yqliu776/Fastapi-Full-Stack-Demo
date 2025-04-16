from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time

from app.modules.schemas import (
    UserCreate, UserUpdate, UserResponse, UserResponseWithRoles, 
    PaginationParams, UserAdminCreate
)

from app.services import AuthService, RbacService, oauth2_scheme
from app.core.decorators import permission_required
from app.routers.auth import get_current_user
from app.core.models import ResponseModel
from app.modules.models import SysUser
from app.core.connects import db

# 创建路由
user_router = APIRouter(prefix="/users", tags=["用户管理"])

# 用户注册接口
@user_router.post("/register", response_model=ResponseModel)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    用户注册接口
    
    Args:
        user_data: 用户注册信息
        auth_service: 认证服务实例
    
    Returns:
        ResponseModel: 包含用户基本信息的响应
    """
    start_time = time.time()
    
    # 检查用户名是否存在
    if await auth_service.user_repository.check_username_exists(user_data.user_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建用户(默认给予普通用户角色)
    user = await auth_service.user_repository.create_user_with_role(
        user_data=user_data,
        role_code="user",  # 默认角色代码
        created_by="system"
    )
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=UserResponse(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            creation_date=user.creation_date
        ),
        message="注册成功",
        process_time=process_time
    )

# 管理员创建用户接口
@user_router.post("/admin/create", response_model=ResponseModel)
@permission_required("user:create")
async def admin_create_user(
    user_data: UserAdminCreate,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    管理员创建用户接口
    
    Args:
        user_data: 用户创建信息(包含角色)
        current_user: 当前登录用户
        auth_service: 认证服务实例
        rbac_service: RBAC服务实例
    
    Returns:
        ResponseModel: 包含用户详细信息的响应
    """
    start_time = time.time()
    
    # 检查用户名是否存在
    if await auth_service.user_repository.check_username_exists(user_data.user_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查所有角色是否存在
    for role_code in user_data.role_codes:
        if not await rbac_service.role_repository.check_role_code_exists(role_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色代码不存在: {role_code}"
            )
    
    # 创建用户并分配角色
    user = await auth_service.user_repository.create_user_with_roles(
        user_data=user_data,
        role_codes=user_data.role_codes,
        created_by=current_user.user_name
    )
    
    # 获取用户详情(包含角色)
    user_with_roles = await auth_service.user_repository.get_user_with_roles(user.id)
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=UserResponseWithRoles.from_orm(user_with_roles),
        message="用户创建成功",
        process_time=process_time
    )

# 获取用户列表接口
@user_router.get("/list", response_model=ResponseModel)
@permission_required("user:list")
async def get_user_list(
    pagination: PaginationParams = Depends(),
    username: Optional[str] = Query(None, description="用户名过滤"),
    email: Optional[str] = Query(None, description="邮箱过滤"),
    phone: Optional[str] = Query(None, description="手机号过滤"),
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    获取用户列表接口
    
    Args:
        pagination: 分页参数
        username: 用户名过滤条件
        email: 邮箱过滤条件
        phone: 手机号过滤条件
        current_user: 当前登录用户
        auth_service: 认证服务实例
    
    Returns:
        ResponseModel: 包含用户列表的响应
    """
    start_time = time.time()
    
    # 获取用户列表
    users = await auth_service.user_repository.get_users_by_filter(
        skip=pagination.skip,
        limit=pagination.limit,
        username=username,
        email=email,
        phone=phone
    )
    
    # 获取总数
    total = await auth_service.user_repository.count_users_by_filter(
        username=username,
        email=email,
        phone=phone
    )
    
    # 转换为响应模型
    user_responses = [UserResponse.from_orm(user) for user in users]
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data={
            "items": user_responses,
            "total": total,
            "page": pagination.page,
            "size": pagination.size
        },
        message="获取用户列表成功",
        process_time=process_time
    )

# 获取用户详情接口
@user_router.get("/detail/{user_id}", response_model=ResponseModel)
@permission_required("user:detail")
async def get_user_detail(
    user_id: int,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    获取用户详情接口
    
    Args:
        user_id: 用户ID
        current_user: 当前登录用户
        auth_service: 认证服务实例
    
    Returns:
        ResponseModel: 包含用户详细信息的响应
    """
    start_time = time.time()
    
    # 获取用户详情
    user = await auth_service.user_repository.get_user_with_roles(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=UserResponseWithRoles.from_orm(user),
        message="获取用户详情成功",
        process_time=process_time
    )

# 更新用户信息接口
@user_router.put("/update/{user_id}", response_model=ResponseModel)
@permission_required("user:update")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(),
    rbac_service: RbacService = Depends()
) -> ResponseModel:
    """
    更新用户信息接口
    
    Args:
        user_id: 用户ID
        user_data: 用户更新信息
        current_user: 当前登录用户
        auth_service: 认证服务实例
        rbac_service: RBAC服务实例
    
    Returns:
        ResponseModel: 包含更新后的用户信息的响应
    """
    start_time = time.time()
    
    # 检查用户是否存在
    user = await auth_service.user_repository.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果要更新角色，检查角色是否存在
    if user_data.role_codes:
        for role_code in user_data.role_codes:
            if not await rbac_service.role_repository.check_role_code_exists(role_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色代码不存在: {role_code}"
                )
    
    # 更新用户信息
    updated_user = await auth_service.user_repository.update_user_with_roles(
        user_id=user_id,
        user_data=user_data,
        updated_by=current_user.user_name
    )
    
    # 获取更新后的用户详情
    user_with_roles = await auth_service.user_repository.get_user_with_roles(user_id)
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=UserResponseWithRoles.from_orm(user_with_roles),
        message="用户更新成功",
        process_time=process_time
    )

# 删除用户接口
@user_router.delete("/delete/{user_id}", response_model=ResponseModel)
@permission_required("user:delete")
async def delete_user(
    user_id: int,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    删除用户接口
    
    Args:
        user_id: 用户ID
        current_user: 当前登录用户
        auth_service: 认证服务实例
    
    Returns:
        ResponseModel: 删除结果响应
    """
    start_time = time.time()
    
    # 检查用户是否存在
    user = await auth_service.user_repository.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录用户"
        )
    
    # 删除用户(软删除)
    await auth_service.user_repository.remove(
        id=user_id,
        updated_by=current_user.user_name
    )
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data=None,
        message="用户删除成功",
        process_time=process_time
    )

# 重置用户密码接口
@user_router.post("/reset-password/{user_id}", response_model=ResponseModel)
@permission_required("user:reset-password")
async def reset_user_password(
    user_id: int,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends()
) -> ResponseModel:
    """
    重置用户密码接口
    
    Args:
        user_id: 用户ID
        current_user: 当前登录用户
        auth_service: 认证服务实例
    
    Returns:
        ResponseModel: 包含重置后的密码的响应
    """
    start_time = time.time()
    
    # 检查用户是否存在
    user = await auth_service.user_repository.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 重置密码
    new_password, updated_user = await auth_service.user_repository.reset_password(
        user_id=user_id,
        updated_by=current_user.user_name
    )
    
    process_time = time.time() - start_time
    return ResponseModel.success(
        data={"new_password": new_password},
        message="密码重置成功",
        process_time=process_time
    )
