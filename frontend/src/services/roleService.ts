import axios from 'axios';
import { getToken, refreshToken, clearTokens } from './authService';

// 创建自定义错误接口
interface CustomError extends Error {
  response?: any;
}

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
    
    // 处理403权限不足错误
    if (error.response && error.response.status === 403) {
      // 创建一个新的错误对象，包含更友好的信息
      const permissionError: CustomError = new Error(error.response.data.message || "您没有执行此操作的权限");
      permissionError.name = "PermissionError";
      
      // 将原始响应数据附加到错误对象，以便组件能够访问
      permissionError.response = error.response;
      
      return Promise.reject(permissionError);
    }
    
    return Promise.reject(error);
  }
);

// 接口类型定义
export interface Permission {
  id: number;
  permission_name: string;
  permission_code: string;
  creation_date: string;
  last_update_date: string;
}

export interface Menu {
  id: number;
  menu_name: string;
  menu_code: string;
  menu_path: string;
  parent_id?: number;
  sort_order?: number;
  creation_date: string;
  last_update_date: string;
  children?: Menu[];
}

// 角色接口定义
export interface Role {
  id: number;
  role_name: string;
  role_code: string;
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

// 角色管理API
export const roleService = {
  // 获取角色列表
  async getRoles(params: { skip?: number; limit?: number; role_name?: string; role_code?: string } = {}) {
    try {
      const response = await apiClient.get<ListResponse<Role>>('/roles', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 创建角色
  async createRole(roleData: RoleCreate) {
    try {
      const response = await apiClient.post<SingleResponse<Role>>('/roles', roleData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 获取角色详情
  async getRole(roleId: number) {
    try {
      const response = await apiClient.get<SingleResponse<Role>>(`/roles/${roleId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 更新角色
  async updateRole(roleId: number, roleData: RoleUpdate) {
    try {
      const response = await apiClient.put<SingleResponse<Role>>(`/roles/${roleId}`, roleData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 删除角色
  async deleteRole(roleId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/roles/${roleId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 为角色分配权限
  async assignPermissionsToRole(roleId: number, operation: RolePermissionOperation) {
    try {
      const response = await apiClient.post<SingleResponse<OperationResponse>>(`/roles/${roleId}/permissions`, operation);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 移除角色的权限
  async removePermissionsFromRole(roleId: number, operation: RolePermissionOperation) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/roles/${roleId}/permissions`, {
        data: operation
      });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 为角色分配菜单
  async assignMenusToRole(roleId: number, operation: RoleMenuOperation) {
    try {
      const response = await apiClient.post<SingleResponse<OperationResponse>>(`/roles/${roleId}/menus`, operation);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 移除角色的菜单
  async removeMenusFromRole(roleId: number, operation: RoleMenuOperation) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/roles/${roleId}/menus`, {
        data: operation
      });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default roleService; 