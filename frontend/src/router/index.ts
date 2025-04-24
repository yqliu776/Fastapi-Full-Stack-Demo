import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/services/authService'
import { useMenuStore } from '@/stores/menu'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginPage.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterPage.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboardHome',
          component: () => import('@/views/DashboardHome.vue')
        }
        // 其他子路由将通过动态路由添加
      ]
    },
    {
      path: '/system',
      redirect: '/dashboard',
      name: 'system',
      component: () => import('@/views/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        // 系统管理子路由将通过动态路由添加
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard'
    }
  ],
})

// 路由加载标记，防止重复加载
let dynamicRoutesAdded = false;

// 导航守卫
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false);
  const isAuthenticated = !!getToken();
  
  if (requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/dashboard');
  } else if (isAuthenticated && requiresAuth && !dynamicRoutesAdded) {
    // 如果已登录但尚未加载动态路由，则加载动态路由
    try {
      console.log('开始加载动态路由...');
      const menuStore = useMenuStore();
      
      // 加载菜单数据并生成动态路由
      await menuStore.fetchMenus();
      await menuStore.fetchMenuTree();
      menuStore.addRoutes();
      
      // 设置本地标记已经加载过动态路由
      dynamicRoutesAdded = true;
      console.log('动态路由加载完成，当前访问路径:', to.path);
      
      // 重新触发当前导航，此时应该能够正确匹配到路由了
      next({ ...to, replace: true });
    } catch (error) {
      console.error('加载动态路由失败:', error);
      next('/dashboard'); // 出错时转到首页
    }
  } else {
    next();
  }
});

export default router
