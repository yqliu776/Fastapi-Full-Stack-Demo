// 用户接口定义
export interface User {
  id: number;
  user_name: string;
  email: string;
  phone_number: string; // 匹配后端返回字段
  status: string; // 用户状态，N启用/Y禁用
  delete_flag?: string; // 删除标识，N正常/Y已软删除
  creation_date: string;
  last_update_date: string;
  roles: { id: number; role_name: string; role_code: string }[]; // 用户关联的角色列表
}

export interface UserCreate {
  user_name: string;
  email: string;
  phone_number: string;
  password: string;
  status: string;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
  role_codes: string[]; // 用户角色代码列表，如 ["ROLE_USER"]
}

export interface UserUpdate {
  user_name?: string;
  email?: string;
  phone_number?: string;
  status?: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface UserRoleOperation {
  role_ids: number[];
  operator: string;
  operation_login: string;
  user_id: number;
}

// 角色分配请求数据定义
export interface UserRoleAssign {
  role_codes: string[];
  operator?: string;
  operation_login?: string;
}

// 角色移除请求数据定义
export interface UserRoleRemove {
  role_codes: string[];
  operator?: string;
  operation_login?: string;
}

export interface UserPasswordUpdate {
  password: string;
  last_updated_by: string;
  last_update_login: string;
}
