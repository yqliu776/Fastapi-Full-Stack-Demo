import apiClient from '@/api/client';
import type {
  Permission,
  PermissionCreate,
  PermissionUpdate,
  ApiPermission,
  ApiPermissionCreate,
  ApiPermissionUpdate
} from '@/types/permission';
import type { ListResponse, SingleResponse, OperationResponse } from '@/types/api';

// 权限接口定义（单一数据源：src/types/permission.ts）
export type {
  Permission,
  PermissionCreate,
  PermissionUpdate,
  ApiPermission,
  ApiPermissionCreate,
  ApiPermissionUpdate
};
export type { ListResponse, SingleResponse, OperationResponse };

// 权限管理API
export const permissionService = {
  // 获取权限列表
  async getPermissions(params: { skip?: number; limit?: number; permission_name?: string; permission_code?: string; deleted?: boolean } = {}) {
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
  },

  // 恢复权限
  async restorePermission(permissionId: number) {
    try {
      const response = await apiClient.post<SingleResponse<Permission>>(`/permissions/restore/${permissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 彻底删除权限
  async purgePermission(permissionId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/permissions/purge/${permissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 获取API权限绑定列表
  async getApiPermissions(params: { skip?: number; limit?: number; method?: string; path_pattern?: string; permission_code?: string; deleted?: boolean } = {}) {
    try {
      const response = await apiClient.get<ListResponse<ApiPermission>>('/permissions/api-bindings', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 创建API权限绑定
  async createApiPermission(apiPermissionData: ApiPermissionCreate) {
    try {
      const response = await apiClient.post<SingleResponse<ApiPermission>>('/permissions/api-bindings', apiPermissionData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 更新API权限绑定
  async updateApiPermission(apiPermissionId: number, apiPermissionData: ApiPermissionUpdate) {
    try {
      const response = await apiClient.put<SingleResponse<ApiPermission>>(`/permissions/api-bindings/${apiPermissionId}`, apiPermissionData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 删除API权限绑定
  async deleteApiPermission(apiPermissionId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/permissions/api-bindings/${apiPermissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 恢复API权限绑定
  async restoreApiPermission(apiPermissionId: number) {
    try {
      const response = await apiClient.post<SingleResponse<ApiPermission>>(`/permissions/api-bindings/restore/${apiPermissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 彻底删除API权限绑定
  async purgeApiPermission(apiPermissionId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/permissions/api-bindings/purge/${apiPermissionId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default permissionService; 
