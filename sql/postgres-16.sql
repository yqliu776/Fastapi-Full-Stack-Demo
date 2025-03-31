-- 先创建表
-- ========== 1. 用户表 ==========
CREATE TABLE sys_users (
    id BIGSERIAL PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

-- 必要的唯一索引
CREATE UNIQUE INDEX uk_user_name ON sys_users (user_name);


-- ========== 2. 角色表 ==========
CREATE TABLE sys_roles (
    id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    role_code VARCHAR(50) NOT NULL,

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX uk_role_code ON sys_roles (role_code);


-- ========== 3. 权限表 ==========
CREATE TABLE sys_permissions (
    id BIGSERIAL PRIMARY KEY,
    permission_name VARCHAR(50) NOT NULL,
    permission_code VARCHAR(50) NOT NULL,

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX uk_permission_code ON sys_permissions (permission_code);


-- ========== 4. 菜单表 ==========
CREATE TABLE sys_menus (
    id BIGSERIAL PRIMARY KEY,
    menu_name VARCHAR(50) NOT NULL,
    menu_code VARCHAR(50) NOT NULL,
    menu_path VARCHAR(200),
    parent_id BIGINT,
    sort_order INT DEFAULT 0,

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX uk_menu_code ON sys_menus (menu_code);


-- ========== 5. 用户-角色关联表 ==========
CREATE TABLE sys_user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX uk_user_id_role_id ON sys_user_roles (user_id, role_id);


-- ========== 6. 角色-权限关联表 ==========
CREATE TABLE sys_role_permissions (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX uk_role_id_permission_id ON sys_role_permissions (role_id, permission_id);


-- ========== 7. 角色-菜单关联表 ==========
CREATE TABLE sys_role_menus (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL,
    menu_id BIGINT NOT NULL,

    creation_date TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    last_update_date TIMESTAMP NOT NULL,
    last_updated_by VARCHAR(50) NOT NULL,
    last_update_login VARCHAR(50) NOT NULL,
    delete_flag CHAR(1) NOT NULL DEFAULT 'N',
    version_num INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX uk_role_id_menu_id ON sys_role_menus (role_id, menu_id);

-- 然后 COMMENT ON 给表和列添加注释
-- ========== 1. 用户表 ==========
COMMENT ON TABLE sys_users IS '用户信息表';
COMMENT ON COLUMN sys_users.id IS '主键ID';
COMMENT ON COLUMN sys_users.user_name IS '用户名';
COMMENT ON COLUMN sys_users.password IS '密码';
COMMENT ON COLUMN sys_users.phone_number IS '手机号';
COMMENT ON COLUMN sys_users.email IS '邮箱';
COMMENT ON COLUMN sys_users.creation_date IS '创建时间';
COMMENT ON COLUMN sys_users.created_by IS '创建人';
COMMENT ON COLUMN sys_users.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_users.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_users.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_users.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_users.version_num IS '版本号';

-- ========== 2. 角色表 ==========
COMMENT ON TABLE sys_roles IS '角色信息表';
COMMENT ON COLUMN sys_roles.id IS '主键ID';
COMMENT ON COLUMN sys_roles.role_name IS '角色名称';
COMMENT ON COLUMN sys_roles.role_code IS '角色编码';

COMMENT ON COLUMN sys_roles.creation_date IS '创建时间';
COMMENT ON COLUMN sys_roles.created_by IS '创建人';
COMMENT ON COLUMN sys_roles.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_roles.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_roles.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_roles.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_roles.version_num IS '版本号';

-- ========== 3. 权限表 ==========
COMMENT ON TABLE sys_permissions IS '权限信息表';
COMMENT ON COLUMN sys_permissions.id IS '主键ID';
COMMENT ON COLUMN sys_permissions.permission_name IS '权限名称';
COMMENT ON COLUMN sys_permissions.permission_code IS '权限编码';

COMMENT ON COLUMN sys_permissions.creation_date IS '创建时间';
COMMENT ON COLUMN sys_permissions.created_by IS '创建人';
COMMENT ON COLUMN sys_permissions.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_permissions.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_permissions.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_permissions.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_permissions.version_num IS '版本号';

-- ========== 4. 菜单表 ==========
COMMENT ON TABLE sys_menus IS '菜单信息表';
COMMENT ON COLUMN sys_menus.id IS '主键ID';
COMMENT ON COLUMN sys_menus.menu_name IS '菜单名称';
COMMENT ON COLUMN sys_menus.menu_code IS '菜单编码';
COMMENT ON COLUMN sys_menus.menu_path IS '菜单路径';
COMMENT ON COLUMN sys_menus.parent_id IS '父菜单ID';
COMMENT ON COLUMN sys_menus.sort_order IS '显示顺序';

COMMENT ON COLUMN sys_menus.creation_date IS '创建时间';
COMMENT ON COLUMN sys_menus.created_by IS '创建人';
COMMENT ON COLUMN sys_menus.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_menus.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_menus.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_menus.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_menus.version_num IS '版本号';

-- ========== 5. 用户-角色关联表 ==========
COMMENT ON TABLE sys_user_roles IS '用户与角色关联表';
COMMENT ON COLUMN sys_user_roles.id IS '主键ID';
COMMENT ON COLUMN sys_user_roles.user_id IS '用户ID';
COMMENT ON COLUMN sys_user_roles.role_id IS '角色ID';

COMMENT ON COLUMN sys_user_roles.creation_date IS '创建时间';
COMMENT ON COLUMN sys_user_roles.created_by IS '创建人';
COMMENT ON COLUMN sys_user_roles.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_user_roles.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_user_roles.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_user_roles.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_user_roles.version_num IS '版本号';

-- ========== 6. 角色-权限关联表 ==========
COMMENT ON TABLE sys_role_permissions IS '角色与权限关联表';
COMMENT ON COLUMN sys_role_permissions.id IS '主键ID';
COMMENT ON COLUMN sys_role_permissions.role_id IS '角色ID';
COMMENT ON COLUMN sys_role_permissions.permission_id IS '权限ID';

COMMENT ON COLUMN sys_role_permissions.creation_date IS '创建时间';
COMMENT ON COLUMN sys_role_permissions.created_by IS '创建人';
COMMENT ON COLUMN sys_role_permissions.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_role_permissions.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_role_permissions.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_role_permissions.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_role_permissions.version_num IS '版本号';

-- ========== 7. 角色-菜单关联表 ==========
COMMENT ON TABLE sys_role_menus IS '角色与菜单关联表';
COMMENT ON COLUMN sys_role_menus.id IS '主键ID';
COMMENT ON COLUMN sys_role_menus.role_id IS '角色ID';
COMMENT ON COLUMN sys_role_menus.menu_id IS '菜单ID';

COMMENT ON COLUMN sys_role_menus.creation_date IS '创建时间';
COMMENT ON COLUMN sys_role_menus.created_by IS '创建人';
COMMENT ON COLUMN sys_role_menus.last_update_date IS '修改时间';
COMMENT ON COLUMN sys_role_menus.last_updated_by IS '修改人';
COMMENT ON COLUMN sys_role_menus.last_update_login IS '最后登录ID';
COMMENT ON COLUMN sys_role_menus.delete_flag IS '删除标识，Y/N';
COMMENT ON COLUMN sys_role_menus.version_num IS '版本号';