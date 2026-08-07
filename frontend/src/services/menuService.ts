import apiClient from '@/api/client';
import type { Menu, MenuCreate, MenuUpdate } from '@/types/menu';
import type { ListResponse, SingleResponse, OperationResponse } from '@/types/api';

// 菜单接口定义（单一数据源：src/types/menu.ts）
export type { Menu, MenuCreate, MenuUpdate };
export type { ListResponse, SingleResponse, OperationResponse };

// 菜单管理API
export const menuService = {
  // 获取菜单列表
  async getMenus(params: { skip?: number; limit?: number; menu_name?: string; deleted?: boolean } = {}) {
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

  // 获取当前用户菜单列表
  async getCurrentMenus() {
    try {
      const response = await apiClient.get<ListResponse<Menu>>('/menus/current');
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 获取当前用户菜单树
  async getCurrentMenuTree() {
    try {
      const response = await apiClient.get<SingleResponse<Menu[]>>('/menus/current/tree');
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
  },

  // 恢复菜单
  async restoreMenu(menuId: number) {
    try {
      const response = await apiClient.post<SingleResponse<Menu>>(`/menus/restore/${menuId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 彻底删除菜单
  async purgeMenu(menuId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/menus/purge/${menuId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default menuService; 
