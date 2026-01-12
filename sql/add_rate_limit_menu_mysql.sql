-- 添加API限流管理菜单 (MySQL版本)
-- 在系统管理下添加API限流管理菜单

-- 设置变量
SET @current_date = NOW();
SET @admin_user = '-1';
SET @system_menu_id = (SELECT id FROM sys_menus WHERE menu_code = 'SYSTEM' AND delete_flag = 'N' LIMIT 1);

-- 检查是否已经存在API限流菜单
SELECT COUNT(*) INTO @exists FROM sys_menus WHERE menu_code = 'API_RATE_LIMIT' AND delete_flag = 'N';

-- 如果不存在，则添加API限流管理菜单
IF @exists = 0 THEN
    INSERT INTO sys_menus
    (menu_name, menu_code, menu_path, parent_id, sort_order, creation_date, created_by, last_update_date, last_updated_by, last_update_login, delete_flag, version_num)
    VALUES
    ('API限流管理', 'API_RATE_LIMIT', '/system/api-rate-limit', @system_menu_id, 5, @current_date, @admin_user, @current_date, @admin_user, @admin_user, 'N', 1);

    SELECT 'API限流管理菜单添加成功' AS result;
ELSE
    SELECT 'API限流管理菜单已存在' AS result;
END IF;