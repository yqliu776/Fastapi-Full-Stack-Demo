-- 初始化日期变量
SET @current_date = NOW();
SET @admin_user = '-1';

-- ========== 1. 初始化角色 ==========
INSERT INTO sys_roles
(role_name, role_code, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('超级管理员', 'ROLE_SUPER_ADMIN', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

-- ========== 2. 初始化权限 ==========
INSERT INTO sys_permissions
(permission_name, permission_code, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('用户管理', 'USER_MANAGE', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('角色管理', 'ROLE_MANAGE', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('权限管理', 'PERMISSION_MANAGE', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('菜单管理', 'MENU_MANAGE', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('系统设置', 'SYSTEM_SETTING', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

-- ========== 3. 初始化菜单 ==========
INSERT INTO sys_menus
(menu_name, menu_code, menu_path, parent_id, sort_order, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('系统管理', 'SYSTEM', '/system', NULL, 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

SET @system_menu_id = LAST_INSERT_ID();

INSERT INTO sys_menus
(menu_name, menu_code, menu_path, parent_id, sort_order, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('用户管理', 'USER', '/system/user', @system_menu_id, 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('角色管理', 'ROLE', '/system/role', @system_menu_id, 2, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('权限管理', 'PERMISSION', '/system/permission', @system_menu_id, 3, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('菜单管理', 'MENU', '/system/menu', @system_menu_id, 4, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

-- ========== 4. 创建超级管理员用户 ==========
-- 密码为 Admin@123，使用bcrypt加密
INSERT INTO sys_users
(user_name, password, phone_number, email, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('admin', '$2b$12$F1nTxUIU9tsiA32SF3Pz1Okp9TBrLNa20zxXVI6KNja47M01M0Jea', '18888888888', 'admin@example.com', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

SET @admin_id = LAST_INSERT_ID();
SET @role_id = (SELECT id FROM sys_roles WHERE role_code = 'ROLE_SUPER_ADMIN' LIMIT 1);

-- ========== 5. 关联用户和角色 ==========
INSERT INTO sys_user_roles
(user_id, role_id, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
(@admin_id, @role_id, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

-- ========== 6. 为超级管理员角色关联所有权限 ==========
INSERT INTO sys_role_permissions
(role_id, permission_id, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
SELECT
  @role_id, id, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1
FROM
  sys_permissions;

-- ========== 7. 为超级管理员角色关联所有菜单 ==========
INSERT INTO sys_role_menus
(role_id, menu_id, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
SELECT
  @role_id, id, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1
FROM
  sys_menus;