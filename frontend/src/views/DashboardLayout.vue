<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { RouterView, useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useMenuStore } from '@/stores/menu';
import { logout } from '@/services/authService';

const userStore = useUserStore();
const menuStore = useMenuStore();
const router = useRouter();
const userDropdownOpen = ref(false);
const isLoggingOut = ref(false);

// 父菜单展开状态
const expandedMenus = ref<Set<number>>(new Set());

// 切换菜单展开状态
const toggleMenuExpand = (menuId: number) => {
  if (expandedMenus.value.has(menuId)) {
    expandedMenus.value.delete(menuId);
  } else {
    expandedMenus.value.add(menuId);
  }
};

// 判断当前路由是否活跃
const isRouteActive = (path: string) => {
  const route = useRoute();
  return route.path === path;
};

// 创建一个ref来存储事件处理函数
const documentClickHandler = ref((event: Event) => {
  // 如果点击的是菜单内部元素，不关闭菜单
  const menu = document.querySelector('[role="menu"]');
  const button = document.getElementById('user-menu-button');
  if (menu?.contains(event.target as Node) || button?.contains(event.target as Node)) {
    return;
  }
  closeUserDropdown();
});

const toggleUserDropdown = (event: Event) => {
  console.log('toggleUserDropdown called', event);
  event.stopPropagation();
  userDropdownOpen.value = !userDropdownOpen.value;
  console.log('userDropdownOpen toggled to:', userDropdownOpen.value);
};

const closeUserDropdown = () => {
  userDropdownOpen.value = false;
};

const handleLogout = async () => {
  if (!window.confirm('确定要退出系统吗？')) {
    return;
  }

  console.log('开始退出登录');
  isLoggingOut.value = true;
  try {
    console.log('正在清除用户状态...');
    await userStore.logout();
    console.log('用户状态已清除，准备调用登出服务...');
    closeUserDropdown();
    menuStore.resetState(); // 重置菜单状态
    logout();
    console.log('登出服务调用完成');
  } catch (error) {
    console.error('退出登录失败:', error);
    alert('退出登录失败，请重试');
  } finally {
    isLoggingOut.value = false;
  }
};

// 固定菜单项
const fixedMenuItems = [
  { name: '退出系统', path: '#', icon: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1', action: handleLogout }
];

// 创建菜单项接口
interface MenuItem {
  id: number;
  name: string;
  path: string;
  icon: string;
  action?: () => Promise<void>;
  children?: Array<{
    id: number;
    menu_name: string;
    menu_path: string;
    menu_code: string;
    children?: any[];
  }>;
}

// 计算属性：动态菜单与固定菜单合并
const navItems = computed<MenuItem[]>(() => {
  const dynamicMenus = menuStore.menuTree.filter(menu => !menu.parent_id).map(menu => ({
    id: menu.id,
    name: menu.menu_name,
    path: menu.menu_path,
    icon: getIconByMenuCode(menu.menu_code),
    children: menu.children || []
  }));
  
  // 确保固定菜单项也有id
  const fixedMenusWithId = fixedMenuItems.map((item, index) => ({
    ...item,
    id: -1 - index // 使用负数作为固定菜单的ID，避免与动态菜单冲突
  }));
  
  return [...dynamicMenus, ...fixedMenusWithId];
});

// 根据菜单代码获取对应图标
function getIconByMenuCode(menuCode: string): string {
  const iconMap: Record<string, string> = {
    'dashboard': 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    'user': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    'role': 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    'permission': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    'menu': 'M4 6h16M4 12h16m-7 6h7',
    'profile': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    'setting': 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
  };
  
  // 从menuCode中提取相关部分作为图标查询键
  const key = menuCode.toLowerCase().split('_')[0];
  return iconMap[key] || iconMap['setting']; // 默认返回设置图标
}

// 加载用户信息和菜单数据
onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo();
  }
  
  // 加载菜单数据并生成路由
  if (!menuStore.hasMenus) {
    await menuStore.fetchMenuTree();
    await menuStore.fetchMenus();
    menuStore.addRoutes();
    
    // 自动展开包含当前路由的父菜单
    const route = useRoute();
    menuStore.menuTree.forEach(menu => {
      if (menu.id && menu.children?.some(child => child.menu_path === route.path)) {
        expandedMenus.value.add(menu.id);
      }
    });
  }
  
  // 添加全局点击事件监听器来关闭菜单
  document.addEventListener('click', documentClickHandler.value);
});

onUnmounted(() => {
  // 移除事件监听器
  document.removeEventListener('click', documentClickHandler.value);
});
</script>

