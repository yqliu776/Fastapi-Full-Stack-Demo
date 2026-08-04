import { createRouter, createWebHistory } from 'vue-router'
import { useMenuStore } from '@/stores/menu'
import { getToken } from '@/services/authService'
import {
  ADMIN_HOME_PATH,
  ADMIN_LOGIN_PATH,
  ADMIN_REGISTER_PATH,
  ADMIN_ROUTE_PREFIX,
  ADMIN_SYSTEM_PATH
} from '@/config/adminRoute'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'frontHome',
      component: () => import('@/views/FrontHome.vue'),
      meta: { requiresAuth: false, title: '前台首页' }
    },
    {
      path: ADMIN_ROUTE_PREFIX,
      redirect: ADMIN_HOME_PATH
    },
    {
      path: ADMIN_LOGIN_PATH,
      name: 'login',
      component: () => import('@/views/LoginPage.vue'),
      meta: { requiresAuth: false, title: '登录' }
    },
    {
      path: ADMIN_REGISTER_PATH,
      name: 'register',
      component: () => import('@/views/RegisterPage.vue'),
      meta: { requiresAuth: false, title: '注册' }
    },
    {
      path: ADMIN_HOME_PATH,
      name: 'dashboard',
      component: () => import('@/views/DashboardLayout.vue'),
      meta: { requiresAuth: true, title: '首页' },
      children: [
        {
          path: '',
          name: 'dashboardHome',
          component: () => import('@/views/DashboardHome.vue'),
          meta: { title: '控制台' }
        }
        // 其他子路由将通过动态路由添加
      ]
    },
    {
      path: ADMIN_SYSTEM_PATH,
      redirect: ADMIN_HOME_PATH,
      name: 'system',
      component: () => import('@/views/DashboardLayout.vue'),
      meta: { requiresAuth: true, title: '系统管理' },
      children: [
        // 系统管理子路由将通过动态路由添加
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 路由加载标记，防止重复加载
let dynamicRoutesAdded = false;

export function resetDynamicRoutesFlag() {
  dynamicRoutesAdded = false;
}

// 导航守卫
router.beforeEach(async (to, from, next) => {
  const isAdminRoute = to.path === ADMIN_ROUTE_PREFIX || to.path.startsWith(`${ADMIN_ROUTE_PREFIX}/`);
  const isPublicAdminRoute = to.path === ADMIN_LOGIN_PATH || to.path === ADMIN_REGISTER_PATH;
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true) || (isAdminRoute && !isPublicAdminRoute);
  const isAuthenticated = !!getToken();
  
  if (requiresAuth && !isAuthenticated) {
    next({ path: ADMIN_LOGIN_PATH, query: { redirect: to.fullPath } });
  } else if (to.path === ADMIN_LOGIN_PATH && isAuthenticated) {
    next(ADMIN_HOME_PATH);
  } else if (isAuthenticated && requiresAuth && !dynamicRoutesAdded) {
    // 如果已登录但尚未加载动态路由，则加载动态路由
    try {
      
      const menuStore = useMenuStore();
      
      // 加载菜单数据并生成动态路由
      await menuStore.fetchMenus();
      await menuStore.fetchMenuTree();
      menuStore.addRoutes();
      
      // 设置本地标记已经加载过动态路由
      dynamicRoutesAdded = true;
      
      // 重新触发当前导航，此时应该能够正确匹配到路由了
      next({ ...to, replace: true });
    } catch (error) {
      console.error('加载动态路由失败:', error);
      next(ADMIN_HOME_PATH); // 出错时转到首页
    }
  } else {
    next();
  }
});

export default router
