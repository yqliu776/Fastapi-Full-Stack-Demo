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

// 权限接口定义
export interface Permission {
  id: number;
  permission_name: string;
  permission_code: string;
  creation_date: string;
  last_update_date: string;
}

export interface ListResponse<T> {
  code: number;
  message: string;
  data: {
    items: T[];
    total: number;
  };
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
      const response = await apiClient.get<ListResponse<Permission>>(`/roles/${roleId}/permissions`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default permissionService; 