<template>
  <div class="h-screen flex overflow-hidden bg-gray-100">
    <!-- 侧边栏 -->
    <div class="hidden md:flex md:flex-shrink-0">
      <div class="flex flex-col w-64">
        <div class="flex flex-col h-0 flex-1 bg-gray-800">
          <div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div class="flex items-center flex-shrink-0 px-4">
              <h1 class="text-white text-xl font-semibold">管理系统</h1>
            </div>
            <nav class="mt-5 flex-1 px-2 bg-gray-800 space-y-1">
              <template v-for="item in navItems" :key="item.name">
                <!-- 有动作的菜单项 -->
                <div 
                  v-if="item.action" 
                  @click="item.action"
                  class="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700 hover:text-white cursor-pointer"
                >
                  <svg
                    class="text-gray-400 group-hover:text-gray-300 mr-3 flex-shrink-0 h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      :d="item.icon"
                    />
                  </svg>
                  {{ item.name }}
                </div>
                
                <!-- 无子菜单的常规菜单项 -->
                <RouterLink
                  v-else-if="!item.children || item.children.length === 0"
                  :to="item.path"
                  class="group flex items-center px-2 py-2 text-sm font-medium rounded-md"
                  v-slot="{ isActive }"
                >
                  <div :class="[
                    isActive ? 'text-white bg-gray-900' : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full'
                  ]">
                    <svg
                      :class="[
                        isActive ? 'text-gray-300' : 'text-gray-400 group-hover:text-gray-300',
                        'mr-3 flex-shrink-0 h-6 w-6'
                      ]"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        :d="item.icon"
                      />
                    </svg>
                    {{ item.name }}
                  </div>
                </RouterLink>
                
                <!-- 有子菜单的菜单项 -->
                <div v-else class="space-y-1">
                  <!-- 父菜单项 -->
                  <div 
                    @click="item.id && toggleMenuExpand(item.id)"
                    class="text-gray-300 group flex items-center px-2 py-2 text-sm font-medium rounded-md hover:bg-gray-700 hover:text-white cursor-pointer"
                  >
                    <svg
                      class="text-gray-400 group-hover:text-gray-300 mr-3 flex-shrink-0 h-6 w-6"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        :d="item.icon"
                      />
                    </svg>
                    <span class="flex-1">{{ item.name }}</span>
                    <!-- 展开/折叠图标 -->
                    <svg 
                      class="h-5 w-5 text-gray-400"
                      :class="{ 'transform rotate-90': item.id && expandedMenus.has(item.id) }"
                      xmlns="http://www.w3.org/2000/svg" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  
                  <!-- 子菜单项，只在父菜单展开时显示 -->
                  <div v-if="item.id && expandedMenus.has(item.id)" class="mt-1">
                    <RouterLink
                      v-for="child in item.children"
                      :key="child.id"
                      :to="child.menu_path"
                      class="group flex items-center pl-10 pr-2 py-2 text-sm font-medium rounded-md"
                      v-slot="{ isActive }"
                    >
                      <div :class="[
                        isActive ? 'text-white bg-gray-900' : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                        'group flex items-center w-full text-sm font-medium rounded-md'
                      ]">
                        {{ child.menu_name }}
                      </div>
                    </RouterLink>
                  </div>
                </div>
              </template>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="flex flex-col w-0 flex-1 overflow-hidden">
      <!-- 顶部导航栏 -->
      <div class="relative z-10 flex-shrink-0 flex h-16 bg-white shadow">
        <button class="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 md:hidden">
          <span class="sr-only">打开侧边栏</span>
          <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div class="flex-1 px-4 flex justify-between">
          <div class="flex-1 flex">
          </div>
          <div class="ml-4 flex items-center md:ml-6">
            <!-- 用户下拉菜单 -->
            <div class="ml-3 relative">
              <div>
                <button
                  type="button"
                  class="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  id="user-menu-button"
                  @click="toggleUserDropdown"
                  aria-expanded="false"
                  aria-haspopup="true"
                >
                  <span class="sr-only">用户菜单</span>
                  <div class="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                    {{ userStore.userInfo?.user_name.charAt(0).toUpperCase() || '?' }}
                  </div>
                  <span class="ml-3 text-gray-700">{{ userStore.userInfo?.user_name || '加载中...' }}</span>
                </button>
              </div>

              <div
                v-if="userDropdownOpen"
                class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
                role="menu"
                aria-orientation="vertical"
                aria-labelledby="user-menu-button"
                @click.stop
              >
                <div class="px-4 py-2 text-sm text-gray-500 border-b border-gray-200">
                  当前用户：{{ userStore.userInfo?.user_name }}
                </div>
                <div class="py-1">
                  <RouterLink
                    to="/dashboard/profile"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                    @click="closeUserDropdown"
                  >
                    个人信息
                  </RouterLink>
                  <RouterLink
                    to="/dashboard/settings"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                    @click="closeUserDropdown"
                  >
                    设置
                  </RouterLink>
                  <button
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    role="menuitem"
                    :disabled="isLoggingOut"
                    @click="handleLogout"
                  >
                    退出系统
                    <span v-if="isLoggingOut" class="ml-2 text-gray-500">(退出中...)</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 页面内容 -->
      <main class="flex-1 relative overflow-y-auto focus:outline-none">
        <div class="py-6">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
            <RouterView />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* 仪表盘样式 */
</style>
