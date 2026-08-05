import { createRouter, createWebHistory } from 'vue-router'
import { useMenuStore } from '@/stores/menu'
import { getToken } from '@/services/authService'
import {
  ADMIN_HOME_PATH,
  ADMIN_LOGIN_PATH,
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
      path: '/register',
      name: 'frontRegister',
      component: () => import('@/views/RegisterPage.vue'),
      meta: { requiresAuth: false, title: '注册' }
    },
    {
      path: '/login',
      name: 'frontLogin',
      component: () => import('@/views/FrontLoginPage.vue'),
      meta: { requiresAuth: false, title: '前台登录' }
    },
    {
      path: '/user',
      name: 'frontUser',
      component: () => import('@/views/FrontUserPage.vue'),
      meta: { requiresFrontAuth: true, title: '用户中心' }
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
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfilePage.vue'),
          meta: { title: '个人信息' }
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
      name: 'notFound',
      component: () => import('@/views/UnsupportedMenuPage.vue'),
      meta: { requiresAuth: false, title: '页面不存在' }
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
  const isPublicAdminRoute = to.path === ADMIN_LOGIN_PATH;
  const requiresAdminAuth = to.matched.some(record => record.meta.requiresAuth === true) || (isAdminRoute && !isPublicAdminRoute);
  const requiresFrontAuth = to.matched.some(record => record.meta.requiresFrontAuth === true);
  const isFrontGuestRoute = to.path === '/login' || to.path === '/register';
  const isAuthenticated = !!getToken();
  
  if (requiresFrontAuth && !isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } });
  } else if (isFrontGuestRoute && isAuthenticated) {
    next('/user');
  } else if (requiresAdminAuth && !isAuthenticated) {
    next({ path: ADMIN_LOGIN_PATH, query: { redirect: to.fullPath } });
  } else if (to.path === ADMIN_LOGIN_PATH && isAuthenticated) {
    next(ADMIN_HOME_PATH);
  } else if (isAuthenticated && requiresAdminAuth && !dynamicRoutesAdded) {
    // 如果已登录但尚未加载动态路由，则加载动态路由
    try {
      
      const menuStore = useMenuStore();
      
      // 加载菜单数据并生成动态路由
      await menuStore.fetchMenus();
      await menuStore.fetchMenuTree();
      menuStore.addRoutes();
      
      // 设置本地标记已经加载过动态路由
      dynamicRoutesAdded = true;
      
      // 重新触发当前导航（按 path 解析，避免 catch-all 的 name 干扰），
      // 此时动态路由已就绪，应该能够正确匹配到目标页面
      next({ path: to.path, query: to.query, hash: to.hash, replace: true });
    } catch (error) {
      console.error('加载动态路由失败:', error);
      next(ADMIN_HOME_PATH); // 出错时转到首页
    }
  } else {
    // 未匹配任何路由：动态路由已加载仍找不到时回到首页
    if (to.name === 'notFound') {
      next('/');
    } else {
      next();
    }
  }
});

export default router
