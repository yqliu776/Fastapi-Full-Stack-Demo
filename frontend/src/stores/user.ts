import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getUserInfo, login as apiLogin, logout as apiLogout } from '@/services/authService';
import { useMenuStore } from './menu';

export interface UserRole {
  id: number | null;
  role_name: string;
  role_code: string;
}

export interface UserInfo {
  id: number;
  user_name: string;
  email: string;
  phone_number: string;
  creation_date: string;
  last_update_date: string;
  roles: UserRole[];
  avatar?: string;
}

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const isLoggedIn = computed(() => !!userInfo.value);

  async function fetchUserInfo() {
    try {
      loading.value = true;
      error.value = null;
      const response = await getUserInfo();
      if (response.code === 200) {
        userInfo.value = response.data;
      } else {
        error.value = response.message || '获取用户信息失败';
      }
    } catch (err) {
      error.value = '获取用户信息失败';
      console.error('获取用户信息出错:', err);
    } finally {
      loading.value = false;
    }
  }

  async function login(username: string, password: string) {
    try {
      loading.value = true;
      error.value = null;
      const response = await apiLogin(username, password);
      if (response.code === 200) {
        await fetchUserInfo();
        
        // 登录成功后获取菜单数据并初始化路由
        const menuStore = useMenuStore();
        await menuStore.fetchMenus();
        await menuStore.fetchMenuTree();
        menuStore.addRoutes();
        
        return true;
      } else {
        error.value = response.message || '登录失败';
        return false;
      }
    } catch (err: unknown) {
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const errorObj = err as { response?: { data?: { message?: string } } };
        error.value = errorObj.response?.data?.message || '登录失败';
      } else if (err instanceof Error) {
        error.value = err.message || '登录失败';
      } else {
        error.value = '登录失败';
      }
      console.error('登录出错:', err);
      return false;
    } finally {
      loading.value = false;
    }
  }

  function logout() {
    userInfo.value = null;
    // 清除菜单数据
    const menuStore = useMenuStore();
    menuStore.resetState();
    apiLogout();
  }

  function clearError() {
    error.value = null;
  }

  return {
    userInfo,
    loading,
    error,
    isLoggedIn,
    login,
    logout,
    fetchUserInfo,
    clearError
  };
}); 