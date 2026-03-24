import axios from 'axios';
import { getToken, getRefreshToken, setToken, setRefreshToken, clearTokens } from '@/services/authService';

interface CustomError extends Error {
  response?: any;
}

let isRefreshing = false;
let pendingRequests: Array<(token: string) => void> = [];

function onTokenRefreshed(token: string) {
  pendingRequests.forEach(cb => cb(token));
  pendingRequests = [];
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(apiClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshTokenValue = getRefreshToken();
        if (!refreshTokenValue) throw new Error('No refresh token');

        const response = await axios.post(
          `${apiClient.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshTokenValue }
        );

        if (response.data.code === 200) {
          const { access_token, refresh_token } = response.data.data;
          setToken(access_token);
          if (refresh_token) setRefreshToken(refresh_token);
          onTokenRefreshed(access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
        throw new Error('Refresh failed');
      } catch (refreshError) {
        clearTokens();
        pendingRequests = [];
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.status === 403) {
      const permissionError: CustomError = new Error(
        error.response.data.message || '您没有执行此操作的权限'
      );
      permissionError.name = 'PermissionError';
      permissionError.response = error.response;
      return Promise.reject(permissionError);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
