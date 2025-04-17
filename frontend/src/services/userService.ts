import axios from 'axios';
import { getToken, refreshToken, clearTokens } from './authService';

// 创建axios实例或复用已有实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 拦截器配置
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    if (error.response && error.response.status === 401) {
      if (error.response.data.detail === "无效的身份凭证") {
        // 尝试刷新令牌
        try {
          await refreshToken();
          // 重新发送原请求
          const originalRequest = error.config;
          originalRequest.headers.Authorization = `Bearer ${getToken()}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // 刷新令牌失败，清除所有凭证并跳转到登录页面
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

// 用户接口定义
export interface User {
  id: number;
  user_name: string;
  email: string;
  phone_number: string;  // 从phone改为phone_number匹配后端返回字段
  delete_flag: string; // 删除标识，Y/N，Y表示已删除/禁用，N表示正常/启用
  creation_date: string;
  last_update_date: string;
  roles: { id: number; role_name: string; role_code: string }[]; // 用户关联的角色列表
}

export interface UserCreate {
  user_name: string;
  email: string;
  phone_number: string;
  password: string;
  delete_flag: string;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
  role_codes: string[]; // 用户角色代码列表，如 ["ROLE_USER"]
}

export interface UserUpdate {
  user_name?: string;
  email?: string;
  phone_number?: string;
  delete_flag?: string;
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

export interface ListResponse<T> {
  code: number;
  message: string;
  data: {
    items: T[];
    total: number;
  };
}

export interface SingleResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 操作响应类型
export interface OperationResponse {
  success: boolean;
  message?: string;
}

// 用户管理API
export const userService = {
  // 获取用户列表
  async getUsers(params: { skip?: number; limit?: number; user_name?: string; email?: string; delete_flag?: string } = {}) {
    try {
      const response = await apiClient.get<ListResponse<User>>('/users/list', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 创建用户
  async createUser(userData: UserCreate) {
    try {
      const response = await apiClient.post<SingleResponse<User>>('/users/admin/create', userData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 获取用户详情
  async getUser(userId: number) {
    try {
      const response = await apiClient.get<SingleResponse<User>>(`/users/detail/${userId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 更新用户
  async updateUser(userId: number, userData: UserUpdate) {
    try {
      const response = await apiClient.put<SingleResponse<User>>(`/users/update/${userId}`, userData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 删除用户
  async deleteUser(userId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/users/delete/${userId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 修改用户密码
  async updateUserPassword(userId: number, passwordData: UserPasswordUpdate) {
    try {
      const response = await apiClient.post<SingleResponse<OperationResponse>>(`/users/reset-password/${userId}`, passwordData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 为用户分配角色
  async assignRolesToUser(userId: number, roleData: UserRoleAssign) {
    try {
      const response = await apiClient.post<SingleResponse<OperationResponse>>(`/users/assign-roles/${userId}`, roleData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 移除用户的角色
  async removeRolesFromUser(userId: number, roleData: UserRoleRemove) {
    try {
      const response = await apiClient.post<SingleResponse<OperationResponse>>(`/users/remove-roles/${userId}`, roleData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default userService; 