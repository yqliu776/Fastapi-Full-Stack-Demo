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

// 权限接口定义
export interface Permission {
  id: number;
  permission_name: string;
  permission_code: string;
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

export interface OperationResponse {
  success: boolean;
  message: string;
}

// 权限管理API
export const permissionService = {
  // 获取权限列表
  async getPermissions(params: { skip?: number; limit?: number; permission_name?: string; permission_code?: string } = {}) {
    try {
      const response = await apiClient.get<ListResponse<Permission>>('/permissions', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  
  // 获取角色拥有的权限
  async getRolePermissions(roleId: number) {
    try {
      const response = await apiClient.get<ListResponse<Permission>>(`/permissions/role/${roleId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 获取权限详情
  async getPermission(permissionId: number) {
    try {
      const response = await apiClient.get<SingleResponse<Permission>>(`/permissions/${permissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 创建权限
  async createPermission(permissionData: PermissionCreate) {
    try {
      const response = await apiClient.post<SingleResponse<Permission>>('/permissions', permissionData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 更新权限
  async updatePermission(permissionId: number, permissionData: PermissionUpdate) {
    try {
      const response = await apiClient.put<SingleResponse<Permission>>(`/permissions/${permissionId}`, permissionData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 删除权限
  async deletePermission(permissionId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/permissions/${permissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default permissionService; 