// 权限接口定义

export interface Permission {
  id: number;
  permission_name: string;
  permission_code: string;
  delete_flag?: string; // 删除标识，N正常/Y已软删除
  creation_date: string;
  last_update_date: string;
}

export interface PermissionCreate {
  permission_name: string;
  permission_code: string;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface PermissionUpdate {
  permission_name?: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface ApiPermission {
  id: number;
  method: string;
  path_pattern: string;
  permission_code: string;
  description?: string | null;
  enabled: boolean;
  delete_flag?: string; // 删除标识，N正常/Y已软删除
  creation_date: string;
  last_update_date: string;
}

export interface ApiPermissionCreate {
  method: string;
  path_pattern: string;
  permission_code: string;
  description?: string;
  enabled: boolean;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface ApiPermissionUpdate {
  method?: string;
  path_pattern?: string;
  permission_code?: string;
  description?: string;
  enabled?: boolean;
  last_updated_by: string;
  last_update_login: string;
}
