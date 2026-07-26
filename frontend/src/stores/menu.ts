import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { menuService } from '@/services/menuService';
import type { Menu } from '@/services/menuService';
import type { RouteRecordRaw } from 'vue-router';
import router from '@/router';

const componentRegistry: Record<string, () => Promise<any>> = {
  dashboard: () => import('@/views/DashboardHome.vue'),
  profile: () => import('@/views/ProfilePage.vue'),
  user: () => import('@/views/UserManagePage.vue'),
  role: () => import('@/views/RoleManagePage.vue'),
  permission: () => import('@/views/PermissionManagePage.vue'),
  menu: () => import('@/views/MenuManagePage.vue'),
  rate_limit: () => import('@/views/RateLimitManagePage.vue'),
  swagger: () => import('@/views/SwaggerUIPage.vue'),
  unsupported: () => import('@/views/UnsupportedMenuPage.vue')
};

const componentAliases: Record<string, string> = {
  dashboard: 'dashboard',
  home: 'dashboard',
  system: 'dashboard',
  profile: 'profile',
  user: 'user',
  user_manage: 'user',
  role: 'role',
  role_manage: 'role',
  permission: 'permission',
  permission_manage: 'permission',
  menu: 'menu',
  menu_manage: 'menu',
  api_rate_limit: 'rate_limit',
  rate_limit: 'rate_limit',
  swagger: 'swagger',
  api_docs: 'swagger',
  swagger_ui: 'swagger'
};

const pathComponentAliases: Record<string, string> = {
  '/dashboard': 'dashboard',
  '/dashboard/profile': 'profile',
  '/dashboard/roles': 'role',
  '/dashboard/permissions': 'permission',
  '/dashboard/menus': 'menu',
  '/dashboard/users': 'user',
  '/dashboard/rate-limit': 'rate_limit',
  '/system': 'dashboard',
  '/system/user': 'user',
  '/system/role': 'role',
  '/system/permission': 'permission',
  '/system/menu': 'menu',
  '/system/api-rate-limit': 'rate_limit',
  '/system/swagger-ui': 'swagger'
};

const normalizeKey = (key: string) => key.trim().toLowerCase().replace(/-/g, '_');

const resolveComponent = (menu: Menu) => {
  const explicitKey = menu.component_key ? normalizeKey(menu.component_key) : '';
  const codeKey = normalizeKey(menu.menu_code || '');
  const pathKey = pathComponentAliases[menu.menu_path || ''];
  const registryKey = componentAliases[explicitKey] || componentAliases[codeKey] || pathKey;

  return componentRegistry[registryKey] || componentRegistry.unsupported;
};

const isShellRoutePath = (path: string) => path === '/dashboard' || path === '/system';

// 将菜单项转换为路由配置
const menuToRoute = (menu: Menu): RouteRecordRaw => {
  // 确保路径格式正确
  let path = '';
  
  if (menu.menu_path.startsWith('/')) {
    if (menu.menu_path.startsWith('/dashboard/')) {
      path = menu.menu_path.substring('/dashboard/'.length);
    } else if (menu.menu_path.startsWith('/system/')) {
      path = menu.menu_path.substring('/system/'.length);
    } else {
      path = menu.menu_path.substring(1);
    }
  } else {
    path = menu.menu_path;
  }
    
  const route: RouteRecordRaw = {
    path: path,
    name: menu.menu_code,
    meta: { 
      title: menu.menu_name,
      requiresAuth: true 
    },
    component: resolveComponent(menu)
  };

  return route;
};

export const useMenuStore = defineStore('menu', () => {
  const menuList = ref<Menu[]>([]);
  const menuTree = ref<Menu[]>([]);
  const routes = ref<RouteRecordRaw[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const routesAdded = ref(false);

  const hasMenus = computed(() => menuList.value.length > 0);

  // 获取菜单列表
  async function fetchMenus() {
    try {
      loading.value = true;
      error.value = null;
      const response = await menuService.getCurrentMenus();
      if (response.code === 200) {
        menuList.value = response.data.items;
        return true;
      } else {
        error.value = response.message || '获取菜单失败';
        return false;
      }
    } catch (err) {
      error.value = '获取菜单失败';
      console.error('获取菜单出错:', err);
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 获取菜单树
  async function fetchMenuTree() {
    try {
      loading.value = true;
      error.value = null;
      const response = await menuService.getCurrentMenuTree();
      if (response.code === 200) {
        menuTree.value = response.data;
        return true;
      } else {
        error.value = response.message || '获取菜单树失败';
        return false;
      }
    } catch (err) {
      error.value = '获取菜单树失败';
      console.error('获取菜单树出错:', err);
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 生成路由配置
  function generateRoutes() {
    const menuRoutes: RouteRecordRaw[] = [];
    
    // 处理所有有效的菜单项作为路由
    menuList.value.forEach(menu => {
      if (
        menu.menu_path &&
        !isShellRoutePath(menu.menu_path) &&
        (menu.menu_path.startsWith('/dashboard') || menu.menu_path.startsWith('/system'))
      ) {
        const route = menuToRoute(menu);
        menuRoutes.push(route);
      }
    });
    
    routes.value = menuRoutes;
    return menuRoutes;
  }

  // 动态添加路由
  function addRoutes() {
    if (routesAdded.value) return;
    
    const menuRoutes = generateRoutes();
    
    // 为路由添加到router
    menuRoutes.forEach(route => {
      if (!router.hasRoute(route.name as string)) {
        // 根据原始菜单路径前缀决定添加到哪个父路由下
        const menu = menuList.value.find(m => m.menu_code === route.name);
        if (menu) {
          if (menu.menu_path.startsWith('/dashboard/')) {
            router.addRoute('dashboard', route);
          } else if (menu.menu_path.startsWith('/system/')) {
            router.addRoute('system', route);
          } else {
            router.addRoute('dashboard', route);
          }
        } else {
          router.addRoute('dashboard', route);
        }
      }
    });
    
    routesAdded.value = true;
  }

  // 重置菜单和路由状态
  function resetState() {
    menuList.value = [];
    menuTree.value = [];
    routes.value = [];
    routesAdded.value = false;
  }

  return {
    menuList,
    menuTree,
    routes,
    loading,
    error,
    hasMenus,
    routesAdded,
    fetchMenus,
    fetchMenuTree,
    generateRoutes,
    addRoutes,
    resetState
  };
}); 
