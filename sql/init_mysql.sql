SET NAMES utf8mb4;

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
('API限流管理', 'RATE_LIMIT_MANAGE', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('系统设置', 'SYSTEM_SETTING', @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

-- ========== 2.1 初始化API权限绑定 ==========
INSERT INTO sys_api_permissions
(method, path_pattern, permission_code, description, enabled, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('GET', '/users/', 'USER_MANAGE', '获取用户列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/users/admin/create', 'USER_MANAGE', '管理员创建用户', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/users/list', 'USER_MANAGE', '获取用户列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/users/detail/{user_id}', 'USER_MANAGE', '获取用户详情', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/users/update/{user_id}', 'USER_MANAGE', '更新用户信息', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/users/delete/{user_id}', 'USER_MANAGE', '删除用户', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/users/reset-password/{user_id}', 'USER_MANAGE', '重置用户密码', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/users/assign-roles/{user_id}', 'USER_MANAGE', '分配用户角色', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/users/remove-roles/{user_id}', 'USER_MANAGE', '删除用户角色', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/roles', 'ROLE_MANAGE', '创建角色', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/roles', 'ROLE_MANAGE', '获取角色列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/roles/{role_id}', 'ROLE_MANAGE', '获取角色详情', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/roles/{role_id}', 'ROLE_MANAGE', '更新角色', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/roles/{role_id}', 'ROLE_MANAGE', '删除角色', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/roles/{role_id}/permissions', 'ROLE_MANAGE', '为角色分配权限', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/roles/{role_id}/permissions', 'ROLE_MANAGE', '移除角色的权限', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/roles/{role_id}/permissions', 'ROLE_MANAGE', '保存角色权限完整集合', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/roles/{role_id}/menus', 'ROLE_MANAGE', '为角色分配菜单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/roles/{role_id}/menus', 'ROLE_MANAGE', '移除角色的菜单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/roles/{role_id}/menus', 'ROLE_MANAGE', '保存角色菜单完整集合', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/permissions', 'PERMISSION_MANAGE', '创建权限', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/permissions', 'PERMISSION_MANAGE', '获取权限列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/permissions/api-bindings', 'PERMISSION_MANAGE', '获取API权限绑定列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/permissions/api-bindings', 'PERMISSION_MANAGE', '创建API权限绑定', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/permissions/api-bindings/{api_permission_id}', 'PERMISSION_MANAGE', '更新API权限绑定', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/permissions/api-bindings/{api_permission_id}', 'PERMISSION_MANAGE', '删除API权限绑定', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/permissions/role/{role_id}', 'PERMISSION_MANAGE', '获取角色拥有的权限', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/permissions/{permission_id}', 'PERMISSION_MANAGE', '获取权限详情', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/permissions/{permission_id}', 'PERMISSION_MANAGE', '更新权限', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/permissions/{permission_id}', 'PERMISSION_MANAGE', '删除权限', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/menus', 'MENU_MANAGE', '创建菜单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/menus', 'MENU_MANAGE', '获取菜单列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/menus/tree', 'MENU_MANAGE', '获取菜单树', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/menus/role/{role_id}', 'MENU_MANAGE', '获取角色拥有的菜单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/menus/{menu_id}', 'MENU_MANAGE', '获取菜单详情', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/menus/{menu_id}', 'MENU_MANAGE', '更新菜单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/menus/{menu_id}', 'MENU_MANAGE', '删除菜单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/rate-limit/stats', 'RATE_LIMIT_MANAGE', '获取限流统计信息', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/rate-limit/whitelist', 'RATE_LIMIT_MANAGE', '添加到白名单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/rate-limit/whitelist/{identifier}', 'RATE_LIMIT_MANAGE', '从白名单移除', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/rate-limit/whitelist', 'RATE_LIMIT_MANAGE', '获取白名单列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/rate-limit/blacklist', 'RATE_LIMIT_MANAGE', '添加到黑名单', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('DELETE', '/rate-limit/blacklist/{identifier}', 'RATE_LIMIT_MANAGE', '从黑名单移除', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/rate-limit/blacklist', 'RATE_LIMIT_MANAGE', '获取黑名单列表', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('POST', '/rate-limit/check', 'RATE_LIMIT_MANAGE', '检查限流状态', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('GET', '/rate-limit/config', 'RATE_LIMIT_MANAGE', '获取限流配置', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('PUT', '/rate-limit/config', 'RATE_LIMIT_MANAGE', '更新限流配置', 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

-- ========== 3. 初始化菜单 ==========
INSERT INTO sys_menus
(menu_name, menu_code, menu_path, component_key, parent_id, sort_order, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('系统管理', 'SYSTEM', '/system', 'dashboard', NULL, 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

SET @system_menu_id = LAST_INSERT_ID();

INSERT INTO sys_menus
(menu_name, menu_code, menu_path, component_key, parent_id, sort_order, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
VALUES
('用户管理', 'USER', '/system/user', 'user', @system_menu_id, 1, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('角色管理', 'ROLE', '/system/role', 'role', @system_menu_id, 2, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('权限管理', 'PERMISSION', '/system/permission', 'permission', @system_menu_id, 3, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('菜单管理', 'MENU', '/system/menu', 'menu', @system_menu_id, 4, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('API限流管理', 'API_RATE_LIMIT', '/system/api-rate-limit', 'rate_limit', @system_menu_id, 5, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1),
('API文档', 'API_DOCS', '/system/swagger-ui', 'swagger', @system_menu_id, 6, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

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
