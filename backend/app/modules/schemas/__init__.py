from app.modules.schemas.base_schema import BaseSchema, BaseResponseModel
from app.modules.schemas.auth_schema import (
    TokenPayload, TokenResponse, LoginRequest, PasswordChangeRequest
)
from app.modules.schemas.user_schema import (
    UserBase, UserCreate, UserUpdate, UserDetail, UserList,
    RoleInfo, PermissionInfo, MenuInfo
)
from app.modules.schemas.role_schema import (
    RoleBase, RoleCreate, RoleUpdate, RoleResponse, RoleDetail, RoleBatchResponse,
    RolePermissionOperation, RoleMenuOperation
)
from app.modules.schemas.permission_schema import (
    PermissionBase, PermissionCreate, PermissionUpdate, PermissionResponse,
    PermissionDetail, PermissionBatchResponse
)
from app.modules.schemas.menu_schema import (
    MenuBase, MenuCreate, MenuUpdate, MenuResponse, MenuDetail,
    MenuTreeNode, MenuBatchResponse
)

__all__ = [
    # 基础模型
    "BaseSchema", "BaseResponseModel",
    
    # 认证相关模型
    "TokenPayload", "TokenResponse", "LoginRequest", "PasswordChangeRequest",
    
    # 用户相关模型
    "UserBase", "UserCreate", "UserUpdate", "UserDetail", "UserList",
    "RoleInfo", "PermissionInfo", "MenuInfo",
    
    # 角色相关模型
    "RoleBase", "RoleCreate", "RoleUpdate", "RoleResponse", "RoleDetail", "RoleBatchResponse",
    "RolePermissionOperation", "RoleMenuOperation",
    
    # 权限相关模型
    "PermissionBase", "PermissionCreate", "PermissionUpdate", "PermissionResponse",
    "PermissionDetail", "PermissionBatchResponse",
    
    # 菜单相关模型
    "MenuBase", "MenuCreate", "MenuUpdate", "MenuResponse", "MenuDetail",
    "MenuTreeNode", "MenuBatchResponse",
]
