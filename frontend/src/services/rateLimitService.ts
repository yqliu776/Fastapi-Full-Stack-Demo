import axios from 'axios';
import { getToken, refreshToken, clearTokens } from './authService';

// 响应类型定义
export interface ResponseModel<T = any> {
  code: number;
  message: string;
  data: T;
}

// 限流配置接口
export interface RateLimitConfig {
  enabled: boolean;
  algorithm: string;
  storage: string;
  default_requests: number;
  default_burst: number;
  block_duration: number;
  enable_whitelist: boolean;
  enable_blacklist: boolean;
  log_violations: boolean;
}

// 白名单/黑名单条目接口
export interface ListEntry {
  identifier: string;
  created_at: string;
  expire_time?: number;
}

// 限流检查结果接口
export interface RateLimitCheckResult {
  allowed: boolean;
  remaining: number;
  reset_time: number;
  limit: number;
  retry_after?: number;
}

// 限流统计接口
export interface RateLimitStats {
  scope: string;
  identifier: string;
  rate_limit_key: string;
  whitelisted: boolean;
  blacklisted: boolean;
}

// 限流作用域枚举
export type RateLimitScope = 'global' | 'ip' | 'user' | 'endpoint' | 'ip_user' | 'ip_endpoint' | 'user_endpoint' | 'ip_user_endpoint';

// 限流算法枚举
export type RateLimitAlgorithm = 'token_bucket' | 'sliding_window' | 'fixed_window';

// 限流存储枚举
export type RateLimitStorage = 'redis' | 'memory' | 'database';

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
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

// 限流管理API服务
export const rateLimitService = {
  /**
   * 获取限流配置
   */
  async getRateLimitConfig(): Promise<ResponseModel<RateLimitConfig>> {
    try {
      const response = await apiClient.get<ResponseModel<RateLimitConfig>>('/rate-limit/config');
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 获取限流统计信息
   */
  async getRateLimitStats(
    scope: RateLimitScope,
    identifier: string,
    endpoint?: string,
    userId?: string
  ): Promise<ResponseModel<RateLimitStats>> {
    try {
      const params = {
        scope,
        identifier,
        ...(endpoint && { endpoint }),
        ...(userId && { user_id: userId })
      };
      const response = await apiClient.get<ResponseModel<RateLimitStats>>('/rate-limit/stats', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 检查限流状态
   */
  async checkRateLimit(
    scope: RateLimitScope,
    identifier: string,
    endpoint?: string,
    userId?: string
  ): Promise<ResponseModel<RateLimitCheckResult>> {
    try {
      const params = {
        scope,
        identifier,
        ...(endpoint && { endpoint }),
        ...(userId && { user_id: userId })
      };
      const response = await apiClient.get<ResponseModel<RateLimitCheckResult>>('/rate-limit/check', { params });
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 获取白名单列表
   */
  async getWhitelist(): Promise<ResponseModel<ListEntry[]>> {
    try {
      const response = await apiClient.get<ResponseModel<ListEntry[]>>('/rate-limit/whitelist');
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 添加到白名单
   */
  async addToWhitelist(identifier: string, expireTime?: number): Promise<ResponseModel> {
    try {
      const requestData = {
        identifier,
        expire_time: expireTime
      };
      const response = await apiClient.post<ResponseModel>('/rate-limit/whitelist', requestData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 从白名单移除
   */
  async removeFromWhitelist(identifier: string): Promise<ResponseModel> {
    try {
      const response = await apiClient.delete<ResponseModel>(`/rate-limit/whitelist/${identifier}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 获取黑名单列表
   */
  async getBlacklist(): Promise<ResponseModel<ListEntry[]>> {
    try {
      const response = await apiClient.get<ResponseModel<ListEntry[]>>('/rate-limit/blacklist');
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 添加到黑名单
   */
  async addToBlacklist(identifier: string, expireTime?: number): Promise<ResponseModel> {
    try {
      const requestData = {
        identifier,
        expire_time: expireTime
      };
      const response = await apiClient.post<ResponseModel>('/rate-limit/blacklist', requestData);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  },

  /**
   * 从黑名单移除
   */
  async removeFromBlacklist(identifier: string): Promise<ResponseModel> {
    try {
      const response = await apiClient.delete<ResponseModel>(`/rate-limit/blacklist/${identifier}`);
      return response.data;
    } catch (error) {
      return Promise.reject(error);
    }
  }
};

export default rateLimitService;