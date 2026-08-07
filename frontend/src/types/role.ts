import type { Permission } from './permission';
import type { Menu } from './menu';

// 角色接口定义
export interface Role {
  id: number;
  role_name: string;
  role_code: string;
  delete_flag?: string; // 删除标识，N正常/Y已软删除
  creation_date: string;
  last_update_date: string;
  permissions: Permission[]; // 角色拥有的权限列表
  menus: Menu[]; // 角色拥有的菜单列表
}

export interface RoleCreate {
  role_name: string;
  role_code: string;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface RoleUpdate {
  role_name?: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface RolePermissionOperation {
  permission_ids: number[];
  operator: string;
  operation_login: string;
  role_id: number;
}

export interface RoleMenuOperation {
  menu_ids: number[];
  operator: string;
  operation_login: string;
  role_id: number;
}

export interface RolePermissionReplace {
  permission_ids: number[];
}

export interface RoleMenuReplace {
  menu_ids: number[];
}
