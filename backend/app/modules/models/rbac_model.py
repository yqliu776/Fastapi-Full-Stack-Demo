from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class SysUser(BaseModel):
    """用户信息表模型"""
    
    __tablename__ = "sys_users"
    
    user_name = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(100), nullable=False, comment="密码")
    phone_number = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    
    # 关联关系
    roles = relationship("SysRole", secondary="sys_user_roles", back_populates="users")
    
    def __repr__(self) -> str:
        return f"<SysUser(id={self.id}, user_name={self.user_name})>"


class SysRole(BaseModel):
    """角色信息表模型"""
    
    __tablename__ = "sys_roles"
    
    role_name = Column(String(50), nullable=False, comment="角色名称")
    role_code = Column(String(50), nullable=False, unique=True, comment="角色编码")
    
    # 关联关系
    users = relationship("SysUser", secondary="sys_user_roles", back_populates="roles")
    permissions = relationship("SysPermission", secondary="sys_role_permissions", back_populates="roles")
    menus = relationship("SysMenu", secondary="sys_role_menus", back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<SysRole(id={self.id}, role_name={self.role_name}, role_code={self.role_code})>"


class SysPermission(BaseModel):
    """权限信息表模型"""
    
    __tablename__ = "sys_permissions"
    
    permission_name = Column(String(50), nullable=False, comment="权限名称")
    permission_code = Column(String(50), nullable=False, unique=True, comment="权限编码")
    
    # 关联关系
    roles = relationship("SysRole", secondary="sys_role_permissions", back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<SysPermission(id={self.id}, permission_name={self.permission_name}, permission_code={self.permission_code})>"


class SysMenu(BaseModel):
    """菜单信息表模型"""
    
    __tablename__ = "sys_menus"
    
    menu_name = Column(String(50), nullable=False, comment="菜单名称")
    menu_code = Column(String(50), nullable=False, unique=True, comment="菜单编码")
    menu_path = Column(String(200), nullable=True, comment="菜单路径")
    parent_id = Column(BigInteger, nullable=True, comment="父菜单ID")
    sort_order = Column(Integer, nullable=True, default=0, comment="显示顺序")
    
    # 关联关系
    roles = relationship("SysRole", secondary="sys_role_menus", back_populates="menus")
    
    def __repr__(self) -> str:
        return f"<SysMenu(id={self.id}, menu_name={self.menu_name}, menu_code={self.menu_code})>"


class SysUserRole(BaseModel):
    """用户与角色关联表模型"""
    
    __tablename__ = "sys_user_roles"
    
    user_id = Column(BigInteger, ForeignKey("sys_users.id"), nullable=False, comment="用户ID")
    role_id = Column(BigInteger, ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")
    
    def __repr__(self) -> str:
        return f"<SysUserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"


class SysRolePermission(BaseModel):
    """角色与权限关联表模型"""
    
    __tablename__ = "sys_role_permissions"
    
    role_id = Column(BigInteger, ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")
    permission_id = Column(BigInteger, ForeignKey("sys_permissions.id"), nullable=False, comment="权限ID")
    
    def __repr__(self) -> str:
        return f"<SysRolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>"


class SysRoleMenu(BaseModel):
    """角色与菜单关联表模型"""
    
    __tablename__ = "sys_role_menus"
    
    role_id = Column(BigInteger, ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")
    menu_id = Column(BigInteger, ForeignKey("sys_menus.id"), nullable=False, comment="菜单ID")
    
    def __repr__(self) -> str:
        return f"<SysRoleMenu(id={self.id}, role_id={self.role_id}, menu_id={self.menu_id})>" 