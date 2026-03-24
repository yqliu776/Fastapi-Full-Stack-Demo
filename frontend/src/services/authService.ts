import apiClient from '@/api/client';

// Token操作相关函数
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

const isSecure = window.location.protocol === 'https:';
const secureSuffix = isSecure ? '; Secure' : '';

export function setToken(token: string): void {
  document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=86400; SameSite=Strict${secureSuffix}`;
}

export function getToken(): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${TOKEN_KEY}=([^;]+)`));
  return match ? match[2] : null;
}

export function setRefreshToken(token: string): void {
  document.cookie = `${REFRESH_TOKEN_KEY}=${token}; path=/; max-age=604800; SameSite=Strict${secureSuffix}`;
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
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
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

export async function logout() {
  try {
    await apiClient.post('/auth/logout').catch(() => {});
    clearTokens();
    const { resetDynamicRoutesFlag } = await import('@/router');
    resetDynamicRoutesFlag();
    window.location.href = '/login';
  } catch (error) {
    console.error('登出过程中发生错误:', error);
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