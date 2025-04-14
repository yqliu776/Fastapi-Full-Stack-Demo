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

// 菜单接口定义
export interface Menu {
  id: number;
  menu_name: string;
  menu_code: string;
  menu_path: string;
  parent_id?: number;
  sort_order: number;
  creation_date: string;
  last_update_date: string;
  children?: Menu[];
}

export interface MenuCreate {
  menu_name: string;
  menu_code: string;
  menu_path: string;
  parent_id?: number;
  sort_order?: number;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface MenuUpdate {
  menu_name?: string;
  menu_path?: string;
  parent_id?: number;
  sort_order?: number;
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

// 菜单管理API
export const menuService = {
  // 获取菜单列表
  async getMenus(params: { skip?: number; limit?: number; menu_name?: string } = {}) {
    try {
      const response = await apiClient.get<ListResponse<Menu>>('/menus', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  
  // 获取菜单树
  async getMenuTree() {
    try {
      const response = await apiClient.get<SingleResponse<Menu[]>>('/menus/tree');
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  
  // 获取角色拥有的菜单
  async getRoleMenus(roleId: number) {
    try {
      const response = await apiClient.get<ListResponse<Menu>>(`/menus/role/${roleId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 获取菜单详情
  async getMenu(menuId: number) {
    try {
      const response = await apiClient.get<SingleResponse<Menu>>(`/menus/${menuId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 创建菜单
  async createMenu(menuData: MenuCreate) {
    try {
      const response = await apiClient.post<SingleResponse<Menu>>('/menus', menuData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 更新菜单
  async updateMenu(menuId: number, menuData: MenuUpdate) {
    try {
      const response = await apiClient.put<SingleResponse<Menu>>(`/menus/${menuId}`, menuData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 删除菜单
  async deleteMenu(menuId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/menus/${menuId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default menuService; 