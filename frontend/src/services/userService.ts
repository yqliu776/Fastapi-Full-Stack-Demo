import apiClient from '@/api/client';
import type {
  User,
  UserCreate,
  UserUpdate,
  UserRoleOperation,
  UserRoleAssign,
  UserRoleRemove,
  UserPasswordUpdate
} from '@/types/user';
import type { ListResponse, SingleResponse, OperationResponse } from '@/types/api';

// 用户接口定义（单一数据源：src/types/user.ts）
export type {
  User,
  UserCreate,
  UserUpdate,
  UserRoleOperation,
  UserRoleAssign,
  UserRoleRemove,
  UserPasswordUpdate
};
export type { ListResponse, SingleResponse, OperationResponse };

// 用户管理API
export const userService = {
  // 获取用户列表
  async getUsers(params: { skip?: number; limit?: number; user_name?: string; email?: string; status?: string; deleted?: boolean } = {}) {
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

  // 恢复用户
  async restoreUser(userId: number) {
    try {
      const response = await apiClient.post<SingleResponse<User>>(`/users/restore/${userId}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  // 彻底删除用户
  async purgeUser(userId: number) {
    try {
      const response = await apiClient.delete<SingleResponse<OperationResponse>>(`/users/purge/${userId}`);
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