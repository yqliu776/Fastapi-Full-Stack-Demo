import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { menuService } from '@/services/menuService';
import type { Menu } from '@/services/menuService';
import type { RouteRecordRaw } from 'vue-router';
import router from '@/router';

// 组件映射表，将后端返回的menu_path映射到对应的组件
const componentMap: Record<string, () => Promise<any>> = {
  '/dashboard': () => import('@/views/DashboardHome.vue'),
  '/dashboard/profile': () => import('@/views/ProfilePage.vue'),
  '/dashboard/settings': () => import('@/views/HomePage.vue'),
  '/dashboard/roles': () => import('@/views/RoleManagePage.vue'),
  '/dashboard/permissions': () => import('@/views/PermissionManagePage.vue'),
  '/dashboard/menus': () => import('@/views/MenuManagePage.vue'),
  '/dashboard/users': () => import('@/views/UserManagePage.vue'),
  // 添加系统管理相关路径映射
  '/system': () => import('@/views/DashboardHome.vue'),
  '/system/user': () => import('@/views/UserManagePage.vue'),
  '/system/role': () => import('@/views/RoleManagePage.vue'),
  '/system/permission': () => import('@/views/PermissionManagePage.vue'),
  '/system/menu': () => import('@/views/MenuManagePage.vue'),
  // 添加以下默认映射，确保即使找不到确切的映射也能返回一个合理的组件
  'default': () => import('@/views/DashboardHome.vue')
};

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
    component: componentMap[menu.menu_path] || componentMap['default']
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
      const response = await menuService.getMenus();
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
      const response = await menuService.getMenuTree();
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
      if (menu.menu_path && (menu.menu_path.startsWith('/dashboard') || menu.menu_path.startsWith('/system'))) {
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
        console.log(`添加路由: ${route.path}`);
        
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