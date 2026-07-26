import apiClient from '@/api/client';

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

export interface ApiPermission {
  id: number;
  method: string;
  path_pattern: string;
  permission_code: string;
  description?: string | null;
  enabled: boolean;
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
  },

  // 获取API权限绑定列表
  async getApiPermissions(params: { skip?: number; limit?: number; method?: string; path_pattern?: string; permission_code?: string } = {}) {
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
  }
};

export default permissionService; 
