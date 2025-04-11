<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { RouterView } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { logout } from '@/services/authService';

const userStore = useUserStore();
const userDropdownOpen = ref(false);
const isLoggingOut = ref(false);

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
    logout();
    console.log('登出服务调用完成');
  } catch (error) {
    console.error('退出登录失败:', error);
    alert('退出登录失败，请重试');
  } finally {
    isLoggingOut.value = false;
  }
};

const navItems = [
  { name: '仪表盘', path: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: '个人信息', path: '/dashboard/profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
  { name: '设置', path: '/dashboard/settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' },
  { name: '退出系统', path: '#', icon: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1', action: handleLogout }
];

onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo();
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
                <RouterLink 
                  v-if="!item.action"
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
                <button
                  v-else
                  @click="item.action"
                  :disabled="isLoggingOut"
                  class="group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full text-gray-300 hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div class="group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full">
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
                    <span v-if="isLoggingOut && item.name === '退出系统'" class="ml-2">(退出中...)</span>
                  </div>
                </button>
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
            <!-- 测试按钮 -->
            <button 
              class="bg-indigo-600 px-4 py-2 text-white rounded"
              @click="() => console.log('Test button clicked')"
            >
              测试按钮
            </button>
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
                    v-for="item in navItems.filter(item => ['个人信息', '设置'].includes(item.name))"
                    :key="item.name"
                    :to="item.path"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                    @click="closeUserDropdown"
                  >
                    {{ item.name }}
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