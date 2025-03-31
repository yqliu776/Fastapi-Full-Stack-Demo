-- ========== 1. 用户表 ==========
CREATE TABLE sys_users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_name VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    phone_number VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_user_name (user_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';


-- ========== 2. 角色表 ==========
CREATE TABLE sys_roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    role_code VARCHAR(50) NOT NULL COMMENT '角色编码',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_role_code (role_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色信息表';


-- ========== 3. 权限表 ==========
CREATE TABLE sys_permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    permission_name VARCHAR(50) NOT NULL COMMENT '权限名称',
    permission_code VARCHAR(50) NOT NULL COMMENT '权限编码',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_permission_code (permission_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限信息表';


-- ========== 4. 菜单表 ==========
CREATE TABLE sys_menus (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    menu_name VARCHAR(50) NOT NULL COMMENT '菜单名称',
    menu_code VARCHAR(50) NOT NULL COMMENT '菜单编码',
    menu_path VARCHAR(200) DEFAULT NULL COMMENT '菜单路径',
    parent_id BIGINT DEFAULT NULL COMMENT '父菜单ID',
    sort_order INT DEFAULT 0 COMMENT '显示顺序',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_menu_code (menu_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单信息表';


-- ========== 5. 用户-角色关联表 ==========
CREATE TABLE sys_user_roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_user_id_role_id (user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户与角色关联表';


-- ========== 6. 角色-权限关联表 ==========
CREATE TABLE sys_role_permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    permission_id BIGINT NOT NULL COMMENT '权限ID',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_role_id_permission_id (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色与权限关联表';


-- ========== 7. 角色-菜单关联表 ==========
CREATE TABLE sys_role_menus (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    menu_id BIGINT NOT NULL COMMENT '菜单ID',
    
    creation_date DATETIME NOT NULL COMMENT '创建时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    last_update_date DATETIME NOT NULL COMMENT '修改时间',
    last_updated_by VARCHAR(50) NOT NULL COMMENT '修改人',
    last_update_login VARCHAR(50) NOT NULL COMMENT '最后登录ID',
    delete_flag CHAR(1) NOT NULL DEFAULT 'N' COMMENT '删除标识，Y/N',
    version_num INT NOT NULL DEFAULT 1 COMMENT '版本号',
    
    UNIQUE KEY uk_role_id_menu_id (role_id, menu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色与菜单关联表';