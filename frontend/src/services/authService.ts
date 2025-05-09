import axios from 'axios';

// 创建自定义错误接口
interface CustomError extends Error {
  response?: any;
}

// 创建axios实例
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

// Token操作相关函数
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export function setToken(token: string): void {
  document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=86400; SameSite=Strict`;
}

export function getToken(): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${TOKEN_KEY}=([^;]+)`));
  return match ? match[2] : null;
}

export function setRefreshToken(token: string): void {
  document.cookie = `${REFRESH_TOKEN_KEY}=${token}; path=/; max-age=604800; SameSite=Strict`;
}

export function getRefreshToken(): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${REFRESH_TOKEN_KEY}=([^;]+)`));
  return match ? match[2] : null;
}

export function clearTokens(): void {
  document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
  document.cookie = `${REFRESH_TOKEN_KEY}=; path=/; max-age=0`;
}

// API调用
export async function login(username: string, password: string) {
  try {
    const response = await apiClient.post('/auth/login', {
      username,
      password
    });
    if (response.data.code === 200) {
      const { access_token, refresh_token } = response.data.data;
      setToken(access_token);
      setRefreshToken(refresh_token);
    }
    return response.data;
  } catch (error) {
    return Promise.reject(error);
  }
}

export async function refreshToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return Promise.reject(new Error('没有刷新令牌'));
  }
  
  try {
    const response = await apiClient.post('/auth/refresh', null, {
      params: { refresh_token: refreshToken },
    });
    
    if (response.data.code === 200) {
      const { access_token, refresh_token } = response.data.data;
      setToken(access_token);
      if (refresh_token) {
        setRefreshToken(refresh_token);
      }
      return response.data;
    } else {
      return Promise.reject(new Error('刷新令牌失败'));
    }
  } catch (error) {
    clearTokens();
    return Promise.reject(error);
  }
}

export async function getUserInfo() {
  try {
    const response = await apiClient.get('/auth/me');
    return response.data;
  } catch (error) {
    return Promise.reject(error);
  }
}

export function logout() {
  try {
    console.log('authService.logout called');
    clearTokens();
    console.log('Tokens cleared');
    // 使用window.location而不是router，确保完全刷新页面
    console.log('Redirecting to login page');
    window.location.href = '/login';
  } catch (error) {
    console.error('登出过程中发生错误:', error);
    // 即使发生错误，也尝试重定向到登录页
    window.location.href = '/login';
  }
}

export async function register(user_name: string, email: string, phone_number: string, password: string) {
  try {
    const response = await apiClient.post('/users/register', {
      user_name,
      email,
      phone_number,
      password
    });
    return response.data;
  } catch (error) {
    return Promise.reject(error);
  }
} 