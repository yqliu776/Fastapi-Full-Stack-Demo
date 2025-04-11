<script setup lang="ts">
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900">仪表盘</h1>
    
    <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <!-- 欢迎卡片 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            欢迎回来，{{ userStore.userInfo?.user_name || '用户' }}
          </h3>
          <div class="mt-2 max-w-xl text-sm text-gray-500">
            <p>登录时间: {{ new Date().toLocaleString() }}</p>
          </div>
        </div>
      </div>
      
      <!-- 用户信息卡片 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">用户角色</h3>
          <div class="mt-2 max-w-xl text-sm text-gray-500">
            <p v-if="userStore.userInfo?.roles && userStore.userInfo.roles.length">
              <span v-for="(role, index) in userStore.userInfo.roles" :key="index">
                {{ role.role_name }}
                <span v-if="index < userStore.userInfo.roles.length - 1">、</span>
              </span>
            </p>
            <p v-else>暂无角色信息</p>
          </div>
        </div>
      </div>
      
      <!-- 快速导航卡片 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">快速导航</h3>
          <div class="mt-2 max-w-xl text-sm text-gray-500">
            <ul class="divide-y divide-gray-200">
              <li class="py-2">
                <router-link to="/dashboard/profile" class="text-indigo-600 hover:text-indigo-900">个人信息</router-link>
              </li>
              <li class="py-2">
                <router-link to="/dashboard/settings" class="text-indigo-600 hover:text-indigo-900">系统设置</router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 系统通知示例 -->
    <div class="mt-8 bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          系统通知
        </h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>这是一个示例仪表盘页面，您可以根据实际需求自定义内容。</p>
        </div>
        <div class="mt-5">
          <button type="button" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            了解更多
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 仪表盘首页样式 */
</style> 