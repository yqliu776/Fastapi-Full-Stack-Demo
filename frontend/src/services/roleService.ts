import apiClient from '@/api/client';
import type {
  Role,
  RoleCreate,
  RoleUpdate,
  RolePermissionOperation,
  RoleMenuOperation,
  RolePermissionReplace,
  RoleMenuReplace
} from '@/types/role';
import type { Permission } from '@/types/permission';
import type { Menu } from '@/types/menu';
import type { ListResponse, SingleResponse, OperationResponse } from '@/types/api';

// 接口类型定义（单一数据源：src/types/）
export type {
  Role,
  RoleCreate,
  RoleUpdate,
  RolePermissionOperation,
  RoleMenuOperation,
  RolePermissionReplace,
  RoleMenuReplace
};
export type { Permission, Menu };
export type { ListResponse, SingleResponse, OperationResponse };

// 角色管理API
export const roleService = {
  // 获取角色列表
  async getRoles(params: { skip?: number; limit?: number; role_name?: string; role_code?: string; deleted?: boolean } = {}) {
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

  // 恢复角色
  async restoreRole(roleId: number) {
    try {
      const response = await apiClient.post<SingleResponse<Role>>(`/roles/restore/${roleId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 彻底删除角色
  async purgeRole(roleId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/roles/purge/${roleId}`);
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

  // 保存角色权限完整集合
  async replacePermissionsForRole(roleId: number, operation: RolePermissionReplace) {
    try {
      const response = await apiClient.put<SingleResponse<OperationResponse>>(`/roles/${roleId}/permissions`, operation);
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
  },

  // 保存角色菜单完整集合
  async replaceMenusForRole(roleId: number, operation: RoleMenuReplace) {
    try {
      const response = await apiClient.put<SingleResponse<OperationResponse>>(`/roles/${roleId}/menus`, operation);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default roleService; 
